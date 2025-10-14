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
  
  const currentTurn = gameRun.turns.find((t) => t.turnNumber === selectedTurnNumber) || gameRun.turns[0];
  const winner = gameRun.players.find((p) => p.id === gameRun.winnerId);

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
              {new Date(gameRun.startTime).toLocaleString()}
            </p>
          </div>
          
          {winner && (
            <div className="bg-yellow-100 px-4 py-2 rounded-lg">
              <div className="flex items-center gap-2">
                <span className="text-2xl">{winner.emoji}</span>
                <div>
                  <div className="text-xs text-yellow-700">Winner</div>
                  <div className="font-bold text-yellow-900">{winner.name}</div>
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
              boardState={currentTurn.boardState}
              players={currentTurn.playerStates}
            />
          </div>

          {/* Player Stats */}
          <PlayerStatsPanel
            players={currentTurn.playerStates}
            targetCurrency={gameRun.targetCurrency}
          />
        </div>
      </div>
    </>
  );
}
