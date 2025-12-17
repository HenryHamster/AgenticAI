"""
Benchmark Evaluator - Evaluates completed benchmark games and generates aggregate metrics

Usage:
    python eval_benchmark.py --input benchmarks/benchmark_20250115_143022.json
    python eval_benchmark.py --input benchmarks/benchmark_20250115_143022.json --output results/eval_001.json
"""

import os
import sys
import argparse
import json
import statistics
from datetime import datetime
from typing import Any
from collections import defaultdict

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.database.gameService import load_game_from_database
from services.database.turnService import get_turns_by_game_id
from services.evaluationService import evaluate_game_responses
from schema.enums import GameStatus

# All evaluation metrics we track
EVAL_METRICS = ["score", "appropriateness", "completeness", "clarity", "creativity", "action_validity"]

# Patterns that indicate a corrupted/rate-limited response
RATE_LIMIT_PATTERNS = [
    "rate limit",
    "rate_limit",
    "429",
    "too many requests",
    "quota exceeded",
    "resource exhausted",
    "try again later",
    "request limit",
    "throttl",
]

ERROR_PATTERNS = [
    "error:",
    "exception:",
    "failed to",
    "could not",
    "unable to",
    "api error",
    "timeout",
    "connection refused",
]


def is_corrupted_response(response: str | None) -> tuple[bool, str]:
    """
    Check if a response appears to be corrupted (rate limited, error, etc.)

    Returns:
        Tuple of (is_corrupted, reason)
    """
    if response is None:
        return True, "null_response"

    if not isinstance(response, str):
        return True, "non_string_response"

    response_lower = response.lower().strip()

    # Empty or very short responses are suspicious
    if len(response_lower) < 5:
        return True, "empty_response"

    # Check for rate limit indicators
    for pattern in RATE_LIMIT_PATTERNS:
        if pattern in response_lower:
            return True, f"rate_limit:{pattern}"

    # Check for error indicators
    for pattern in ERROR_PATTERNS:
        if pattern in response_lower:
            return True, f"error:{pattern}"

    return False, ""


def check_game_corruption(game_id: str) -> dict[str, Any]:
    """
    Check a game for signs of corruption (rate limits, errors).

    Returns:
        Dict with corruption status and details
    """
    from services.database.turnService import get_turns_by_game_id

    try:
        turns = get_turns_by_game_id(game_id)
    except Exception as e:
        return {"is_corrupted": True, "reason": f"failed_to_load: {e}", "corrupted_turns": [], "total_turns": 0}

    corrupted_turns = []
    corrupted_responses = 0
    total_responses = 0

    for turn in turns:
        turn_issues = []
        for player_uid, response in turn.game_state.player_responses.items():
            total_responses += 1
            is_bad, reason = is_corrupted_response(response)
            if is_bad:
                corrupted_responses += 1
                turn_issues.append({"player": player_uid, "reason": reason, "response_preview": str(response)[:100] if response else None})

        if turn_issues:
            corrupted_turns.append({"turn": turn.turn_number, "issues": turn_issues})

    # Game is corrupted if more than 20% of responses are bad
    corruption_ratio = corrupted_responses / total_responses if total_responses > 0 else 0
    is_corrupted = corruption_ratio > 0.2 or len(corrupted_turns) > len(turns) * 0.3

    return {
        "is_corrupted": is_corrupted,
        "corruption_ratio": round(corruption_ratio, 3),
        "corrupted_responses": corrupted_responses,
        "total_responses": total_responses,
        "corrupted_turns": corrupted_turns,
        "total_turns": len(turns)
    }


def load_benchmark_file(input_path: str) -> dict:
    """Load benchmark results from JSON file."""
    with open(input_path, 'r') as f:
        return json.load(f)


def load_multiple_benchmarks(input_paths: list[str]) -> tuple[list[dict], list[str]]:
    """
    Load multiple benchmark files and combine their games.

    Args:
        input_paths: List of paths to benchmark JSON files (can include globs)

    Returns:
        Tuple of (combined_games, benchmark_ids)
    """
    import glob

    all_games = []
    benchmark_ids = []
    resolved_paths = []

    # Resolve glob patterns
    for path in input_paths:
        matches = glob.glob(path)
        if matches:
            resolved_paths.extend(matches)
        else:
            resolved_paths.append(path)  # Keep as-is if no glob match

    for path in resolved_paths:
        try:
            data = load_benchmark_file(path)
            benchmark_id = data.get("benchmark_id", os.path.basename(path))
            benchmark_ids.append(benchmark_id)
            games = data.get("games", [])
            # Tag each game with its source benchmark
            for game in games:
                game["_source_benchmark"] = benchmark_id
            all_games.extend(games)
            print(f"  Loaded {len(games)} games from {benchmark_id}")
        except Exception as e:
            print(f"  [WARNING] Failed to load {path}: {e}")

    return all_games, benchmark_ids


def get_game_details(game_id: str) -> dict[str, Any] | None:
    """
    Get details about a completed game from the database.

    Args:
        game_id: The game ID to look up

    Returns:
        Dictionary with game details or None if not found
    """
    try:
        game = load_game_from_database(game_id)
        turns = get_turns_by_game_id(game_id)

        # Get player names/uids from player_configs or turns
        player_uids = []
        if game.player_configs:
            player_uids = [f"player{i}" for i in range(len(game.player_configs))]
        elif turns:
            # Extract from first turn's game state
            first_turn = turns[0]
            if hasattr(first_turn, 'game_state') and first_turn.game_state:
                player_uids = list(first_turn.game_state.players.keys())

        return {
            "game_id": game_id,
            "status": game.status.value if hasattr(game.status, 'value') else str(game.status),
            "winner": game.winner_player_name,
            "turns_played": len(turns),
            "num_players": game.total_players,
            "player_uids": player_uids,
            "model": game.model,
            "game_over_reason": None  # Will be extracted from last turn if available
        }
    except Exception as e:
        print(f"  [WARNING] Could not load game {game_id}: {e}")
        return None


def evaluate_single_game(game_id: str, service_type: str = "mock", ai_model: str = "gpt-4.1-nano") -> dict[str, Any] | None:
    """
    Evaluate a single game and return evaluation results.

    Args:
        game_id: The game ID to evaluate
        service_type: Evaluation service type ("mock" or "custom")
        ai_model: AI model to use for evaluation

    Returns:
        Evaluation results dictionary or None if failed
    """
    try:
        return evaluate_game_responses(game_id, service_type=service_type, ai_model=ai_model)
    except Exception as e:
        print(f"  [WARNING] Could not evaluate game {game_id}: {e}")
        return None


def extract_player_metrics(eval_result: dict) -> dict[str, dict[str, list[float]]]:
    """
    Extract per-player metrics from evaluation result.

    Returns dict: {player_uid: {metric_name: [scores_per_turn]}}
    """
    player_metrics = defaultdict(lambda: defaultdict(list))

    if not eval_result or "evaluations" not in eval_result:
        return player_metrics

    for turn_eval in eval_result["evaluations"]:
        player_evals = turn_eval.get("player_evaluations", {})
        for player_uid, eval_data in player_evals.items():
            evaluation = eval_data.get("evaluation", {})
            for metric in EVAL_METRICS:
                if metric in evaluation:
                    player_metrics[player_uid][metric].append(evaluation[metric])

    return player_metrics


def calculate_metric_stats(values: list[float]) -> dict[str, float]:
    """Calculate statistics for a list of metric values."""
    if not values:
        return {"mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0, "median": 0.0}

    return {
        "mean": round(statistics.mean(values), 3),
        "std": round(statistics.stdev(values), 3) if len(values) > 1 else 0.0,
        "min": round(min(values), 3),
        "max": round(max(values), 3),
        "median": round(statistics.median(values), 3)
    }


def calculate_aggregate_metrics(per_game_results: list[dict], all_player_metrics: dict) -> dict[str, Any]:
    """
    Calculate aggregate metrics across all evaluated games.

    Args:
        per_game_results: List of per-game result dictionaries
        all_player_metrics: Aggregated player metrics across all games

    Returns:
        Dictionary with aggregate metrics
    """
    if not per_game_results:
        return {
            "win_rates": {"games_with_winner": 0, "total_games": 0, "win_rate": 0.0, "per_player_wins": {}},
            "turn_statistics": {"average_turns": 0, "min_turns": 0, "max_turns": 0, "median_turns": 0},
            "player_statistics": {"average_players_per_game": 0, "total_players_evaluated": 0, "unique_players": 0, "total_responses_evaluated": 0},
            "evaluation_metrics": {m: {"mean": 0, "std": 0, "min": 0, "max": 0, "median": 0} for m in EVAL_METRICS},
            "per_player_metrics": {},
            "game_outcomes": {"completed_normally": 0, "max_turns_reached": 0, "all_players_dead": 0}
        }

    # Win rates - track per player
    total_games = len(per_game_results)
    games_with_winner = sum(1 for g in per_game_results if g.get("winner"))

    # Count wins per player
    player_wins = defaultdict(int)
    player_games = defaultdict(int)
    for g in per_game_results:
        winner = g.get("winner")
        player_uids = g.get("player_uids", [])
        for uid in player_uids:
            player_games[uid] += 1
            if winner and uid in winner:  # Check if this player won
                player_wins[uid] += 1

    per_player_win_rates = {}
    for uid in player_games:
        per_player_win_rates[uid] = {
            "wins": player_wins[uid],
            "games": player_games[uid],
            "win_rate": round(player_wins[uid] / player_games[uid], 3) if player_games[uid] > 0 else 0.0
        }

    # Turn statistics
    turn_counts = [g.get("turns_played", 0) for g in per_game_results if g.get("turns_played", 0) > 0]
    if turn_counts:
        avg_turns = statistics.mean(turn_counts)
        min_turns = min(turn_counts)
        max_turns = max(turn_counts)
        median_turns = statistics.median(turn_counts)
    else:
        avg_turns = min_turns = max_turns = median_turns = 0

    # Player statistics
    player_counts = [g.get("num_players", 0) for g in per_game_results if g.get("num_players", 0) > 0]
    avg_players = statistics.mean(player_counts) if player_counts else 0
    total_players = sum(player_counts)
    unique_players = len(all_player_metrics)

    # Aggregate evaluation metrics across all players
    all_metric_values = defaultdict(list)
    for player_uid, metrics in all_player_metrics.items():
        for metric_name, values in metrics.items():
            all_metric_values[metric_name].extend(values)

    evaluation_metrics = {}
    for metric in EVAL_METRICS:
        evaluation_metrics[metric] = calculate_metric_stats(all_metric_values[metric])

    # Per-player aggregated metrics
    per_player_metrics = {}
    for player_uid, metrics in all_player_metrics.items():
        per_player_metrics[player_uid] = {
            "total_responses": len(metrics.get("score", [])),
            "metrics": {}
        }
        for metric in EVAL_METRICS:
            per_player_metrics[player_uid]["metrics"][metric] = calculate_metric_stats(metrics.get(metric, []))

    # Game outcomes - analyze game_over_reason
    completed_normally = 0
    max_turns_reached = 0
    all_players_dead = 0

    for g in per_game_results:
        reason = g.get("game_over_reason", "") or ""
        reason_lower = reason.lower()

        if "currency" in reason_lower or "goal" in reason_lower or "win" in reason_lower:
            completed_normally += 1
        elif "turn" in reason_lower or "max" in reason_lower:
            max_turns_reached += 1
        elif "dead" in reason_lower or "died" in reason_lower:
            all_players_dead += 1
        else:
            # Default: count as completed normally if it has a winner, else max turns
            if g.get("winner"):
                completed_normally += 1
            else:
                max_turns_reached += 1

    return {
        "win_rates": {
            "games_with_winner": games_with_winner,
            "total_games": total_games,
            "win_rate": round(games_with_winner / total_games, 3) if total_games > 0 else 0.0,
            "per_player_wins": per_player_win_rates
        },
        "turn_statistics": {
            "average_turns": round(avg_turns, 2),
            "min_turns": min_turns,
            "max_turns": max_turns,
            "median_turns": round(median_turns, 1)
        },
        "player_statistics": {
            "average_players_per_game": round(avg_players, 2),
            "total_players_evaluated": total_players,
            "unique_players": unique_players,
            "total_responses_evaluated": sum(len(m.get("score", [])) for m in all_player_metrics.values())
        },
        "evaluation_metrics": evaluation_metrics,
        "per_player_metrics": per_player_metrics,
        "game_outcomes": {
            "completed_normally": completed_normally,
            "max_turns_reached": max_turns_reached,
            "all_players_dead": all_players_dead
        }
    }


def evaluate_benchmark(
    input_paths: list[str],
    output_path: str | None = None,
    service_type: str = "mock",
    ai_model: str = "gpt-4.1-nano",
    verbose: bool = False
) -> dict:
    """
    Evaluate all completed games from one or more benchmark runs.

    Args:
        input_paths: List of paths to benchmark JSON files (supports globs like "benchmarks/*.json")
        output_path: Optional path to save evaluation results
        service_type: Evaluation service type ("mock" or "custom")
        ai_model: AI model to use for evaluation
        verbose: Enable verbose logging

    Returns:
        Evaluation results dictionary
    """
    print(f"\n{'='*60}")
    print(f"Evaluating Benchmark(s)")
    print(f"{'='*60}")
    print(f"  Input(s): {input_paths}")
    print(f"  Evaluation service: {service_type}")
    print(f"  Evaluation model: {ai_model}")
    print(f"{'='*60}\n")

    # Load benchmark data (supports multiple files)
    if len(input_paths) == 1 and not any(c in input_paths[0] for c in ['*', '?']):
        # Single file, no glob
        benchmark_data = load_benchmark_file(input_paths[0])
        benchmark_id = benchmark_data.get("benchmark_id", "unknown")
        games = benchmark_data.get("games", [])
        source_benchmarks = [benchmark_id]
    else:
        # Multiple files or glob pattern
        print("Loading multiple benchmark files...")
        games, source_benchmarks = load_multiple_benchmarks(input_paths)
        benchmark_id = f"batch_{len(source_benchmarks)}_benchmarks"
        print(f"  Combined {len(games)} games from {len(source_benchmarks)} benchmarks\n")

    print(f"Benchmark ID: {benchmark_id}")
    print(f"Total games in benchmark: {len(games)}")

    # Filter for completed games
    completed_games = [g for g in games if g.get("status") == "completed"]
    skipped_games = [g for g in games if g.get("status") != "completed"]

    print(f"Completed games to evaluate: {len(completed_games)}")
    print(f"Skipped (failed/pending): {len(skipped_games)}")

    # Evaluate each completed game
    per_game_results = []
    all_player_metrics = defaultdict(lambda: defaultdict(list))  # {player_uid: {metric: [values]}}
    evaluated_count = 0
    eval_failed_count = 0

    corrupted_games = []

    for i, game_entry in enumerate(completed_games, 1):
        game_id = game_entry.get("game_id")
        print(f"\n[{i}/{len(completed_games)}] Evaluating game {game_id}...")

        # Check for corruption (rate limits, errors)
        corruption_check = check_game_corruption(game_id)
        if corruption_check["is_corrupted"]:
            print(f"  [WARNING] Game appears corrupted: {corruption_check['corrupted_responses']}/{corruption_check['total_responses']} bad responses")
            corrupted_games.append({
                "game_id": game_id,
                "corruption_ratio": corruption_check["corruption_ratio"],
                "corrupted_turns": len(corruption_check["corrupted_turns"]),
                "total_turns": corruption_check["total_turns"]
            })
            eval_failed_count += 1
            continue

        # Get game details from database
        game_details = get_game_details(game_id)
        if not game_details:
            eval_failed_count += 1
            continue

        # Run evaluation
        eval_result = evaluate_single_game(game_id, service_type, ai_model)

        # Extract per-player metrics
        player_metrics = extract_player_metrics(eval_result)
        for player_uid, metrics in player_metrics.items():
            for metric_name, values in metrics.items():
                all_player_metrics[player_uid][metric_name].extend(values)

        # Extract average scores per metric for this game
        game_metrics = {}
        if eval_result and "evaluations" in eval_result:
            metric_values = defaultdict(list)
            for turn_eval in eval_result["evaluations"]:
                for player_uid, eval_data in turn_eval.get("player_evaluations", {}).items():
                    evaluation = eval_data.get("evaluation", {})
                    for metric in EVAL_METRICS:
                        if metric in evaluation:
                            metric_values[metric].append(evaluation[metric])

            for metric in EVAL_METRICS:
                if metric_values[metric]:
                    game_metrics[metric] = round(statistics.mean(metric_values[metric]), 3)

        # Get game over reason from last turn if available
        try:
            turns = get_turns_by_game_id(game_id)
            if turns:
                last_turn = turns[-1]
                if hasattr(last_turn, 'game_state') and last_turn.game_state:
                    game_details["game_over_reason"] = getattr(
                        last_turn.game_state, 'game_over_reason', None
                    )
        except Exception:
            pass

        game_result = {
            "game_id": game_id,
            "status": game_details.get("status", "unknown"),
            "winner": game_details.get("winner"),
            "turns_played": game_details.get("turns_played", 0),
            "num_players": game_details.get("num_players", 0),
            "player_uids": game_details.get("player_uids", []),
            "metrics": game_metrics,
            "game_over_reason": game_details.get("game_over_reason"),
            "character_templates": game_entry.get("character_templates", [])
        }

        per_game_results.append(game_result)
        evaluated_count += 1

        if verbose:
            print(f"    Winner: {game_result['winner'] or 'None'}")
            print(f"    Turns: {game_result['turns_played']}")
            print(f"    Metrics: {game_metrics}")

        print(f"  [OK] Evaluated {game_id}")

    # Calculate aggregate metrics
    print(f"\n{'='*60}")
    print("Calculating aggregate metrics...")
    aggregate_metrics = calculate_aggregate_metrics(per_game_results, dict(all_player_metrics))

    # Build final results
    results = {
        "benchmark_id": benchmark_id,
        "source_benchmarks": source_benchmarks,
        "evaluated_at": datetime.now().isoformat(),
        "games_evaluated": evaluated_count,
        "games_skipped": len(skipped_games) + eval_failed_count,
        "games_corrupted": len(corrupted_games),
        "evaluation_service": service_type,
        "evaluation_model": ai_model,
        "aggregate_metrics": aggregate_metrics,
        "per_game_results": per_game_results,
        "corrupted_games": corrupted_games
    }

    # Save results if output path provided
    if output_path:
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {output_path}")

    # Print summary
    print(f"\n{'='*60}")
    print(f"Evaluation Complete: {benchmark_id}")
    print(f"{'='*60}")
    print(f"\n  Games evaluated: {evaluated_count}")
    print(f"  Games skipped: {results['games_skipped']}")
    if corrupted_games:
        print(f"  Games corrupted (rate limited): {len(corrupted_games)}")
        for cg in corrupted_games:
            print(f"    - {cg['game_id']}: {cg['corruption_ratio']:.0%} bad responses")

    print(f"\n  Win Rates:")
    print(f"    Games with winner: {aggregate_metrics['win_rates']['games_with_winner']}/{aggregate_metrics['win_rates']['total_games']}")
    print(f"    Overall win rate: {aggregate_metrics['win_rates']['win_rate']:.1%}")
    if aggregate_metrics['win_rates']['per_player_wins']:
        print(f"    Per-player win rates:")
        for uid, stats in aggregate_metrics['win_rates']['per_player_wins'].items():
            print(f"      {uid}: {stats['wins']}/{stats['games']} ({stats['win_rate']:.1%})")

    print(f"\n  Turn Statistics:")
    print(f"    Average turns: {aggregate_metrics['turn_statistics']['average_turns']:.1f}")
    print(f"    Min/Max: {aggregate_metrics['turn_statistics']['min_turns']}/{aggregate_metrics['turn_statistics']['max_turns']}")
    print(f"    Median: {aggregate_metrics['turn_statistics']['median_turns']}")

    print(f"\n  Player Statistics:")
    print(f"    Avg players/game: {aggregate_metrics['player_statistics']['average_players_per_game']}")
    print(f"    Unique players: {aggregate_metrics['player_statistics']['unique_players']}")
    print(f"    Total responses: {aggregate_metrics['player_statistics']['total_responses_evaluated']}")

    print(f"\n  Evaluation Metrics (Overall):")
    for metric in EVAL_METRICS:
        stats = aggregate_metrics['evaluation_metrics'][metric]
        print(f"    {metric}: mean={stats['mean']:.3f}, std={stats['std']:.3f}, range=[{stats['min']:.3f}, {stats['max']:.3f}]")

    print(f"\n  Per-Player Metrics:")
    for player_uid, data in aggregate_metrics['per_player_metrics'].items():
        print(f"    {player_uid} ({data['total_responses']} responses):")
        for metric in EVAL_METRICS:
            stats = data['metrics'][metric]
            print(f"      {metric}: mean={stats['mean']:.3f}")

    print(f"\n  Game Outcomes:")
    print(f"    Completed normally: {aggregate_metrics['game_outcomes']['completed_normally']}")
    print(f"    Max turns reached: {aggregate_metrics['game_outcomes']['max_turns_reached']}")
    print(f"    All players dead: {aggregate_metrics['game_outcomes']['all_players_dead']}")

    print(f"{'='*60}\n")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate benchmark games and generate aggregate metrics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single benchmark
  python eval_benchmark.py --input benchmarks/benchmark_20250115_143022.json

  # Multiple specific files
  python eval_benchmark.py --input benchmarks/run_001.json benchmarks/run_002.json --output results/batch_eval.json

  # Glob pattern (all benchmarks)
  python eval_benchmark.py --input "benchmarks/benchmark_*.json" --output results/all_evals.json

  # With better model
  python eval_benchmark.py --input benchmarks/run_001.json --model gpt-4o-mini
        """
    )

    parser.add_argument(
        "--input", "-i",
        type=str,
        nargs='+',
        required=True,
        help="Path(s) to benchmark JSON file(s). Supports multiple files and globs (e.g., 'benchmarks/*.json')"
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Output file path for evaluation results (optional)"
    )

    parser.add_argument(
        "--service-type", "-s",
        type=str,
        default="custom",
        choices=["mock", "custom"],
        help="Evaluation service type (default: custom)"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    parser.add_argument(
        "--model", "-m",
        type=str,
        default="gpt-4.1-nano",
        help="AI model to use for evaluation (default: gpt-4.1-nano)"
    )

    args = parser.parse_args()

    # Run evaluation
    evaluate_benchmark(
        input_paths=args.input,  # Now a list
        output_path=args.output,
        service_type=args.service_type,
        ai_model=args.model,
        verbose=args.verbose
    )


if __name__ == "__main__":
    main()
