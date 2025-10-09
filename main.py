#!/usr/bin/env python3
"""
Local test runner for DungeonMaster / Game.

Usage examples:
  python main.py --num-players 3 --rounds 5 --model "gpt-4o" --openai-key YOUR_KEY
  python main.py --num-players 2 --rounds 2 --mock
  python main.py -v --num-players 2 --rounds 2 --mock   # verbose step-by-step
"""

import argparse
import asyncio
import json
import os
from typing import Dict, Any

# Imports from your project
from src.app.Game import Game
from src.app.Player import Player
from src.app.DungeonMaster import DungeonMaster
from src.services.aiServices.wrapper import AIWrapper
from src.database.fileManager import Savable


# ------------------ Verbose printing helper ------------------
class StepPrinter:
    """Lightweight logger that only prints when enabled."""
    def __init__(self, enabled: bool):
        self.enabled = bool(enabled)

    def __call__(self, *parts, sep: str = " ", prefix: str = "[v]", end: str = "\n", flush: bool = True):
        if self.enabled:
            print(prefix, *parts, sep=sep, end=end, flush=flush)

    def banner(self, title: str):
        if self.enabled:
            print(f"\n[v] ==== {title} ====", flush=True)

    def kv(self, **items):
        if self.enabled:
            pairs = "  ".join(f"{k}={v}" for k, v in items.items())
            print(f"[v] {pairs}", flush=True)


def make_player_payload(uid: str, model: str = "GPT4o") -> Dict[str, Any]:
    return {
        "position": [0, 0],
        "UID": uid,
        "model": model,
        "player_class": "human",
        "values": {"money": 0, "health": 100},
        "responses": []
    }


def enable_env_keys(openai_key: str | None, anthropic_key: str | None):
    if openai_key:
        os.environ["OPENAI_API_KEY"] = openai_key
    if anthropic_key:
        os.environ["ANTHROPIC_API_KEY"] = anthropic_key


def install_mock_ai():
    import asyncio

    def mock_ask(message: str,
                 model: str = "gpt-4o",
                 chat_id: str | None = None,
                 system_prompt: str | None = None,
                 structured_output=None,
                 isolated: bool = False):
        async def _impl():
            cid = chat_id or "mock-chat"
            summary = f"[MOCK-{model}] ({cid})"
            snippet = (message[:100] + "...") if message and len(message) > 100 else (message or "")
            return f"{summary} Response -> {snippet}"

        try:
            asyncio.get_running_loop()
            return _impl()
        except RuntimeError:
            return asyncio.run(_impl())

    AIWrapper.ask = mock_ask  # type: ignore


async def run_game_rounds(game: Game, rounds: int, vprint: StepPrinter):
    """
    Run the game for the specified number of rounds, emitting step-by-step
    updates when verbose printing is enabled.
    """
    for r in range(1, rounds + 1):
        vprint.banner(f"Round {r}/{rounds} — begin")
        try:
            # Pre-step snapshot
            vprint("Pre-step snapshot:")
            for uid, player in sorted(game.get_all_players().items()):
                vprint.kv(uid=uid, position=player.get_position(), last=len(player.get_responses_history() or []))

            vprint("Executing game.step() …")
            await game.step()

            vprint("Post-step updates:")
            for uid, player in sorted(game.get_all_players().items()):
                pos = player.get_position()
                hist = player.get_responses_history()
                last = hist[-1] if hist else "(no response)"
                vprint.kv(uid=uid, position=pos, last_response=last)

            vprint.banner(f"Round {r}/{rounds} — end")

        except Exception as e:
            print(f"[ERROR] Exception during game step: {e}")
            raise


def save_game_to_file(game: Game, path: str = "game_save.json"):
    try:
        payload = game.save()
        if isinstance(payload, str):
            try:
                obj = Savable.fromJSON(payload)
            except Exception:
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
    p.add_argument("-v", "--verbose", action="store_true", help="Print step-by-step updates each round")
    return p.parse_args()


def main():
    args = parse_args()
    vprint = StepPrinter(args.verbose)

    enable_env_keys(args.openai_key, args.anthropic_key)

    if args.mock:
        print("[INFO] Mock AI mode enabled — no external API calls will be made.")
        install_mock_ai()

    player_info = {}
    for i in range(args.num_players):
        uid = f"player{i}"
        player_info[uid] = make_player_payload(uid, model=args.model)

    dm = DungeonMaster(model=args.model)
    print("[INFO] Instantiating game (this may call the DM to generate some tiles)...")
    game = Game(player_info)
    game.dm.model = args.model

    try:
        asyncio.run(run_game_rounds(game, args.rounds, vprint))
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user.")
    except Exception as e:
        print(f"[ERROR] Uncaught exception while running game: {e}")

    save_game_to_file(game, args.save)
    print("[INFO] Done.")


if __name__ == "__main__":
    main()
