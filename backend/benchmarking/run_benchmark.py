"""
Benchmark Runner - Runs multiple games for benchmarking purposes

Usage:
    python run_benchmark.py --num-games 10 --model "gpt-4.1-nano"
    python run_benchmark.py --num-games 5 --mock  # For testing without API calls
"""

import os
import sys
import argparse
import json
import uuid
import random
import time
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.database.gameService import save_game_to_database
from services.gameWorker import run_game_sync
from schema.gameModel import GameModel, PlayerConfigModel
from schema.enums import GameStatus


# Available character templates
AVAILABLE_TEMPLATES = ["warrior", "mage", "rogue"]

# Fixed game parameters for reproducibility
DEFAULT_WORLD_SIZE = 2
DEFAULT_MAX_TURNS = 10
DEFAULT_CURRENCY_TARGET = 1000
DEFAULT_STARTING_CURRENCY = 0
DEFAULT_STARTING_HEALTH = 100


def generate_random_player_configs(
    num_players: int,
    player_models: dict[int, str] = None
) -> list[PlayerConfigModel]:
    """
    Generate random player configurations with randomized character templates.

    Args:
        num_players: Number of players to create
        player_models: Optional dict mapping player index to model string (e.g., {0: "a2a://localhost:9018"})

    Returns:
        List of PlayerConfigModel instances
    """
    player_models = player_models or {}
    configs = []
    for i in range(num_players):
        # Randomly choose a template (always assign one)
        template = random.choice(AVAILABLE_TEMPLATES)
        configs.append(PlayerConfigModel(
            name=f"player{i}",
            starting_health=DEFAULT_STARTING_HEALTH,
            starting_currency=DEFAULT_STARTING_CURRENCY,
            character_class=template,
            agent_prompt="",
            model=player_models.get(i)  # Per-player model override
        ))
    return configs


def create_game_for_benchmark(
    model: str,
    verbose: bool = False,
    num_players: int = None,
    player_models: dict[int, str] = None
) -> tuple[str, int, list[str]]:
    """
    Create a game with randomized configuration for benchmarking.

    Args:
        model: Default AI model to use
        verbose: Enable verbose logging
        num_players: Fixed number of players (random 2-5 if None)
        player_models: Optional dict mapping player index to model string

    Returns:
        Tuple of (game_id, num_players, character_templates)
    """
    game_id = f"bench_{uuid.uuid4().hex[:8]}"
    if num_players is None:
        num_players = random.randint(2, 5)
    player_configs = generate_random_player_configs(num_players, player_models)

    # Extract template names for logging
    templates = [p.character_class for p in player_configs]

    if verbose:
        print(f"  Creating game {game_id} with {num_players} players")
        print(f"  Templates: {templates}")

    # Create GameModel with PENDING status
    game_model = GameModel(
        id=game_id,
        name=f"Benchmark {game_id}",
        description=f"Benchmark game with {num_players} players",
        status=GameStatus.PENDING,
        model=model,
        world_size=DEFAULT_WORLD_SIZE,
        currency_target=DEFAULT_CURRENCY_TARGET,
        total_players=num_players,
        max_turns=DEFAULT_MAX_TURNS,
        player_configs=player_configs,
        starting_currency=DEFAULT_STARTING_CURRENCY,
        starting_health=DEFAULT_STARTING_HEALTH,
    )

    # Save to database
    save_game_to_database(game_model)

    return game_id, num_players, templates


def run_single_game(game_id: str, verbose: bool = False) -> tuple[bool, str | None]:
    """
    Run a single game and return success status.

    Args:
        game_id: ID of the game to run
        verbose: Enable verbose logging

    Returns:
        Tuple of (success, error_message)
    """
    try:
        run_game_sync(game_id=game_id, verbose=verbose)
        return True, None
    except Exception as e:
        error_msg = str(e)
        # Check for rate limit errors
        if "rate" in error_msg.lower() or "429" in error_msg:
            return False, f"Rate limit: {error_msg}"
        return False, error_msg


def is_rate_limit_error(error: str | None) -> bool:
    """Check if an error message indicates a rate limit."""
    if not error:
        return False
    error_lower = error.lower()
    return "rate" in error_lower or "429" in error_lower or "limit" in error_lower


def run_benchmark(
    num_games: int,
    model: str,
    output_path: str,
    delay_seconds: float = 2.0,
    verbose: bool = False,
    stop_on_rate_limit: bool = True,
    agent_model: str = None,
    num_players: int = None
) -> dict:
    """
    Run multiple benchmark games and save results.

    Args:
        num_games: Number of games to run
        model: Default AI model to use (baseline)
        output_path: Path to save results JSON
        delay_seconds: Delay between games
        verbose: Enable verbose logging
        stop_on_rate_limit: Stop early if rate limit hit
        agent_model: Optional A2A agent model for player0 (e.g., "a2a://localhost:9018")
        num_players: Fixed number of players (default: 2 for agent vs baseline, random otherwise)

    Returns:
        Benchmark results dictionary
    """
    benchmark_id = f"bench_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    created_at = datetime.now().isoformat()

    # Build player_models dict if agent specified
    player_models = None
    if agent_model:
        player_models = {0: agent_model}  # Player0 uses the agent
        if num_players is None:
            num_players = 2  # Default to 2 players for agent vs baseline

    print(f"\n{'='*60}")
    print(f"Starting Benchmark Run: {benchmark_id}")
    print(f"{'='*60}")
    print(f"  Games to run: {num_games}")
    print(f"  Baseline model: {model}")
    if agent_model:
        print(f"  Agent (player0): {agent_model}")
        print(f"  Players: {num_players}")
    print(f"  Delay between games: {delay_seconds}s")
    print(f"  Output: {output_path}")
    print(f"{'='*60}\n")

    results = {
        "benchmark_id": benchmark_id,
        "created_at": created_at,
        "config": {
            "model": model,
            "agent_model": agent_model,
            "num_players": num_players,
            "num_games_requested": num_games,
            "delay_seconds": delay_seconds,
            "world_size": DEFAULT_WORLD_SIZE,
            "max_turns": DEFAULT_MAX_TURNS,
            "currency_target": DEFAULT_CURRENCY_TARGET,
        },
        "games": [],
        "summary": {
            "total_requested": num_games,
            "completed": 0,
            "failed": 0,
            "success_rate": 0.0
        }
    }

    completed = 0
    failed = 0

    for i in range(num_games):
        game_num = i + 1
        print(f"\n[{game_num}/{num_games}] Running game...")

        game_entry = {
            "game_id": None,
            "status": "pending",
            "num_players": 0,
            "character_templates": [],
            "started_at": datetime.now().isoformat(),
            "completed_at": None,
            "error": None
        }

        try:
            # Create game
            game_id, game_num_players, templates = create_game_for_benchmark(
                model, verbose, num_players, player_models
            )
            game_entry["game_id"] = game_id
            game_entry["num_players"] = game_num_players
            game_entry["character_templates"] = templates

            # Run game
            print(f"  Running game {game_id}...")
            success, error = run_single_game(game_id, verbose)

            game_entry["completed_at"] = datetime.now().isoformat()

            if success:
                game_entry["status"] = "completed"
                completed += 1
                print(f"  [OK] Game {game_id} completed successfully")
            else:
                game_entry["status"] = "error"
                game_entry["error"] = error
                failed += 1
                print(f"  [FAILED] Game {game_id}: {error}")

                # Check for rate limit
                if stop_on_rate_limit and is_rate_limit_error(error):
                    print(f"\n[!] Rate limit detected after {game_num} games. Stopping early.")
                    results["games"].append(game_entry)
                    break

        except Exception as e:
            game_entry["status"] = "error"
            game_entry["error"] = str(e)
            game_entry["completed_at"] = datetime.now().isoformat()
            failed += 1
            print(f"  [ERROR] Unexpected error: {e}")

            if stop_on_rate_limit and is_rate_limit_error(str(e)):
                print(f"\n[!] Rate limit detected after {game_num} games. Stopping early.")
                results["games"].append(game_entry)
                break

        results["games"].append(game_entry)

        # Delay before next game (except for last one)
        if i < num_games - 1:
            if verbose:
                print(f"  Waiting {delay_seconds}s before next game...")
            time.sleep(delay_seconds)

    # Update summary
    results["summary"]["completed"] = completed
    results["summary"]["failed"] = failed
    total_run = completed + failed
    results["summary"]["success_rate"] = completed / total_run if total_run > 0 else 0.0

    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Save results
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    # Print summary
    print(f"\n{'='*60}")
    print(f"Benchmark Complete: {benchmark_id}")
    print(f"{'='*60}")
    print(f"  Games completed: {completed}/{num_games}")
    print(f"  Games failed: {failed}")
    print(f"  Success rate: {results['summary']['success_rate']:.1%}")
    print(f"  Results saved to: {output_path}")
    print(f"{'='*60}\n")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Run benchmark games for evaluation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # All players use same model
  python run_benchmark.py --num-games 10 --model gpt-4.1-nano
  python run_benchmark.py --num-games 5 --mock

  # A2A agent (player0) vs baseline model (player1)
  python run_benchmark.py --num-games 5 --agent a2a://localhost:9018 --model gpt-4.1-nano

  # A2A agent vs baseline with more players
  python run_benchmark.py --num-games 3 --agent a2a://localhost:9018 --model gpt-4.1-nano --num-players 3
        """
    )

    parser.add_argument(
        "--num-games", "-n",
        type=int,
        default=10,
        help="Number of games to run (default: 10)"
    )

    parser.add_argument(
        "--model", "-m",
        type=str,
        default="gpt-4.1-nano",
        help="AI model to use (default: gpt-4.1-nano)"
    )

    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use mock AI (no API calls)"
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Output file path (default: benchmarks/benchmark_TIMESTAMP.json)"
    )

    parser.add_argument(
        "--delay", "-d",
        type=float,
        default=2.0,
        help="Delay between games in seconds (default: 2.0)"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    parser.add_argument(
        "--no-stop-on-rate-limit",
        action="store_true",
        help="Continue running even if rate limit is hit"
    )

    parser.add_argument(
        "--agent", "-a",
        type=str,
        default=None,
        help="A2A agent URL for player0 (e.g., a2a://localhost:9018). Baseline model used for other players."
    )

    parser.add_argument(
        "--num-players", "-p",
        type=int,
        default=None,
        help="Fixed number of players (default: 2 when --agent is used, random 2-5 otherwise)"
    )

    args = parser.parse_args()

    # Determine model
    model = "mock" if args.mock else args.model

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Create output in benchmarking/benchmarks/ directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, "benchmarks", f"benchmark_{timestamp}.json")

    # Run benchmark
    run_benchmark(
        num_games=args.num_games,
        model=model,
        output_path=output_path,
        delay_seconds=args.delay,
        verbose=args.verbose,
        stop_on_rate_limit=not args.no_stop_on_rate_limit,
        agent_model=args.agent,
        num_players=args.num_players
    )


if __name__ == "__main__":
    main()
