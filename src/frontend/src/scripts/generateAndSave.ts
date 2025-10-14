/**
 * Standalone script to generate mock game data and save to file
 * Run with: npx tsx src/scripts/generateAndSave.ts
 */

import { writeFileSync } from 'fs';
import { join } from 'path';
import { generateMultipleGameRuns } from './generateMockData';

const numGames = process.argv[2] ? parseInt(process.argv[2]) : 3;

console.log(`🎲 Generating ${numGames} mock game runs...`);

const gameRuns = generateMultipleGameRuns(numGames);

console.log(`✅ Generated ${gameRuns.length} game runs`);

gameRuns.forEach((game, idx) => {
  console.log(`   Game ${idx + 1}: ${game.players.length} players, ${game.turns.length} turns, winner: ${game.winnerId || 'none'}`);
});

// Save to JSON file
const outputPath = join(process.cwd(), 'src', 'scripts', 'mockGameData.json');
const jsonData = JSON.stringify(gameRuns, null, 2);

writeFileSync(outputPath, jsonData, 'utf-8');

console.log(`\n💾 Saved to: ${outputPath}`);
console.log(`📊 Total size: ${(jsonData.length / 1024).toFixed(2)} KB`);
