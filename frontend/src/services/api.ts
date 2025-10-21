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
  // Map frontend game creation request to backend JSON body
  // Backend expects: { game_config: {...}, players: [...] }
  
  const requestBody = {
    game_config: {
      world_size: gameRequest.worldSize || 2,
      model_mode: 'gpt-4.1-mini',
      currency_target: gameRequest.currencyGoal,
      max_turns: gameRequest.maxTurns === 'until_win' ? 100 : gameRequest.maxTurns,
    },
    players: gameRequest.players.map(player => ({
      name: player.name,
      starting_health: player.startingHealth,
      starting_currency: player.startingCurrency,
    })),
  };
  
  const response = await fetch(`${FRONTEND_BASE_URL}/games/create`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(requestBody),
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to create game: ${response.statusText}`);
  }
  
  const data = await response.json();
  return data.game_id;
}
