'use client';

import { useState, useEffect, useRef } from 'react';
import GameBoard from '@/components/GameBoard';
import TurnTimeline from '@/components/TurnTimeline';
import PlayerStatsPanel from '@/components/PlayerStatsPanel';
import { GameRun } from '@/types/game';

interface GameDetailClientProps {
  gameRun: GameRun;
}

export default function GameDetailClient({ gameRun: initialGameRun }: GameDetailClientProps) {
  const [selectedTurnIndex, setSelectedTurnIndex] = useState(0);
  const [formattedStartTime, setFormattedStartTime] = useState<string>('');
  const refreshIntervalRef = useRef<NodeJS.Timeout | null>(null);
  
  // Format start time client-side to avoid hydration mismatch
  useEffect(() => {
    setFormattedStartTime(new Date(initialGameRun.startTime).toLocaleString());
  }, [initialGameRun.startTime]);
  
  // Refresh page every 1 second if there are no turns yet
  useEffect(() => {
    const hasNoTurns = !initialGameRun.turns || initialGameRun.turns.length === 0;
    
    if (hasNoTurns) {
      // Set up refresh interval
      refreshIntervalRef.current = setInterval(() => {
        window.location.reload();
      }, 2000); // Refresh every 2 seconds
    }
    
    // Cleanup function
    return () => {
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current);
        refreshIntervalRef.current = null;
      }
    };
  }, [initialGameRun.turns]);
  
  // Safety check for turns
  if (!initialGameRun.turns || initialGameRun.turns.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <div className="text-4xl mb-4">⚠️</div>
        <h2 className="text-xl font-semibold text-gray-700">No turns available</h2>
        <p className="text-gray-500 mt-2">This game has no recorded turns yet. Refreshing page every 2 seconds.</p>
      </div>
    );
  }
  
  const currentTurn = initialGameRun.turns[selectedTurnIndex] || initialGameRun.turns[0];
  
  // Additional safety check
  if (!currentTurn) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <div className="text-4xl mb-4">⚠️</div>
        <h2 className="text-xl font-semibold text-gray-700">Turn not found</h2>
        <p className="text-gray-500 mt-2">Unable to load turn data.</p>
      </div>
    );
  }
  
  // Convert players dictionary to array for easier iteration
  const playersArray = Object.values(initialGameRun.players || {});
  const winner = initialGameRun.winnerId ? initialGameRun.players?.[initialGameRun.winnerId] : null;
  
  // Get status badge styling
  const getStatusBadge = (status?: string) => {
    const statusLower = (status || 'unknown').toLowerCase();
    
    const statusConfig = {
      active: { bg: 'bg-green-100', text: 'text-green-800', dot: 'bg-green-500', label: 'Active' },
      pending: { bg: 'bg-yellow-100', text: 'text-yellow-800', dot: 'bg-yellow-500', label: 'Pending' },
      completed: { bg: 'bg-blue-100', text: 'text-blue-800', dot: 'bg-blue-500', label: 'Completed' },
      cancelled: { bg: 'bg-gray-100', text: 'text-gray-800', dot: 'bg-gray-500', label: 'Cancelled' },
      unknown: { bg: 'bg-gray-100', text: 'text-gray-600', dot: 'bg-gray-400', label: 'Unknown' },
    };
    
    return statusConfig[statusLower as keyof typeof statusConfig] || statusConfig.unknown;
  };
  
  const statusBadge = getStatusBadge(initialGameRun.status);
  
  // Convert tiles array to board state (2D grid) for backwards compatibility
  const getBoardStateFromTiles = (tiles: any): any => {
    if (tiles && Array.isArray(tiles)) {
      // If it's the new tiles array format, we'll pass it directly
      return tiles;
    }
    // Fallback to legacy boardState if available
    return currentTurn.boardState || [];
  };
  
  // Get player states as array from dictionary
  const getPlayerStatesArray = (players: any): any[] => {
    if (players && typeof players === 'object' && !Array.isArray(players)) {
      return Object.values(players);
    }
    // Fallback to legacy playerStates if available
    return currentTurn.playerStates || [];
  };

  return (
    <>
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <h1 className="text-3xl font-bold text-gray-800">
                Game #{initialGameRun.id.slice(0, 8)}
              </h1>
              <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-medium ${statusBadge.bg} ${statusBadge.text}`}>
                <span className={`w-2 h-2 rounded-full ${statusBadge.dot} ${(initialGameRun.status === 'active' || initialGameRun.status === 'pending') ? 'animate-pulse' : ''}`}></span>
                {statusBadge.label}
              </span>
            </div>
            <p className="text-gray-600">
              {formattedStartTime || '...'}
            </p>
          </div>
          
          {winner && (
            <div className="bg-yellow-100 px-4 py-2 rounded-lg">
              <div className="flex items-center gap-2">
                <span className="text-2xl">{winner.emoji || '👑'}</span>
                <div>
                  <div className="text-xs text-yellow-700">Winner</div>
                  <div className="font-bold text-yellow-900">{winner.name || winner.uid}</div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Turn Slider Control */}
      <div className="bg-white rounded-lg shadow-md p-4 mb-6">
        <div className="flex items-center gap-4">
          <button
            onClick={() => setSelectedTurnIndex(Math.max(0, selectedTurnIndex - 1))}
            disabled={selectedTurnIndex === 0}
            className="px-3 py-2 bg-blue-500 text-white rounded-lg disabled:bg-gray-300 disabled:cursor-not-allowed hover:bg-blue-600 transition flex-shrink-0"
          >
            ← Prev
          </button>
          
          <div className="flex-1">
            <div className="flex items-center gap-3">
              <span className="text-sm font-semibold text-gray-700 flex-shrink-0">
                Turn {currentTurn.turnNumber} / {initialGameRun.turns.length}
              </span>
              <input
                type="range"
                min="0"
                max={initialGameRun.turns.length - 1}
                value={selectedTurnIndex}
                onChange={(e) => setSelectedTurnIndex(parseInt(e.target.value))}
                className="flex-1 cursor-pointer"
              />
            </div>
          </div>
          
          <button
            onClick={() => setSelectedTurnIndex(Math.min(initialGameRun.turns.length - 1, selectedTurnIndex + 1))}
            disabled={selectedTurnIndex === initialGameRun.turns.length - 1}
            className="px-3 py-2 bg-blue-500 text-white rounded-lg disabled:bg-gray-300 disabled:cursor-not-allowed hover:bg-blue-600 transition flex-shrink-0"
          >
            Next →
          </button>
        </div>
      </div>

      {/* Two-panel layout: Main (Turn History) + Side (Board & Stats) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Main Panel: Turn History (wider) */}
        <div className="lg:col-span-8">
          <TurnTimeline
            turns={initialGameRun.turns}
            selectedTurnNumber={currentTurn.turnNumber}
            onTurnSelect={(turnNumber) => {
              const index = initialGameRun.turns.findIndex(t => t.turnNumber === turnNumber);
              if (index !== -1) setSelectedTurnIndex(index);
            }}
          />
        </div>

        {/* Side Panel: Game Board + Player Stats */}
        <div className="lg:col-span-4 space-y-6">
          {/* Game Board */}
          <div className="bg-white rounded-lg shadow-md p-4">
            <div className="mb-3 text-center">
              <h2 className="text-lg font-bold text-gray-800">
                Game Board
              </h2>
              <p className="text-xs text-gray-500">
                Turn {currentTurn.turnNumber}
              </p>
            </div>
            
            <GameBoard
              boardState={getBoardStateFromTiles(currentTurn.tiles)}
              players={getPlayerStatesArray(currentTurn.players)}
              boardSize={currentTurn.board_size || initialGameRun.board_size}
            />
          </div>

          {/* Player Stats */}
          <PlayerStatsPanel
            players={getPlayerStatesArray(currentTurn.players)}
            targetCurrency={initialGameRun.targetCurrency}
          />
        </div>
      </div>
    </>
  );
}
