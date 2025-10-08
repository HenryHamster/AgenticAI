#!/usr/bin/env python3
"""
Local test runner for DungeonMaster / Game.

Usage examples:
  python main.py --num-players 3 --rounds 5 --model "gpt-4o" --openai-key YOUR_KEY
  python main.py --num-players 2 --rounds 2 --mock

What it does:
 - Optionally sets environment variables for API keys (OPENAI_API_KEY, ANTHROPIC_API_KEY)
 - Creates a small set of faux players (UIDs "player0", "player1", ...)
 - Instantiates Game(...) with player data and runs N rounds (async)
 - Prints brief round summaries and writes a JSON save to ./game_save.json
 - --mock uses a deterministic mock LLM responder to avoid network calls
"""

import argparse
import asyncio
import json
import os
import sys
from typing import Dict, Any

# Ensure src directory is importable when running from repo root
ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

# Imports from your project
from src.app.Game import Game             # Game class and orchestration. :contentReference[oaicite:4]{index=4}
from src.app.Player import Player         # Player shape / save/load. :contentReference[oaicite:5]{index=5}
from src.app.DungeonMaster import DungeonMaster  # DM generation routines. :contentReference[oaicite:6]{index=6}
from src.services.aiServices.wrapper import AIWrapper  # Unified AI interface. :contentReference[oaicite:7]{index=7}
from src.database.fileManager import Savable

def make_player_payload(uid: str, model: str = "GPT4o") -> Dict[str, Any]:
    """
    Minimal player data dict acceptable to Game.__init__ -> Player.load.
    Mirrors the structure Player.save produces.
    """
    return {
        "position": [0, 0],
        "UID": uid,
        "model": model,
        "player_class": "human",
        "values": {"money": 0, "health": 100},
        "responses": []
    }

def enable_env_keys(openai_key: str | None, anthropic_key: str | None):
    """
    If provided, set environment variables the service implementations will look for.
    Adjust key names if your service implementations expect different env var names.
    """
    if openai_key:
        os.environ["OPENAI_API_KEY"] = openai_key
    if anthropic_key:
        os.environ["ANTHROPIC_API_KEY"] = anthropic_key

def install_mock_ai():
    """
    Monkeypatch AIWrapper.ask to a lightweight, deterministic mock
    that works both when called synchronously (during initialization)
    and when awaited inside an event loop (player actions).
    This avoids modifying other files.
    """

    import asyncio

    def mock_ask(message: str,
                 model: str = "gpt-4o",
                 chat_id: str | None = None,
                 system_prompt: str | None = None,
                 structured_output = None,
                 isolated: bool = False):
        """
        Returns either a string (if called outside an event loop) or a coroutine
        (if called inside an event loop). Player.get_action awaits this result,
        and DungeonMaster.generate_tile calls it synchronously during Game init.
        """
        async def _impl():
            # Keep the mock short but deterministic
            cid = chat_id or "mock-chat"
            summary = f"[MOCK-{model}] ({cid})"
            # incorporate a tiny echo of input to help debugging
            snippet = (message[:100] + "...") if message and len(message) > 100 else (message or "")
            return f"{summary} Response -> {snippet}"

        try:
            # If there's a running loop, return coroutine (to be awaited by caller).
            loop = asyncio.get_running_loop()
            return _impl()
        except RuntimeError:
            # No running loop: run to completion and return concrete string (sync call).
            return asyncio.run(_impl())

    AIWrapper.ask = mock_ask  # type: ignore

async def run_game_rounds(game: Game, rounds: int):
    """
    Run the game for the specified number of rounds (awaiting Game.step()).
    Prints a small summary each round.
    """
    for r in range(1, rounds + 1):
        print(f"\n--- Round {r}/{rounds} ---")
        try:
            await game.step()
        except Exception as e:
            print(f"[ERROR] Exception during game step: {e}")
            raise
        # Print simple state: players' positions and last responses (if available)
        for uid, player in sorted(game.get_all_players().items()):
            pos = player.get_position()
            hist = player.get_responses_history()
            last = hist[-1] if hist else "(no response)"
            print(f"Player {uid} @ {pos} -> last: {last}")

def save_game_to_file(game: Game, path: str = "game_save.json"):
    """
    Persist game.save() JSON to disk (human-readable).
    """
    try:
        payload = game.save()
        # game.save() returns a JSON string via Savable.toJSON, ensure it's a dict for pretty output
        if isinstance(payload, str):
            try:
                obj = Savable.fromJSON(payload)
            except Exception:
                # If not JSON, just write raw string
                with open(path, "w", encoding="utf-8") as f:
                    f.write(payload)
                print(f"Saved raw game string to {path}")
                return
        else:
            obj = payload
        with open(path, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2)
        print(f"Game saved to {path}")
    except Exception as e:
        print(f"[WARN] Failed to save game: {e}")

def parse_args():
    p = argparse.ArgumentParser(description="Local test runner for DungeonMaster/Game")
    p.add_argument("--num-players", type=int, default=2, help="Number of fake players to create")
    p.add_argument("--rounds", type=int, default=3, help="Number of game rounds to run")
    p.add_argument("--model", type=str, default="GPT4o", help="Model id to attach to players / DM")
    p.add_argument("--openai-key", type=str, default=None, help="OpenAI API key (optional)")
    p.add_argument("--anthropic-key", type=str, default=None, help="Anthropic API key (optional)")
    p.add_argument("--mock", action="store_true", help="Enable mock LLM responses (no network)")
    p.add_argument("--save", type=str, default="game_save.json", help="Output path for final game save")
    return p.parse_args()

def main():
    args = parse_args()

    # Set environment API keys if provided
    enable_env_keys(args.openai_key, args.anthropic_key)

    # Optionally install a mock responder
    if args.mock:
        print("[INFO] Mock AI mode enabled — no external API calls will be made.")
        install_mock_ai()

    # Prepare player_info dict for Game constructor. Game expects each value to be a dict
    # in the same shape Player.save() would produce (Player.load expects that).
    player_info = {}
    for i in range(args.num_players):
        uid = f"player{i}"
        player_info[uid] = make_player_payload(uid, model=args.model)

    # Set DM model if you want to pass a different one: we create a DM and force the model
    dm = DungeonMaster(model=args.model)
    # Create game instance (this will call dm.generate_tile for initial tiles).
    # The Game constructor itself builds a DungeonMaster internally; still we create ours
    # to show the idea and demonstrate model selection. We'll pass player_info into Game.
    print("[INFO] Instantiating game (this may call the DM to generate some tiles)...")
    game = Game(player_info)

    # If you want to override DM model used inside the game:
    game.dm.model = args.model

    # Run the rounds inside asyncio
    try:
        asyncio.run(run_game_rounds(game, args.rounds))
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user.")
    except Exception as e:
        print(f"[ERROR] Uncaught exception while running game: {e}")

    # Save state
    save_game_to_file(game, args.save)
    print("[INFO] Done.")

if __name__ == "__main__":
    main()
