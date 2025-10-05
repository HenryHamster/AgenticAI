import { GameRun, Turn, GameCreationRequest } from '@/types/game';
import {mockGameRuns} from '@/scripts/generateMockData';

/**
 * API service for fetching game data
 * Currently returns mock data - will be replaced with actual API calls
 */
console.log(mockGameRuns)
export async function fetchGameRuns(): Promise<GameRun[]> {
  // TODO: Replace with actual API call
  // const response = await fetch('/api/game-runs');
  // return response.json();
  
  // Using mock data for now
  return mockGameRuns;
}

export async function fetchGameRunById(id: string): Promise<GameRun | null> {
  // TODO: Replace with actual API call
  // const response = await fetch(`/api/game-runs/${id}`);
  // return response.json();
  
  // Using mock data for now
  return mockGameRuns.find(game => game.id === id) || null;
}

export async function fetchTurnByNumber(gameId: string, turnNumber: number): Promise<Turn | null> {
  // TODO: Replace with actual API call
  // const response = await fetch(`/api/game-runs/${gameId}/turns/${turnNumber}`);
  // return response.json();
  
  // Using mock data for now
  const gameRun = mockGameRuns.find(game => game.id === gameId);
  if (!gameRun) return null;
  
  return gameRun.turns.find(turn => turn.turnNumber === turnNumber) || null;
}

export async function createGame(gameRequest: GameCreationRequest): Promise<string> {
  // TODO: Replace with actual API call to backend
  // const response = await fetch('/api/game-runs', {
  //   method: 'POST',
  //   headers: { 'Content-Type': 'application/json' },
  //   body: JSON.stringify(gameRequest),
  // });
  // const data = await response.json();
  // return data.id;
  
  // Mock implementation - simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  console.log('Game creation request:', gameRequest);
  
  // Return a mock game ID for now
  const mockGameId = `game-${Date.now()}`;
  return mockGameId;
}
