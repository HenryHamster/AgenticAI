export type TerrainType = 'mountain' | 'forest' | 'desert' | 'ocean' | 'plains';

export interface Player {
  uid: string;
  model: string;
  values: {
    money: number;
    health: number;
  };
  position: [number, number]; // [x, y]
  responses: string[];
  player_class: "human";
  level?: number;
  experience?: number;
  invalid_action_count?: number;
  total_action_count?: number;
  // Legacy fields for backwards compatibility
  name?: string;
  emoji?: string;
  validityScore?: number;
  creativityScore?: number;
  isActive?: boolean;
}

export interface Secret {
  key: string;
  value: number;
}

export interface Tile {
  position: [number, number]; // [x, y]
  description: string;
  secrets?: Secret[];
  // Legacy fields for backwards compatibility
  terrainType?: TerrainType;
  terrainEmoji?: string;
}

export interface PlayerAction {
  playerId: string;
  playerName: string;
  actionDeclaration: string;
  resolution: string;
  healthChange: number;
  currencyChange: number;
  validityScore: number;
  creativityScore: number;
  isValid: boolean;
}

export interface CharacterState {
  uid: string;
  money_change: number;
  health_change: number;
  position_change: [number, number];
}

export interface WorldState {
  tiles: {
    position: [number, number];
    description: string;
  }[];
}

export interface Turn {
  turnNumber: number;
  tiles: Tile[];
  players: { [key: string]: Player }; // Dictionary of players keyed by player ID
  dm?: {
    responses: string[];
  };
  player_responses?: { [key: string]: string };
  dungeon_master_verdict?: string;
  // Decomposed verdict components
  character_state_change?: CharacterState[];
  world_state_change?: WorldState | null;
  narrative_result?: string;
  world_size?: number; // Backend world_size parameter
  board_size?: number; // Calculated board dimension (2 * world_size + 1)
  // Legacy fields for backwards compatibility
  actions?: PlayerAction[];
  boardState?: Tile[][];
  playerStates?: Player[];
}

export interface GameRun {
  id: string;
  status?: string; // Game status (e.g., 'active', 'completed', 'cancelled')
  startTime: string;
  endTime: string;
  winnerId: string | null;
  players: { [key: string]: Player }; // Dictionary of players keyed by player ID
  turns: Turn[];
  targetCurrency: number;
  model?: string; // AI model used for the game
  world_size?: number; // Backend world_size parameter
  board_size?: number; // Calculated board dimension (2 * world_size + 1)
  initialTiles?: Tile[];
  // Legacy fields for backwards compatibility
  initialBoardState?: Tile[][];
  // New game summary fields
  winnerPlayerName?: string | null;
  currencyTarget?: number | null;
  maxTurns?: number | null;
  totalPlayers?: number | null;
  gameDuration?: string | null; // Duration as ISO 8601 string or seconds
  // Legacy fields for backwards compatibility
}

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
  worldSize?: number; // Optional world size (defaults to backend default if not provided)
}
