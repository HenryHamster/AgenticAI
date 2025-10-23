"use client";

import { useState } from 'react';

interface EvaluationModalProps {
  isOpen: boolean;
  onClose: () => void;
  evaluationResults: any;
  gameId: string;
}

export default function EvaluationModal({ isOpen, onClose, evaluationResults, gameId }: EvaluationModalProps) {
  if (!isOpen) return null;

  // Helper function to get score color based on value
  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600 bg-green-100';
    if (score >= 0.6) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  // Helper function to format score as percentage
  const formatScore = (score: number) => {
    return `${Math.round(score * 100)}%`;
  };

  // Render individual evaluation item
  const renderEvaluationItem = (item: any, index: number) => {
    if (!item) return null;

    return (
      <div key={index} className="bg-white rounded-lg shadow-md p-4 mb-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold text-gray-800">
            Turn {item.turn_number || index + 1}
          </h3>
          <div className="flex gap-2">
            {item.turn_stats?.average_score !== undefined && (
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getScoreColor(item.turn_stats.average_score)}`}>
                Avg Score: {formatScore(item.turn_stats.average_score)}
              </span>
            )}
          </div>
        </div>

        {/* Player Evaluations */}
        {item.player_evaluations && (
          <div className="mb-4">
            <h4 className="text-md font-semibold text-gray-700 mb-2">Player Evaluations</h4>
            <div className="space-y-3">
              {Object.entries(item.player_evaluations).map(([playerName, playerData]: [string, any]) => (
                <div key={playerName} className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <span className="font-semibold text-gray-800 text-lg">
                      {playerName}
                    </span>
                    <div className="flex gap-2">
                      {playerData.evaluation?.score !== undefined && (
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${getScoreColor(playerData.evaluation.score)}`}>
                          Overall: {formatScore(playerData.evaluation.score)}
                        </span>
                      )}
                    </div>
                  </div>
                  
                  {/* Player Response */}
                  {playerData.response && (
                    <div className="mb-3">
                      <p className="text-sm font-medium text-gray-700 mb-1">Response:</p>
                      <p className="text-sm text-gray-600 bg-white p-3 rounded border">
                        {playerData.response}
                      </p>
                    </div>
                  )}

                  {/* Detailed Evaluation Metrics */}
                  {playerData.evaluation && (
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                      {playerData.evaluation.appropriateness !== undefined && (
                        <div className="bg-blue-50 rounded-lg p-2">
                          <div className="text-xs font-medium text-blue-800">Appropriateness</div>
                          <div className={`text-lg font-bold ${getScoreColor(playerData.evaluation.appropriateness)}`}>
                            {formatScore(playerData.evaluation.appropriateness)}
                          </div>
                        </div>
                      )}
                      {playerData.evaluation.completeness !== undefined && (
                        <div className="bg-green-50 rounded-lg p-2">
                          <div className="text-xs font-medium text-green-800">Completeness</div>
                          <div className={`text-lg font-bold ${getScoreColor(playerData.evaluation.completeness)}`}>
                            {formatScore(playerData.evaluation.completeness)}
                          </div>
                        </div>
                      )}
                      {playerData.evaluation.clarity !== undefined && (
                        <div className="bg-purple-50 rounded-lg p-2">
                          <div className="text-xs font-medium text-purple-800">Clarity</div>
                          <div className={`text-lg font-bold ${getScoreColor(playerData.evaluation.clarity)}`}>
                            {formatScore(playerData.evaluation.clarity)}
                          </div>
                        </div>
                      )}
                      {playerData.evaluation.creativity !== undefined && (
                        <div className="bg-yellow-50 rounded-lg p-2">
                          <div className="text-xs font-medium text-yellow-800">Creativity</div>
                          <div className={`text-lg font-bold ${getScoreColor(playerData.evaluation.creativity)}`}>
                            {formatScore(playerData.evaluation.creativity)}
                          </div>
                        </div>
                      )}
                      {playerData.evaluation.action_validity !== undefined && (
                        <div className="bg-red-50 rounded-lg p-2">
                          <div className="text-xs font-medium text-red-800">Action Validity</div>
                          <div className={`text-lg font-bold ${getScoreColor(playerData.evaluation.action_validity)}`}>
                            {formatScore(playerData.evaluation.action_validity)}
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Reasoning */}
                  {playerData.evaluation?.reasoning && (
                    <div className="mt-3">
                      <p className="text-sm font-medium text-gray-700 mb-1">Reasoning:</p>
                      <p className="text-sm text-gray-600 bg-white p-3 rounded border">
                        {playerData.evaluation.reasoning}
                      </p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Turn Statistics */}
        {item.turn_stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="bg-blue-50 rounded-lg p-3">
              <div className="text-sm font-medium text-blue-800">Average Score</div>
              <div className={`text-xl font-bold ${getScoreColor(item.turn_stats.average_score)}`}>
                {formatScore(item.turn_stats.average_score)}
              </div>
            </div>
            <div className="bg-green-50 rounded-lg p-3">
              <div className="text-sm font-medium text-green-800">Min Score</div>
              <div className={`text-xl font-bold ${getScoreColor(item.turn_stats.min_score)}`}>
                {formatScore(item.turn_stats.min_score)}
              </div>
            </div>
            <div className="bg-purple-50 rounded-lg p-3">
              <div className="text-sm font-medium text-purple-800">Max Score</div>
              <div className={`text-xl font-bold ${getScoreColor(item.turn_stats.max_score)}`}>
                {formatScore(item.turn_stats.max_score)}
              </div>
            </div>
            <div className="bg-yellow-50 rounded-lg p-3">
              <div className="text-sm font-medium text-yellow-800">Players</div>
              <div className="text-xl font-bold text-yellow-600">
                {item.turn_stats.total_players}
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  // Calculate overall game metrics
  const calculateOverallMetrics = () => {
    if (!evaluationResults) return null;

    // Handle the actual data structure
    if (evaluationResults.overall_stats) {
      return {
        avgScore: evaluationResults.overall_stats.overall_average_score,
        totalResponses: evaluationResults.overall_stats.total_responses_evaluated,
        totalTurns: evaluationResults.overall_stats.total_turns,
        scoreTrend: evaluationResults.overall_stats.score_trend
      };
    }

    // Fallback for array format
    if (Array.isArray(evaluationResults)) {
      const allScores = evaluationResults
        .flatMap(item => 
          item.player_evaluations ? 
            Object.values(item.player_evaluations).map((player: any) => player.evaluation?.score).filter(Boolean) :
            []
        );

      const avgScore = allScores.length > 0 
        ? allScores.reduce((sum, score) => sum + score, 0) / allScores.length 
        : 0;

      return { avgScore, totalResponses: allScores.length };
    }

    return null;
  };

  const overallMetrics = calculateOverallMetrics();

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-6xl w-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div>
            <h2 className="text-2xl font-bold text-gray-800 mb-1">
              📊 Game Evaluation Results
            </h2>
            <p className="text-sm text-gray-600">
              Game ID: <span className="font-mono bg-gray-100 px-2 py-1 rounded">{gameId}</span>
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl font-bold"
          >
            ×
          </button>
        </div>
        
        {/* Overall Metrics */}
        {overallMetrics && (
          <div className="p-6 border-b bg-gradient-to-r from-blue-50 to-purple-50">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Overall Game Performance</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-white rounded-lg p-4 shadow-sm">
                <div className="text-sm font-medium text-blue-800 mb-2">Average Score</div>
                <div className={`text-3xl font-bold ${getScoreColor(overallMetrics.avgScore)}`}>
                  {formatScore(overallMetrics.avgScore)}
                </div>
              </div>
              <div className="bg-white rounded-lg p-4 shadow-sm">
                <div className="text-sm font-medium text-green-800 mb-2">Total Responses</div>
                <div className="text-3xl font-bold text-green-600">
                  {overallMetrics.totalResponses}
                </div>
              </div>
              <div className="bg-white rounded-lg p-4 shadow-sm">
                <div className="text-sm font-medium text-purple-800 mb-2">Total Turns</div>
                <div className="text-3xl font-bold text-purple-600">
                  {overallMetrics.totalTurns || evaluationResults.evaluations?.length || 0}
                </div>
              </div>
              <div className="bg-white rounded-lg p-4 shadow-sm">
                <div className="text-sm font-medium text-yellow-800 mb-2">Game ID</div>
                <div className="text-lg font-bold text-yellow-600 font-mono">
                  {evaluationResults.game_id?.slice(0, 8) || 'N/A'}
                </div>
              </div>
            </div>
          </div>
        )}
        
        {/* Content */}
        <div className="flex-1 overflow-auto p-6">
          {evaluationResults?.evaluations && Array.isArray(evaluationResults.evaluations) ? (
            <div className="space-y-4">
              {evaluationResults.evaluations.map((item: any, index: number) => renderEvaluationItem(item, index))}
            </div>
          ) : evaluationResults && Array.isArray(evaluationResults) ? (
            <div className="space-y-4">
              {evaluationResults.map((item: any, index: number) => renderEvaluationItem(item, index))}
            </div>
          ) : (
            <div className="bg-gray-50 rounded-lg p-8 text-center">
              <div className="text-4xl mb-4">📊</div>
              <h3 className="text-lg font-semibold text-gray-700 mb-2">No Evaluation Data</h3>
              <p className="text-gray-500">The evaluation results are not in the expected format.</p>
              <details className="mt-4 text-left">
                <summary className="cursor-pointer text-sm text-gray-600 hover:text-gray-800">
                  View Raw Data
                </summary>
                <pre className="mt-2 text-xs bg-white p-4 rounded border overflow-auto max-h-40">
                  {JSON.stringify(evaluationResults, null, 2)}
                </pre>
              </details>
            </div>
          )}
        </div>
        
        {/* Footer */}
        <div className="p-6 border-t bg-gray-50 rounded-b-lg">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
