import { fetchGameRunById } from '@/services/api';
import GameDetailClient from '@/components/GameDetailClient';
import Link from 'next/link';
import { GameRun } from '@/types/game';

interface PageProps {
  params: Promise<{ id: string }>;
}

export default async function GameDetailPage({ params }: PageProps) {
  const { id } = await params;
  
  // Fetch game data
  const gameRun = await fetchGameRunById(id) as GameRun;

  if (!gameRun) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
        <div className="max-w-7xl mx-auto">
          <Link 
            href="/" 
            className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 mb-6"
          >
            ← Back to Game Runs
          </Link>
          
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <div className="text-6xl mb-4">🎮</div>
            <h2 className="text-2xl font-semibold text-gray-700 mb-2">
              Game Not Found
            </h2>
            <p className="text-gray-500 mb-4">
              The game run with ID "{id}" could not be found.
            </p>
            <p className="text-sm text-gray-400">
              Mock data needs to be added to see game details.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
      <div className="max-w-7xl mx-auto">
        <Link 
          href="/" 
          className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 mb-4"
        >
          ← Back to Game Runs
        </Link>
        
        <GameDetailClient gameRun={gameRun} />
      </div>
    </div>
  );
}
