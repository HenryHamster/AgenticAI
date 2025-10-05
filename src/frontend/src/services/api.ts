import { GameRun, Turn } from '@/types/game';
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
