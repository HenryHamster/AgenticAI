'use client';

import { Turn, Player } from '@/types/game';
import { useEffect, useRef } from 'react';

interface TurnTimelineProps {
  turns: Turn[];
  selectedTurnNumber: number;
  onTurnSelect: (turnNumber: number) => void;
}

interface PlayerAction {
  playerId: string;
  playerName: string;
  response: string;
  emoji?: string;
  healthChange: number;
  currencyChange: number;
}

/**
 * Extracts player actions from a turn's player data
 */
function extractPlayerActions(turn: Turn): PlayerAction[] {
  const playerActions: PlayerAction[] = [];

  if (!turn.game_state?.players && !(turn as any).players) {
    return playerActions;
  }

  // Create a map of character states for quick lookup
  const characterStateMap = new Map<string, { healthChange: number; currencyChange: number }>();
  if (turn.game_state?.character_state_change) {
    turn.game_state.character_state_change.forEach((cs) => {
      characterStateMap.set(cs.uid, {
        healthChange: cs.health_change,
        currencyChange: cs.money_change,
      });
    });
  }

  const players = turn.game_state?.players || (turn as any).players || {};
  Object.entries(players).forEach(([playerId, player]: [string, any]) => {
    if (player.responses && player.responses.length > 0) {
      // Get the most recent response for this turn
      const latestResponse = player.responses[player.responses.length - 1];

      // Get actual changes from character_state_change, fallback to 0 if not found
      const changes = characterStateMap.get(playerId) || { healthChange: 0, currencyChange: 0 };

      playerActions.push({
        playerId,
        playerName: player.name || player.uid,
        response: latestResponse,
        emoji: player.emoji || '🧙',
        healthChange: changes.healthChange,
        currencyChange: changes.currencyChange,
      });
    }
  });

  return playerActions;
}

/**
 * Renders a single player action card
 */
function PlayerActionCard({ action }: { action: PlayerAction }) {
  return (
    <div className="border-l-4 pl-4 py-2 rounded-r border-blue-500 bg-blue-50/50">
      <div className="flex items-center gap-2 mb-2">
        <div className="font-bold text-gray-800 flex items-center gap-2">
          {action.emoji && <span>{action.emoji}</span>}
          <span>{action.playerName}</span>
        </div>
      </div>

      <div className="text-sm text-gray-700 italic bg-white/70 p-2 rounded mb-2">
        💬 "{action.response}"
      </div>

      <div className="flex flex-wrap gap-3 text-sm">
        {action.healthChange !== 0 && (
          <span
            className={`px-2 py-1 rounded ${
              action.healthChange > 0
                ? 'bg-green-100 text-green-700'
                : 'bg-red-100 text-red-700'
            }`}
          >
            ❤️ {action.healthChange > 0 ? '+' : ''}{action.healthChange}
          </span>
        )}
        {action.currencyChange !== 0 && (
          <span
            className={`px-2 py-1 rounded ${
              action.currencyChange > 0
                ? 'bg-green-100 text-green-700'
                : 'bg-red-100 text-red-700'
            }`}
          >
            💰 {action.currencyChange > 0 ? '+' : ''}{action.currencyChange}
          </span>
        )}
      </div>
    </div>
  );
}

/**
 * Renders the actions section for a turn
 */
function TurnActions({ turn }: { turn: Turn }) {
  const playerActions = extractPlayerActions(turn);

  if (playerActions.length === 0) {
    return (
      <div className="text-center text-gray-500 py-4">
        No actions recorded for this turn
      </div>
    );
  }

  return (
    <>
      {playerActions.map((action, idx) => (
        <PlayerActionCard key={idx} action={action} />
      ))}
      
      {/* Display narrative result if available */}
      {turn.game_state?.narrative_result && (
        <div className="mt-4 border-l-4 pl-4 py-3 rounded-r border-purple-500 bg-purple-50/50">
          <div className="font-bold text-purple-900 mb-2 flex items-center gap-2">
            <span>🎲</span>
            <span>Dungeon Master's Verdict</span>
          </div>
          <div className="text-sm text-gray-700 bg-white/70 p-3 rounded">
            {turn.game_state.narrative_result}
          </div>
        </div>
      )}
    </>
  );
}

export default function TurnTimeline({ turns, selectedTurnNumber, onTurnSelect }: TurnTimelineProps) {
  const selectedRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to selected turn
  useEffect(() => {
    if (selectedRef.current) {
      selectedRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }, [selectedTurnNumber]);

  return (
    <div className="bg-white rounded-lg shadow-md p-6 h-full overflow-y-auto max-h-[calc(100vh-280px)]">
      <div className="pb-4 mb-4 border-b-2 border-gray-200">
      <h3 className="text-2xl font-bold text-gray-800">
          📜 Turn History
        </h3>
        <p className="text-sm text-gray-500 mt-1">
          {turns.length} turns • Click to view details
        </p>
      </div>
      
      <div className="space-y-5">
        {turns.map((turn) => {
          const isSelected = turn.turn_number === selectedTurnNumber;
          
          return (
            <div
              key={turn.turn_number}
              ref={isSelected ? selectedRef : null}
              onClick={() => onTurnSelect(turn.turn_number)}
              className={`border-2 rounded-xl p-5 cursor-pointer transition-all ${
                isSelected 
                  ? 'border-blue-500 bg-blue-50 shadow-lg scale-[1.02]' 
                  : 'border-gray-300 hover:border-blue-300 hover:bg-gray-50 hover:shadow-md'
              }`}
            >
              <div className="flex items-center justify-between mb-4">
                <h4 className="text-xl font-bold text-gray-800">
                  Turn {turn.turn_number}
                </h4>
                {isSelected && (
                  <span className="text-xs bg-blue-500 text-white px-3 py-1 rounded-full font-semibold">
                    👁️ Viewing
                  </span>
                )}
              </div>
              
              <div className="space-y-4">
                <TurnActions turn={turn} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
