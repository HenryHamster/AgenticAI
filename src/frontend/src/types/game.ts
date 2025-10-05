export type TerrainType = 'mountain' | 'forest' | 'desert' | 'ocean' | 'plains';

export interface Player {
  id: string;
  name: string;
  emoji: string;
  health: number;
  currency: number;
  position: { x: number; y: number };
  class: "human";
  validityScore: number;
  creativityScore: number;
  isActive: boolean; // false if player died (health = 0)
}

export interface Tile {
  x: number;
  y: number;
  terrainType: TerrainType;
  terrainEmoji: string;
  description: string;
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

export interface Turn {
  turnNumber: number;
  actions: PlayerAction[];
  boardState: Tile[][];
  playerStates: Player[];
}

export interface GameRun {
  id: string;
  startTime: string;
  endTime: string;
  winnerId: string | null;
  players: Player[];
  turns: Turn[];
  targetCurrency: number;
  initialBoardState: Tile[][];
}

export interface PlayerSetup {
  name: string;
  class: 'human';
  startingCurrency: number;
  startingHealth: number;
  startingPosition: 'random' | { x: number; y: number };
  agentPrompt: string;
}

export interface GameCreationRequest {
  numberOfPlayers: number;
  players: PlayerSetup[];
  maxTurns: number | 'until_win';
  currencyGoal: number;
}
