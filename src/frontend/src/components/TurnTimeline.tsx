'use client';

import { Turn } from '@/types/game';

interface TurnTimelineProps {
  turns: Turn[];
  selectedTurnNumber: number;
  onTurnSelect: (turnNumber: number) => void;
}

export default function TurnTimeline({ turns, selectedTurnNumber, onTurnSelect }: TurnTimelineProps) {
  return (
    <div className="bg-white rounded-lg shadow-md p-4 h-full overflow-y-auto">
      <h3 className="text-lg font-bold text-gray-800 border-b pb-2 mb-4 sticky top-0 bg-white">
        Turn History
      </h3>
      
      <div className="space-y-4">
        {turns.map((turn) => {
          const isSelected = turn.turnNumber === selectedTurnNumber;
          
          return (
            <div
              key={turn.turnNumber}
              onClick={() => onTurnSelect(turn.turnNumber)}
              className={`border rounded-lg p-3 cursor-pointer transition-all ${
                isSelected 
                  ? 'border-blue-500 bg-blue-50 shadow-md' 
                  : 'border-gray-300 hover:border-blue-300 hover:bg-gray-50'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-semibold text-gray-800">
                  Turn {turn.turnNumber}
                </h4>
                {isSelected && (
                  <span className="text-xs bg-blue-500 text-white px-2 py-1 rounded">
                    Viewing
                  </span>
                )}
              </div>
              
              <div className="space-y-2">
                {turn.actions.map((action, idx) => (
                  <div 
                    key={idx}
                    className={`text-sm border-l-2 pl-2 ${
                      action.isValid ? 'border-green-500' : 'border-red-500'
                    }`}
                  >
                    <div className="font-medium text-gray-700 flex items-center gap-2">
                      <span>{action.playerName}</span>
                      {!action.isValid && <span className="text-red-500 text-xs">✗</span>}
                      {action.isValid && <span className="text-green-500 text-xs">✓</span>}
                    </div>
                    
                    <div className="text-xs text-gray-600 italic mt-1">
                      "{action.actionDeclaration}"
                    </div>
                    
                    <div className="text-xs text-gray-700 mt-1">
                      {action.resolution}
                    </div>
                    
                    <div className="flex gap-3 mt-1 text-xs">
                      {action.healthChange !== 0 && (
                        <span className={action.healthChange > 0 ? 'text-green-600' : 'text-red-600'}>
                          ❤️ {action.healthChange > 0 ? '+' : ''}{action.healthChange}
                        </span>
                      )}
                      {action.currencyChange !== 0 && (
                        <span className={action.currencyChange > 0 ? 'text-green-600' : 'text-red-600'}>
                          💰 {action.currencyChange > 0 ? '+' : ''}{action.currencyChange}
                        </span>
                      )}
                      <span className="text-purple-600">
                        ✨ Creativity: {action.creativityScore}
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
