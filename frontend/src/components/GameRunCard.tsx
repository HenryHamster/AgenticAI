import Link from 'next/link';
import { GameRun } from '@/types/game';

interface GameRunCardProps {
  gameRun: GameRun;
}

export default function GameRunCard({ gameRun }: GameRunCardProps) {
  // Convert players dictionary to array
  const playersArray = gameRun.players ? Object.values(gameRun.players) : [];
  const winner = gameRun.winnerId && gameRun.players ? gameRun.players[gameRun.winnerId] : null;
  const startDate = new Date(gameRun.created_at);
  const endDate = new Date(gameRun.endTime);
  const duration = Math.round((endDate.getTime() - startDate.getTime()) / 1000 / 60); // minutes

  return (
    <Link href={`/game/${gameRun.id}`}>
      <div className="border border-gray-300 rounded-lg p-4 hover:shadow-lg hover:border-blue-400 transition-all cursor-pointer bg-white">
        <div className="flex items-start justify-between mb-3">
          <div>
            <h3 className="text-lg font-bold text-gray-800">
              Game #{gameRun.id.slice(0, 8)}
            </h3>
            <p className="text-xs text-gray-500">
              {startDate.toLocaleDateString()} {startDate.toLocaleTimeString()}
            </p>
          </div>
          
          {winner && (
            <div className="flex items-center gap-1 bg-yellow-100 px-2 py-1 rounded">
              <span className="text-lg">{winner.emoji || '🏆'}</span>
              <span className="text-xs font-semibold text-yellow-800">Winner</span>
            </div>
          )}
        </div>

        <div className="grid grid-cols-2 gap-3 text-sm mb-3">
          <div className="flex items-center gap-2">
            <span className="text-gray-600">Players:</span>
            <span className="font-semibold text-gray-600">{playersArray.length}</span>
          </div>
          
          <div className="flex items-center gap-2">
            <span className="text-gray-600">Turns:</span>
            <span className="font-semibold text-gray-600">{gameRun.turns?.length || 0}</span>
          </div>
          
          <div className="flex items-center gap-2">
            <span className="text-gray-600">Duration:</span>
            <span className="font-semibold text-gray-600">{duration}m</span>
          </div>
          
          <div className="flex items-center gap-2">
            <span className="text-gray-600">Target:</span>
            <span className="font-semibold text-gray-600">💰 {gameRun.targetCurrency}</span>
          </div>
        </div>

        <div className="flex items-center gap-1 pt-2 border-t">
          {playersArray.slice(0, 4).map((player) => (
            <span key={player.uid || (player as any).id} className="text-xl" title={player.name || player.uid}>
              {player.emoji || '🧙'}
            </span>
          ))}
          {playersArray.length > 4 && (
            <span className="text-sm text-gray-500">+{playersArray.length - 4}</span>
          )}
        </div>
      </div>
    </Link>
  );
}
