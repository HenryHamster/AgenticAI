'use client';

import { use, useState } from 'react';
import { fetchGameRunById } from '@/services/api';
import GameBoard from '@/components/GameBoard';
import TurnTimeline from '@/components/TurnTimeline';
import PlayerStatsPanel from '@/components/PlayerStatsPanel';
import Link from 'next/link';
import { GameRun } from '@/types/game';
import mockGameDataJson from '@/scripts/mockGameData.json';

interface PageProps {
  params: Promise<{ id: string }>;
}

export default function GameDetailPage({ params }: PageProps) {
  const { id } = use(params);
  
  // In a real app, this would be fetched from the API
  // For now, we'll use a mock loading state
  const [selectedTurnNumber, setSelectedTurnNumber] = useState(0);
  
  // TODO: Fetch game data
  // const gameRun = await fetchGameRunById(id);
  
  // Type assert the imported JSON to match our TypeScript types
  const mockGameData = mockGameDataJson as GameRun[];
  
  // Mock empty state for now
  const gameRun = mockGameData.find((g: GameRun) => g.id === id);

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

  const currentTurn = gameRun.turns.find((t) => t.turnNumber === selectedTurnNumber) || gameRun.turns[0];
  const winner = gameRun.players.find((p) => p.id === gameRun.winnerId);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <Link 
            href="/" 
            className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 mb-4"
          >
            ← Back to Game Runs
          </Link>
          
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
      </div>
    </div>
  );
}
