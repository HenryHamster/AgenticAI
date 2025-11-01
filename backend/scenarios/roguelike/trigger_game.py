"""Trigger game"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import asyncio
from agentbeats_lib.client_cli import main as cli_main

if __name__ == "__main__":
    sys.argv = ["trigger_game.py", "scenarios/roguelike/scenario.toml"]
    asyncio.run(cli_main())
