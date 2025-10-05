'use client';

import { Turn } from '@/types/game';
import { useEffect, useRef } from 'react';

interface TurnTimelineProps {
  turns: Turn[];
  selectedTurnNumber: number;
  onTurnSelect: (turnNumber: number) => void;
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
          const isSelected = turn.turnNumber === selectedTurnNumber;
          
          return (
            <div
              key={turn.turnNumber}
              ref={isSelected ? selectedRef : null}
              onClick={() => onTurnSelect(turn.turnNumber)}
              className={`border-2 rounded-xl p-5 cursor-pointer transition-all ${
                isSelected 
                  ? 'border-blue-500 bg-blue-50 shadow-lg scale-[1.02]' 
                  : 'border-gray-300 hover:border-blue-300 hover:bg-gray-50 hover:shadow-md'
              }`}
            >
              <div className="flex items-center justify-between mb-4">
                <h4 className="text-xl font-bold text-gray-800">
                  Turn {turn.turnNumber + 1}
                </h4>
                {isSelected && (
                  <span className="text-xs bg-blue-500 text-white px-3 py-1 rounded-full font-semibold">
                    👁️ Viewing
                  </span>
                )}
              </div>
              
              <div className="space-y-4">
                {turn.actions.map((action, idx) => (
                  <div 
                    key={idx}
                    className={`border-l-4 pl-4 py-2 rounded-r ${
                      action.isValid 
                        ? 'border-green-500 bg-green-50/50' 
                        : 'border-red-500 bg-red-50/50'
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <div className="font-bold text-gray-800 flex items-center gap-2">
                        <span>{action.playerName}</span>
                        {action.isValid ? (
                          <span className="text-green-600 text-sm">✓ Valid</span>
                        ) : (
                          <span className="text-red-600 text-sm">✗ Invalid</span>
                        )}
                      </div>
                    </div>
                    
                    <div className="text-sm text-gray-700 italic bg-white/70 p-2 rounded mb-2">
                      💬 "{action.actionDeclaration}"
                    </div>
                    
                    <div className="text-sm text-gray-800 bg-white/70 p-2 rounded mb-2">
                      🎲 {action.resolution}
                    </div>
                    
                    <div className="flex flex-wrap gap-3 text-sm">
                      {action.healthChange !== 0 && (
                        <span className={`px-2 py-1 rounded ${
                          action.healthChange > 0 
                            ? 'bg-green-100 text-green-700' 
                            : 'bg-red-100 text-red-700'
                        }`}>
                          ❤️ {action.healthChange > 0 ? '+' : ''}{action.healthChange}
                        </span>
                      )}
                      {action.currencyChange !== 0 && (
                        <span className={`px-2 py-1 rounded ${
                          action.currencyChange > 0 
                            ? 'bg-green-100 text-green-700' 
                            : 'bg-red-100 text-red-700'
                        }`}>
                          💰 {action.currencyChange > 0 ? '+' : ''}{action.currencyChange}
                        </span>
                      )}
                      <span className="px-2 py-1 rounded bg-purple-100 text-purple-700">
                        ✨ Creativity: {action.creativityScore}/10
                      </span>
                      <span className="px-2 py-1 rounded bg-blue-100 text-blue-700">
                        📊 Validity: {action.validityScore}/10
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
