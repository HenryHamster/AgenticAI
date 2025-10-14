"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { PlayerSetup, GameCreationRequest } from "@/types/game";
// import { createGame } from "@/services/api";

// Random name pool for players
const PLAYER_NAMES = [
  "Aria",
  "Borin",
  "Cedric",
  "Diana",
  "Elden",
  "Fiona",
  "Gideon",
  "Helena",
  "Ivan",
  "Jade",
  "Kael",
  "Luna",
  "Magnus",
  "Nora",
  "Orin",
  "Petra",
  "Quinn",
  "Rowan",
  "Sasha",
  "Thorne",
  "Uma",
  "Victor",
  "Willow",
  "Xander",
  "Yara",
  "Zane",
  "Astrid",
  "Bjorn",
  "Cora",
  "Drake",
  "Elara",
  "Finn",
];

const getRandomName = (): string => {
  return PLAYER_NAMES[Math.floor(Math.random() * PLAYER_NAMES.length)];
};

export default function NewGamePage() {
  const router = useRouter();
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [numberOfPlayers, setNumberOfPlayers] = useState(2);
  const [maxTurns, setMaxTurns] = useState<number | "until_win">("until_win");
  const [currencyGoal, setCurrencyGoal] = useState(50);
  const [players, setPlayers] = useState<PlayerSetup[]>([
    {
      name: getRandomName(),
      class: "human",
      startingCurrency: 0,
      startingHealth: 100,
      startingPosition: "random",
      agentPrompt: "",
    },
    {
      name: getRandomName(),
      class: "human",
      startingCurrency: 0,
      startingHealth: 100,
      startingPosition: "random",
      agentPrompt: "",
    },
  ]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Update number of players
  const handleNumberOfPlayersChange = (num: number) => {
    setNumberOfPlayers(num);
    const newPlayers = [...players];

    if (num > players.length) {
      // Add new players
      for (let i = players.length; i < num; i++) {
        newPlayers.push({
          name: getRandomName(),
          class: "human",
          startingCurrency: 0,
          startingHealth: 100,
          startingPosition: "random",
          agentPrompt: "",
        });
      }
    } else {
      // Remove excess players
      newPlayers.splice(num);
    }

    setPlayers(newPlayers);
  };

  // Update player field
  const updatePlayer = (
    index: number,
    field: keyof PlayerSetup,
    value: any
  ) => {
    const newPlayers = [...players];
    newPlayers[index] = { ...newPlayers[index], [field]: value };
    setPlayers(newPlayers);
  };

  // Submit form
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    const gameRequest: GameCreationRequest = {
      numberOfPlayers,
      players,
      maxTurns,
      currencyGoal,
    };

    try {
      // todo: implement create game
      const gameId = '1231231123'
      router.push(`/game/${gameId}`);
    } catch (error) {
      console.error("Failed to create game:", error);
      alert("Failed to create game. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 mb-4"
          >
            ← Back to Home
          </Link>

          <h1 className="text-3xl font-bold text-gray-800">
            Create New Game
          </h1>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Game Settings */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-800">
                Game Settings
              </h2>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={showAdvanced}
                  onChange={(e) => setShowAdvanced(e.target.checked)}
                  className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                />
                <span className="text-sm font-medium text-gray-700">
                  Advanced Options
                </span>
              </label>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Number of Players
                </label>
                <input
                  type="number"
                  min="1"
                  max="10"
                  value={numberOfPlayers}
                  onChange={(e) =>
                    handleNumberOfPlayersChange(parseInt(e.target.value))
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>

              {showAdvanced && (
                <>
                  <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Max Turns
                </label>
                <select
                  value={maxTurns}
                  onChange={(e) =>
                    setMaxTurns(
                      e.target.value === "until_win"
                        ? "until_win"
                        : parseInt(e.target.value)
                    )
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="until_win">Until Win Condition Met</option>
                  {[...Array(50)].map((_, i) => (
                    <option key={i + 1} value={i + 1}>
                      {i + 1}
                    </option>
                  ))}
                </select>
              </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Currency Goal
                    </label>
                    <input
                      type="number"
                      min="1"
                      value={currencyGoal}
                      onChange={(e) => setCurrencyGoal(parseInt(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      required
                    />
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Player Configuration */}
          {showAdvanced && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-bold text-gray-800 mb-4">
                Player Configuration
              </h2>

            <div className="space-y-6">
              {players.map((player, index) => (
                <div
                  key={index}
                  className="border-2 border-gray-200 rounded-lg p-4"
                >
                  <h3 className="font-semibold text-gray-700 mb-3">
                    Player {index + 1}
                  </h3>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Name
                      </label>
                      <input
                        type="text"
                        value={player.name}
                        onChange={(e) =>
                          updatePlayer(index, "name", e.target.value)
                        }
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Class
                      </label>
                      <select
                        value={player.class}
                        onChange={(e) =>
                          updatePlayer(index, "class", e.target.value)
                        }
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option value="human">Human</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Starting Currency
                      </label>
                      <input
                        type="number"
                        min="0"
                        value={player.startingCurrency}
                        onChange={(e) =>
                          updatePlayer(
                            index,
                            "startingCurrency",
                            parseInt(e.target.value)
                          )
                        }
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Starting Health
                      </label>
                      <input
                        type="number"
                        min="1"
                        value={player.startingHealth}
                        onChange={(e) =>
                          updatePlayer(
                            index,
                            "startingHealth",
                            parseInt(e.target.value)
                          )
                        }
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        required
                      />
                    </div>

                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Starting Position
                      </label>
                      <select
                        value={
                          player.startingPosition === "random"
                            ? "random"
                            : "custom"
                        }
                        onChange={(e) =>
                          updatePlayer(
                            index,
                            "startingPosition",
                            e.target.value === "random"
                              ? "random"
                              : { x: 0, y: 0 }
                          )
                        }
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option value="random">Random</option>
                        <option value="custom">Custom</option>
                      </select>
                    </div>

                    {player.startingPosition !== "random" && (
                      <>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            X Coordinate
                          </label>
                          <input
                            type="number"
                            min="0"
                            value={
                              typeof player.startingPosition === "object"
                                ? player.startingPosition.x
                                : 0
                            }
                            onChange={(e) =>
                              updatePlayer(index, "startingPosition", {
                                x: parseInt(e.target.value),
                                y:
                                  typeof player.startingPosition === "object"
                                    ? player.startingPosition.y
                                    : 0,
                              })
                            }
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            required
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Y Coordinate
                          </label>
                          <input
                            type="number"
                            min="0"
                            value={
                              typeof player.startingPosition === "object"
                                ? player.startingPosition.y
                                : 0
                            }
                            onChange={(e) =>
                              updatePlayer(index, "startingPosition", {
                                x:
                                  typeof player.startingPosition === "object"
                                    ? player.startingPosition.x
                                    : 0,
                                y: parseInt(e.target.value),
                              })
                            }
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            required
                          />
                        </div>
                      </>
                    )}

                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Agent Prompt
                      </label>
                      <textarea
                        value={player.agentPrompt}
                        onChange={(e) =>
                          updatePlayer(index, "agentPrompt", e.target.value)
                        }
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        rows={3}
                        placeholder="Enter instructions for the AI agent..."
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
            </div>
          )}

          {/* Submit Button */}
          <div className="flex justify-end gap-4">
            <Link
              href="/"
              className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition font-semibold"
            >
              Cancel
            </Link>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-semibold shadow-md disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {isSubmitting ? "Creating..." : "Create Game"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
