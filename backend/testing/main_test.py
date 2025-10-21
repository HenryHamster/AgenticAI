#!/usr/bin/env python3
"""
Local test runner for DungeonMaster / Game.

Usage examples:
  python main.py --num-players 3 --rounds 5 --model "gpt-4.1-nano" --openai-key YOUR_KEY
  python main.py --num-players 2 --rounds 2 --mock
  python main.py -v --num-players 2 --rounds 2 --mock   # verbose step-by-step
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime   
from typing import Dict, Any

# append the parent directory to the path BEFORE imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()


from datetime import datetime
# Imports from your project
from src.app.Game import Game
from src.app.Player import Player
from src.app.DungeonMaster import DungeonMaster
from src.services.aiServices.wrapper import AIWrapper
from database.fileManager import Savable


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


def make_player_payload(uid: str, model: str = "gpt-4.1-nano") -> Dict[str, Any]:
    return {
        "position": [0, 0],
        "UID": uid,
        "model": model,
        "player_class": "human",
        "values": {"money": 0, "health": 100},
        "responses": []
    }

def make_dm_payload(model: str = "gpt-4.1-nano") -> Dict[str, Any]:
    return {
        "model": model
    }


def enable_env_keys(openai_key: str | None, anthropic_key: str | None):
    if openai_key:
        os.environ["OPENAI_API_KEY"] = openai_key
    if anthropic_key:
        os.environ["ANTHROPIC_API_KEY"] = anthropic_key


def run_game_rounds(game: Game, rounds: int, vprint: StepPrinter):
    """
    Run the game for the specified number of rounds, emitting step-by-step
    updates when verbose printing is enabled.
    """
    game_index = datetime.now().strftime("%d_%H%M%S")
    for r in range(1, rounds + 1):
        vprint.banner(f"Round {r}/{rounds} — begin")
        try:
            # Pre-step snapshot
            vprint("Pre-step snapshot:")
            for uid, player in sorted(game.get_all_players().items()):
                vprint.kv(
                    uid=uid,
                    position=player.get_position(),
                    money=getattr(player.values, "money", "?"),
                    health=getattr(player.values, "health", "?"),
                    last=len(player.get_responses_history() or []),
                )

            vprint(f"Executing game.step() {r} …")
            game.step()

            # vprint("Post-step updates:")
            # for uid, player in sorted(game.get_all_players().items()):
            #     pos = player.get_position()
            #     hist = player.get_responses_history()
            #     last = hist[-1] if hist else "(no response)"
            #     vprint.kv(
            #         uid=uid,
            #         position=pos,
            #         money=getattr(player.values, "money", "?"),
            #         health=getattr(player.values, "health", "?"),
            #         last_response=last,
            #     )
            vprint.banner(f"Round {r}/{rounds} — end")
            save_game_to_file(game, path=f"data/game_save_{game_index}.json")
            save_game_to_file(game, path=f"data/rounds/rounds_game_save_{r}_{game_index}.json")

        except Exception as e:
            print(f"[ERROR] Exception during game step: {e}")
            raise


def save_game_to_file(game: "Game", path: str = "data/game_save.json") -> None:
    # Materialize current game's JSON object (keep this simple)
    payload = game.save()
    obj = json.loads(payload) if isinstance(payload, str) else payload

    # Ensure parent directory exists
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    if os.path.exists(path):
        # Assume: file contains a clean JSON list of timestep-indexed dicts
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        data.append(obj)
    else:
        data = [obj]

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)



def parse_args():
    p = argparse.ArgumentParser(description="Local test runner for DungeonMaster/Game")
    p.add_argument("--num-players", type=int, default=2, help="Number of fake players to create")
    p.add_argument("--rounds", type=int, default=3, help="Number of game rounds to run")
    p.add_argument("--model", type=str, default="gpt-4.1-nano", help="Model id to attach to players / DM")
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
        print("[INFO] Mock AI mode enabled — using MockAiService (no external API calls).")
        args.model = "mock"


    player_info = {}
    for i in range(args.num_players):
        uid = f"player{i}"
        player_info[uid] = make_player_payload(uid, model=args.model)

    dm_info = make_dm_payload(model=args.model)
    print("[INFO] Instantiating game (this may call the DM to generate some tiles)...")
    game = Game(player_info,dm_info=dm_info)

    try:
        run_game_rounds(game, args.rounds, vprint)
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user.")
    except Exception as e:
        print(f"[ERROR] Uncaught exception while running game: {e}")

    save_game_to_file(game, args.save)
    print("[INFO] Done.")


if __name__ == "__main__":
    main()
