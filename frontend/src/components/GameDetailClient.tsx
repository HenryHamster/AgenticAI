'use client';

import { useState } from 'react';
import GameBoard from '@/components/GameBoard';
import TurnTimeline from '@/components/TurnTimeline';
import PlayerStatsPanel from '@/components/PlayerStatsPanel';
import { GameRun } from '@/types/game';

interface GameDetailClientProps {
  gameRun: GameRun;
}

export default function GameDetailClient({ gameRun }: GameDetailClientProps) {
  const [selectedTurnNumber, setSelectedTurnNumber] = useState(0);
  
  // Safety check for turns
  if (!gameRun.turns || gameRun.turns.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <div className="text-4xl mb-4">⚠️</div>
        <h2 className="text-xl font-semibold text-gray-700">No turns available</h2>
        <p className="text-gray-500 mt-2">This game has no recorded turns yet.</p>
      </div>
    );
  }
  
  const currentTurn = gameRun.turns.find((t) => t.turnNumber === selectedTurnNumber) || gameRun.turns[0];
  
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
  const playersArray = Object.values(gameRun.players || {});
  const winner = gameRun.winnerId ? gameRun.players?.[gameRun.winnerId] : null;
  
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
            <h1 className="text-3xl font-bold text-gray-800 mb-1">
              Game #{gameRun.id.slice(0, 8)}
            </h1>
            <p className="text-gray-600">
              {new Date(gameRun.created_at).toLocaleString()}
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
            onClick={() => setSelectedTurnNumber(Math.max(0, selectedTurnNumber - 1))}
            disabled={selectedTurnNumber === 0}
            className="px-3 py-2 bg-blue-500 text-white rounded-lg disabled:bg-gray-300 disabled:cursor-not-allowed hover:bg-blue-600 transition flex-shrink-0"
          >
            ← Prev
          </button>
          
          <div className="flex-1">
            <div className="flex items-center gap-3">
              <span className="text-sm font-semibold text-gray-700 flex-shrink-0">
                Turn {selectedTurnNumber + 1} / {gameRun.turns.length}
              </span>
              <input
                type="range"
                min="0"
                max={gameRun.turns.length - 1}
                value={selectedTurnNumber}
                onChange={(e) => setSelectedTurnNumber(parseInt(e.target.value))}
                className="flex-1 cursor-pointer"
              />
            </div>
          </div>
          
          <button
            onClick={() => setSelectedTurnNumber(Math.min(gameRun.turns.length - 1, selectedTurnNumber + 1))}
            disabled={selectedTurnNumber === gameRun.turns.length - 1}
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
            turns={gameRun.turns}
            selectedTurnNumber={selectedTurnNumber}
            onTurnSelect={setSelectedTurnNumber}
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
                Turn {selectedTurnNumber + 1}
              </p>
            </div>
            
            <GameBoard
              boardState={getBoardStateFromTiles(currentTurn.tiles)}
              players={getPlayerStatesArray(currentTurn.players)}
              boardSize={currentTurn.board_size || gameRun.board_size}
            />
          </div>

          {/* Player Stats */}
          <PlayerStatsPanel
            players={getPlayerStatesArray(currentTurn.players)}
            targetCurrency={gameRun.targetCurrency}
          />
        </div>
      </div>
    </>
  );
}
