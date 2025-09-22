# Agentic AI

## Overview
THis projectis a text-led roguelike economy simulator where large-language-model agents explore a shared tile grid, trade, and compete to grow their wealth. Each tile carries a concise natural-language description that is fed back into the model loop so that actions can continuously reshape the world narrative (e.g., a forest tile becomes scorched after being burned).

## Core Agents
- **Green Agent (Controller / Dungeon Master):** bootstraps the map, orchestrates economic events, and adjudicates every player action before updating global state.
- **White Agents (Players):** submit short, turn-based intentions, track private stats such as health and inventory, and navigate the grid to pursue profit.

## Turn Cycle
1. Players propose single-sentence actions for the current turn.
2. The controller batches and resolves the actions against the shared world model.
3. Updated tile descriptions and personal stats are broadcast to every participant.
4. The loop repeats until the scenario ends or a win condition is satisfied.

The baseline objective is wealth maximization within a dynamic local economy, though alternative victory conditions can be layered on top of the turn loop.

## Project Structure
- `Main.py`: entry point that will wire together the game loop and orchestration logic.
- `src/Game.py`: placeholder for the main simulation driver.
- `src/Agent.py`: planned interface to the LLM backends used for both controller and player agents.
- `src/FileManager.py`: specification for persisting world state via coordinate-to-description hashes.
- `data/Agentic AI Master File.txt`: design document detailing the MVP concept and agent responsibilities.
- `playground.ipynb`: scratchpad for rapid prototyping and experimentation.

## Next Steps
- Flesh out the game loop inside `src/Game.py`, including turn orchestration and state mutation hooks.
- Implement the LLM plumbing in `src/Agent.py` so agents can interpret context and produce actions reliably.
- Complete the persistence layer outlined in `src/FileManager.py` and design player state schemas as noted in the master file.
- Define automated tests that validate state transitions, economic balancing, and tile description updates.
