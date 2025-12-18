import { GameRun } from '@/types/game';
const NEXT_PUBLIC_SERVER_SIDE_API_URL = process.env.NEXT_PUBLIC_SERVER_SIDE_API_URL || 'http://localhost:8000/api/v1';

export async function fetchGameRunById(id: string): Promise<GameRun | null> {
  try {
    console.log("Fetching game by ID:", id);
    console.log("server side base url:", NEXT_PUBLIC_SERVER_SIDE_API_URL);
    const response = await fetch(`${NEXT_PUBLIC_SERVER_SIDE_API_URL}/game/${id}?include_turns=true`);
    
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
