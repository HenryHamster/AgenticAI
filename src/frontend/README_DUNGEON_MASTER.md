# Dungeon Master Frontend

A Next.js-based frontend for viewing Dungeon Master game runs and history.

## 🎯 Overview

This application displays:
- **Game Runs List**: All completed game sessions
- **Game Detail View**: Interactive turn-by-turn playback with:
  - 10x10 tile-based game board with terrain and player emojis
  - Turn timeline with action declarations and resolutions
  - Player statistics panel with health, currency, and scores

## 📁 Project Structure

```
src/frontend/src/
├── app/
│   ├── page.tsx                    # Game runs list (home page)
│   └── game/[id]/page.tsx          # Game detail view
├── components/
│   ├── GameRunCard.tsx             # Card for game run preview
│   ├── GameBoard.tsx               # 10x10 tile grid display
│   ├── TileCell.tsx                # Individual tile component
│   ├── TurnTimeline.tsx            # Turn history sidebar
│   └── PlayerStatsPanel.tsx        # Player stats display
├── services/
│   └── api.ts                      # API wrapper functions (placeholders)
└── types/
    └── game.ts                     # TypeScript interfaces
```

## 🚀 Getting Started

### Prerequisites
- Node.js 20+
- npm or yarn

### Installation

```bash
cd src/frontend
npm install
```

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the application.

## 📊 Data Structure

### Key Types

```typescript
interface GameRun {
  id: string;
  startTime: string;
  endTime: string;
  winnerId: string | null;
  players: Player[];
  turns: Turn[];
  targetCurrency: number;
  initialBoardState: Tile[][];
}

interface Turn {
  turnNumber: number;
  actions: PlayerAction[];
  boardState: Tile[][];
  playerStates: Player[];
}

interface Player {
  id: string;
  name: string;
  emoji: string;
  health: number;
  currency: number;
  position: { x: number; y: number };
  validityScore: number;
  creativityScore: number;
  isActive: boolean;
}
```

See `src/types/game.ts` for complete type definitions.

## 🎲 Mock Data Generation

The application currently uses **auto-generated mock data** from `src/scripts/generateMockData.ts`.

### Features
- ✅ Automatically generates 3 game runs on startup
- ✅ 2-4 players per game with unique emojis and names
- ✅ Realistic terrain distribution (mountains, forests, deserts, oceans, plains)
- ✅ Varied action types: mining, trading, combat, exploration, movement, creative
- ✅ Dynamic player actions based on terrain type
- ✅ Valid/invalid action mechanics with consequences
- ✅ Player health/currency tracking
- ✅ Win conditions and player elimination

### Generate Custom Mock Data

To generate a different number of games, modify `src/scripts/generateMockData.ts`:

```typescript
// Change the number of games (default: 3)
export const mockGameRuns = generateMultipleGameRuns(5);
```

### Save Mock Data to JSON File

Generate and save mock data to a JSON file:

```bash
npx tsx src/scripts/generateAndSave.ts [number_of_games]
```

Example:
```bash
npx tsx src/scripts/generateAndSave.ts 5  # Generate 5 game runs
```

This creates `src/scripts/mockGameData.json` which you can inspect or use elsewhere.

## 🔌 API Integration

### Current State
The API wrapper functions in `src/services/api.ts` currently return **generated mock data**.

### To Connect Real Backend

Replace the mock data imports in `src/services/api.ts`:

```typescript
// Remove this line:
import { mockGameRuns } from '@/scripts/generateMockData';

// Update the functions:
export async function fetchGameRuns(): Promise<GameRun[]> {
  const response = await fetch('http://your-backend-url/api/game-runs');
  return response.json();
}

export async function fetchGameRunById(id: string): Promise<GameRun | null> {
  const response = await fetch(`http://your-backend-url/api/game-runs/${id}`);
  return response.json();
}
```

### Expected API Endpoints

1. **GET /api/game-runs** - Returns array of all game runs
2. **GET /api/game-runs/:id** - Returns single game run with full history

## 🎨 Features

### Game Runs List
- Grid layout of game run cards
- Shows game metadata: players, turns, duration, winner
- Click to view details

### Game Detail View
- **Turn Timeline** (left panel): Scrollable list of all turns with action details
- **Game Board** (center): Interactive 10x10 grid showing current turn state
- **Player Stats** (right panel): Real-time stats for all players
- **Turn Navigation**: Previous/Next buttons and timeline selection

### Game Board
- Hover over tiles to see descriptions
- Terrain represented by emojis (🏔️ mountain, 🌲 forest, 🏜️ desert, 🌊 ocean)
- Player emojis appear on tiles with subtle animation
- Coordinate labels for reference

## 🎮 Game Rules (Frontend Context)

- **Win Condition**: First player to reach target currency
- **Board**: 10x10 grid with varied terrain
- **Players**: Start with health and currency, positioned on board
- **Turns**: Players declare actions, game master resolves
- **Scoring**: Validity, creativity, and progress tracked per action

## ⚠️ Known Issues

### TypeScript Warnings
The game detail page shows TypeScript errors because `gameRun` is initially `null`. These will resolve once mock/real data is provided.

### CSS Warning
The `@theme` rule warning is expected with Tailwind CSS v4 and can be ignored.

## 🔧 Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4
- **React**: v19

## 🚧 Next Steps

1. **Add Mock Data**: Create realistic game scenarios for testing
2. **Connect Backend**: Implement real API calls
3. **Add Loading States**: Show spinners while fetching data
4. **Error Handling**: Display user-friendly error messages
5. **Enhanced Animations**: Add turn transition effects
6. **Mobile Optimization**: Improve responsive design for smaller screens
7. **Accessibility**: Add ARIA labels and keyboard navigation

## 📚 Development Notes

### Adding New Terrain Types
Update `TerrainType` in `src/types/game.ts` and add emoji mappings.

### Customizing Player Display
Modify `PlayerStatsPanel.tsx` to show additional metrics.

### Board Size
Currently hardcoded to 10x10. To make dynamic, update `GameBoard.tsx` grid columns.

## 📄 License

Part of the AgenticAI Dungeon Master project.
