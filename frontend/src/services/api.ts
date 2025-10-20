import { GameRun, Turn, GameCreationRequest } from '@/types/game';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
export const FRONTEND_BASE_URL = process.env.NEXT_PUBLIC_FRONTEND_URL || 'http://localhost:8000/api/v1';

/**
 * API service for fetching game data from the FastAPI backend
 */
export async function fetchGameRuns(): Promise<GameRun[]> {
  const response = await fetch(`${API_BASE_URL}/games`);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch games: ${response.statusText}`);
  }
  
  const data = await response.json() as GameRun[];
  return data.sort((a: any, b: any) => new Date(b.startTime).getTime() - new Date(a.startTime).getTime());
}

export async function fetchGameRunById(id: string): Promise<GameRun | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/game/${id}?include_turns=true`);
    
    if (response.status === 404) {
      return null;
    }
    
    if (!response.ok) {
      throw new Error(`Failed to fetch game: ${response.statusText}`);
    }
    
    return response.json();
  } catch (error) {
    console.error('Error fetching game by ID:', error);
    return null;
  }
}

export async function fetchTurnByNumber(gameId: string, turnNumber: number): Promise<Turn | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/game/${gameId}?include_turns=true`);
    
    if (response.status === 404) {
      return null;
    }
    
    if (!response.ok) {
      throw new Error(`Failed to fetch game turns: ${response.statusText}`);
    }
    
    const gameRun = await response.json();
    return gameRun.turns?.find((turn: Turn) => turn.turnNumber === turnNumber) || null;
  } catch (error) {
    console.error('Error fetching turn:', error);
    return null;
  }
}

export async function createGame(gameRequest: GameCreationRequest): Promise<string> {
  // Map frontend game creation request to backend query parameters
  // Backend expects: number_of_rounds, number_of_players, world_size, model_mode, currency_target, starting_currency, starting_health
  
  // Use first player's settings as defaults, or game-level defaults
  const firstPlayer = gameRequest.players[0];
  
  const params = new URLSearchParams({
    number_of_players: gameRequest.numberOfPlayers.toString(),
    number_of_rounds: gameRequest.maxTurns === 'until_win' ? '100' : gameRequest.maxTurns.toString(),
    world_size: (gameRequest.worldSize || 5).toString(),
    model_mode: 'gpt-4.1-nano', // Default to mock mode for now
    currency_target: gameRequest.currencyGoal.toString(),
    starting_currency: firstPlayer.startingCurrency.toString(),
    starting_health: firstPlayer.startingHealth.toString(),
  });
  
  const response = await fetch(`${FRONTEND_BASE_URL}/games/create?${params}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  });
  
  if (!response.ok) {
    throw new Error(`Failed to create game: ${response.statusText}`);
  }
  
  const data = await response.json();
  return data.game_id;
}
