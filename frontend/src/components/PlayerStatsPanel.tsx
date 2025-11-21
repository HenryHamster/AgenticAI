import { Player } from '@/types/game';

interface PlayerStatsPanelProps {
  players: Player[];
  targetCurrency: number;
}

export default function PlayerStatsPanel({ players, targetCurrency }: PlayerStatsPanelProps) {
  return (
    <div className="bg-white rounded-lg shadow-md p-4 space-y-3">
      <h3 className="text-lg font-bold text-gray-800 border-b pb-2">
        Player Statistics
      </h3>
      
      <div className="text-sm text-gray-600 mb-4">
        🎯 Target Currency: <span className="font-bold">{targetCurrency}</span>
      </div>
      
      <div className="space-y-3">
        {players.map((player) => {
          // Extract values with backwards compatibility
          const playerId = player.uid || (player as any).id;
          const playerName = player.name || player.uid;
          const playerEmoji = player.emoji || '🎮';
          const health = player.values?.health ?? (player as any).health ?? 0;
          const currency = player.values?.money ?? (player as any).currency ?? 0;
          const isActive = player.isActive ?? (health > 0);
          const posX = Array.isArray(player.position) ? player.position[0] : (player.position as any)?.x ?? 0;
          const posY = Array.isArray(player.position) ? player.position[1] : (player.position as any)?.y ?? 0;
          const validityScore = player.validityScore ?? 0;
          const creativityScore = player.creativityScore ?? 0;
          const level = player.level ?? 1;
          const experience = player.experience ?? 0;
          const invalidActions = player.invalid_action_count ?? 0;
          const totalActions = player.total_action_count ?? 0;
          const failureRate = totalActions > 0 ? ((invalidActions / totalActions) * 100).toFixed(1) : '0.0';

          return (
            <div 
              key={playerId}
              className={`border rounded-lg p-3 transition-all ${
                isActive 
                  ? 'bg-white border-gray-300 hover:border-blue-400' 
                  : 'bg-gray-100 border-gray-200 opacity-60'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="text-2xl">{playerEmoji}</span>
                  <div>
                    <div className="font-semibold text-gray-800">{playerName}</div>
                    {!isActive && (
                      <div className="text-xs text-red-600">Eliminated</div>
                    )}
                  </div>
                </div>
                <div className="text-xs text-gray-500">
                  ({posX}, {posY})
                </div>
              </div>
            
              <div className="space-y-2">
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div className="flex items-center gap-1">
                    <span className="text-red-500">❤️</span>
                    <span className="font-medium text-gray-600">{health}</span>
                  </div>

                  <div className="flex items-center gap-1">
                    <span className="text-yellow-500">💰</span>
                    <span className="font-medium text-gray-600">{currency}</span>
                  </div>

                  <div className="flex items-center gap-1">
                    <span className="text-blue-500">⭐</span>
                    <span className="text-xs text-gray-600">Lvl {level} ({experience} XP)</span>
                  </div>

                  <div className="flex items-center gap-1">
                    <span className="text-red-400">❌</span>
                    <span className="text-xs text-gray-600">Fail: {failureRate}%</span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="flex items-center gap-1">
                    <span className="text-green-500">✓</span>
                    <span className="text-gray-600">Valid: {validityScore}</span>
                  </div>

                  <div className="flex items-center gap-1">
                    <span className="text-purple-500">✨</span>
                    <span className="text-gray-600">Creative: {creativityScore}</span>
                  </div>
                </div>
              </div>
            
              {/* Progress bar */}
              <div className="mt-2">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-gradient-to-r from-yellow-400 to-yellow-600 h-2 rounded-full transition-all"
                    style={{ width: `${Math.min((currency / targetCurrency) * 100, 100)}%` }}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
