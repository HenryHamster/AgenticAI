"use client";

import { useEffect, useState } from "react";
import { fetchGameRunsClient } from "@/services/api";
import GameRunCard from "@/components/GameRunCard";
import Link from "next/link";
import { GameRun } from "@/types/game";

export default function Home() {
  const [gameRuns, setGameRuns] = useState<GameRun[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchGameRunsClient()
      .then(setGameRuns)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to gray-100 p-6">
      <div className="max-w-7xl mx-auto">
        <header className="mb-8">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h1 className="text-4xl font-bold text-gray-800 mb-2">
                🎮 Dungeon Master
              </h1>
            </div>
            <Link
              href="/game/new"
              className="group relative px-8 py-3.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 transition-all duration-300 font-semibold shadow-lg hover:shadow-xl hover:scale-105 flex items-center gap-2"
            >
              <span className=" text-white leading-none">+</span>
              <span className="text-white">New Game</span>
            </Link>
          </div>
        </header>
        {loading ? (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <div className="text-6xl mb-4 animate-pulse">⏳</div>
            <h2 className="text-2xl font-semibold text-gray-700 mb-2">
              Loading Games...
            </h2>
          </div>
        ) : gameRuns.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <div className="text-6xl mb-4">🎲</div>
            <h2 className="text-2xl font-semibold text-gray-700 mb-2">
              No Game Runs Yet
            </h2>
            <p className="text-gray-500">
              Game runs will appear here once they are completed.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {gameRuns.map((gameRun) => (
              <GameRunCard key={gameRun.id} gameRun={gameRun} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
