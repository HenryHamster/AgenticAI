// Aligned with Backend Pydantic Models

export interface SecretKV {
  key: string;
  value: number;
}

export interface Tile {
  position: [number, number];
  secrets?: SecretKV[];
  description: string;
  terrainType: string;
  terrainEmoji: string;
}

export interface PlayerValues {
  money: number;
  health: number;
  inventory: string[];
}

export interface Player {
  uid: string;
  position: [number, number];
  model: string;
  player_class: string;
  values: PlayerValues;
  responses: string[];
  character_template_name?: string;
  current_abilities: string[];
  resource_pools: { [key: string]: number };
  skill_cooldowns: { [key: string]: number };
  experience: number;
  level: number;
  inventory: string[];
  invalid_action_count: number;
  total_action_count: number;
  agent_prompt: string;
}

export interface DungeonMaster {
  model: string;
  name: string;
  personality: string;
}

export interface CharacterState {
  uid: string;
  money_change: number;
  health_change: number;
  position_change: [number, number];
  experience_change: number;
  resource_changes: { [key: string]: number };
  skill_cooldowns: { [key: string]: number };
  new_unlocks: string[];
  action_was_invalid: boolean;
  inventory_add?: string[];
  inventory_remove?: string[];
}

export interface WorldState {
  tiles: Tile[];
}

export interface GameState {
  players: { [key: string]: Player };
  dm: DungeonMaster;
  tiles: Tile[];
  player_responses: { [key: string]: string };
  dungeon_master_verdict: string;
  character_state_change: CharacterState[];
  world_state_change: WorldState | null;
  narrative_result: string;
  is_game_over: boolean;
  game_over_reason?: string | null;
}

export interface Turn {
  id?: number;
  game_id: string;
  turn_number: number;
  game_state: GameState;
  created_at?: string;
  experience_awarded: { [key: string]: number };
  level_ups: { [key: string]: number };
  unlocked_skills: { [key: string]: string[] };
}

export interface PlayerConfig {
  name: string;
  starting_health: number;
  starting_currency: number;
  character_class?: string | null;
  agent_prompt?: string | null;
}

export interface GameRun {
  id: string;
  name: string;
  description: string;
  status: string;
  model: string;
  world_size: number;
  winner_player_name?: string | null;
  currency_target?: number | null;
  max_turns?: number | null;
  total_players?: number | null;
  starting_currency?: number | null;
  starting_health?: number | null;
  player_configs?: PlayerConfig[] | null;
  game_duration?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
  // The backend now returns 'turns' as part of the game detail
  turns: Turn[];
}

export interface CreateGameRequest {
  game_config: {
    world_size: number;
    model_mode: string;
    currency_target: number;
    max_turns: number;
  };
  players: PlayerConfig[];
}

// --- Form Types (Used in Game Creation Page) ---

export interface PlayerSetup {
  name: string;
  class: 'human';
  startingCurrency: number;
  startingHealth: number;
  startingPosition: 'random' | [number, number];
  agentPrompt: string;
  characterClass?: 'Warrior' | 'Mage' | 'Rogue';
}

export interface GameCreationRequest {
  numberOfPlayers: number;
  players: PlayerSetup[];
  maxTurns: number | 'until_win';
  currencyGoal: number;
  worldSize?: number;
}
