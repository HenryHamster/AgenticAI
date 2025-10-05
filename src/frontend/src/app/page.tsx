import { fetchGameRuns } from '@/services/api';
import GameRunCard from '@/components/GameRunCard';

export default async function Home() {
  const gameRuns = await fetchGameRuns();

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
      <div className="max-w-7xl mx-auto">
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            🎮 Dungeon Master
          </h1>
          <p className="text-gray-600">
            Turn-based RPG game runs and history viewer
          </p>
        </header>

        {gameRuns.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <div className="text-6xl mb-4">🎲</div>
            <h2 className="text-2xl font-semibold text-gray-700 mb-2">
              No Game Runs Yet
            </h2>
            <p className="text-gray-500">
              Game runs will appear here once they are completed.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {gameRuns.map((gameRun) => (
              <GameRunCard key={gameRun.id} gameRun={gameRun} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
