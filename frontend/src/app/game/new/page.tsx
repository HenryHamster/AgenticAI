"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { PlayerSetup, GameCreationRequest } from "@/types/game";
import { createGame } from "@/services/api";

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
  const [worldSize, setWorldSize] = useState(1); // Default world_size = 1 (creates 3x3 board)
  const [players, setPlayers] = useState<PlayerSetup[]>([
    {
      name: getRandomName(),
      class: "human",
      startingCurrency: 0,
      startingHealth: 100,
      startingPosition: "random",
      agentPrompt: "",
      characterClass: "Warrior",
    },
    {
      name: getRandomName(),
      class: "human",
      startingCurrency: 0,
      startingHealth: 100,
      startingPosition: "random",
      agentPrompt: "",
      characterClass: "Warrior",
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
          characterClass: "Warrior",
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
      worldSize,
    };

    try {
      console.log("trying to create game:", JSON.stringify(gameRequest, null ,2));
      const gameId = await createGame(gameRequest);
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
                      Board Size
                    </label>
                    <select
                      value={worldSize}
                      onChange={(e) => setWorldSize(parseInt(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="1">1x1 (Smallest)</option>
                      <option value="1">3×3 (Small)</option>
                      <option value="2">5×5</option>
                      <option value="3">7×7</option>
                      <option value="4">9×9</option>
                      <option value="5">11×11 (Default)</option>
                      <option value="6">13×13</option>
                      <option value="7">15×15</option>
                      <option value="8">17×17</option>
                      <option value="9">19×19</option>
                      <option value="10">21×21 (Large)</option>
                    </select>
                    <p className="text-xs text-gray-500 mt-1">
                      World size determines the game board dimensions
                    </p>
                  </div>

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
                        Character Class
                      </label>
                      <select
                        value={player.characterClass || ""}
                        onChange={(e) =>
                          updatePlayer(index, "characterClass", e.target.value || undefined)
                        }
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option value="Warrior">Warrior</option>
                        <option value="Mage">Mage</option>
                        <option value="Rogue">Rogue</option>
                      </select>
                      <p className="text-xs text-gray-500 mt-1">
                        DnD-style progression with skills and leveling
                      </p>
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
                              : [0, 0]
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
                              Array.isArray(player.startingPosition)
                                ? player.startingPosition[0]
                                : 0
                            }
                            onChange={(e) =>
                              updatePlayer(index, "startingPosition", [
                                parseInt(e.target.value),
                                Array.isArray(player.startingPosition)
                                  ? player.startingPosition[1]
                                  : 0,
                              ])
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
                              Array.isArray(player.startingPosition)
                                ? player.startingPosition[1]
                                : 0
                            }
                            onChange={(e) =>
                              updatePlayer(index, "startingPosition", [
                                Array.isArray(player.startingPosition)
                                  ? player.startingPosition[0]
                                  : 0,
                                parseInt(e.target.value),
                              ])
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
