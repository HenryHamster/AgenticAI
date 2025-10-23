"use client";

import { useState } from 'react';
import { evaluateGameClient } from '@/services/api';

interface EvaluationButtonProps {
  gameId: string;
  onEvaluationComplete: (results: any) => void;
}

export default function EvaluationButton({ gameId, onEvaluationComplete }: EvaluationButtonProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleEvaluate = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const results = await evaluateGameClient(gameId);
      onEvaluationComplete(results);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to evaluate game');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center gap-2">
      <button
        onClick={handleEvaluate}
        disabled={isLoading}
        className="px-4 py-2 bg-purple-600 text-white rounded-lg disabled:bg-gray-400 disabled:cursor-not-allowed hover:bg-purple-700 transition-colors flex items-center gap-2"
      >
        {isLoading ? (
          <>
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            Evaluating...
          </>
        ) : (
          <>
            <span>📊</span>
            Evaluate Actions
          </>
        )}
      </button>
      
      {error && (
        <div className="text-red-600 text-sm text-center max-w-xs">
          {error}
        </div>
      )}
    </div>
  );
}
