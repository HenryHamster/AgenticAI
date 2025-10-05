import { GameRun, Player, Tile, Turn, PlayerAction, TerrainType } from '@/types/game';
// import { join } from 'path';
// import fs from 'fs';

// Terrain configurations
const TERRAIN_CONFIG: Record<TerrainType, { emoji: string; descriptions: string[] }> = {
  mountain: {
    emoji: '🏔️',
    descriptions: [
      'A towering mountain peak covered in snow',
      'Rocky cliffs with treacherous paths',
      'A steep mountainside with hidden caves',
      'Ancient stone formations rising high',
    ]
  },
  forest: {
    emoji: '🌲',
    descriptions: [
      'A dense forest with towering trees',
      'Lush woodland filled with wildlife',
      'A dark grove with twisted branches',
      'Ancient trees with thick canopies',
    ]
  },
  desert: {
    emoji: '🏜️',
    descriptions: [
      'A vast expanse of golden sand',
      'Barren wasteland with scorching heat',
      'Sandy dunes stretching endlessly',
      'A desolate desert plain',
    ]
  },
  ocean: {
    emoji: '🌊',
    descriptions: [
      'Deep blue waters with strong currents',
      'A calm bay with crystal clear water',
      'Turbulent seas with crashing waves',
      'Shallow coastal waters',
    ]
  },
  plains: {
    emoji: '🌾',
    descriptions: [
      'Rolling grasslands under open sky',
      'Fertile plains with golden wheat',
      'Open meadow with wildflowers',
      'Flat grassland stretching to horizon',
    ]
  }
};

const PLAYER_EMOJIS = ['🧙', '⚔️', '🛡️', '🏹', '🗡️', '🔮', '⚡', '🌟'];
const PLAYER_NAMES = ['Aria', 'Borin', 'Cade', 'Delia', 'Eren', 'Fiona', 'Gareth', 'Hilda'];

// Action templates for different scenarios
const ACTION_TEMPLATES = {
  mining: {
    valid: [
      { action: 'mine the mountain for ore', resolution: 'Successfully extracted valuable ore from the mountain', health: 0, currency: 10, creativity: 7 },
      { action: 'dig for precious gems', resolution: 'Found a cache of precious gemstones', health: -1, currency: 15, creativity: 8 },
      { action: 'quarry stone from the cliffs', resolution: 'Harvested quality stone and sold it to merchants', health: -1, currency: 8, creativity: 5 },
    ],
    invalid: [
      { action: 'mine the desert sand', resolution: 'Exhausted trying to mine sand, found nothing of value', health: -2, currency: -1, creativity: 2 },
      { action: 'dig in the ocean', resolution: 'Foolishly attempted to mine underwater, nearly drowned', health: -3, currency: 0, creativity: 1 },
    ]
  },
  trading: {
    valid: [
      { action: 'seek out a merchant to trade', resolution: 'Found a traveling merchant and made a profitable trade', health: 0, currency: 12, creativity: 6 },
      { action: 'barter with local villagers', resolution: 'Exchanged goods with villagers for coins', health: 0, currency: 8, creativity: 5 },
      { action: 'sell foraged items', resolution: 'Gathered herbs and sold them at market', health: 0, currency: 6, creativity: 7 },
    ]
  },
  combat: {
    valid: [
      { action: 'hunt wild beasts for bounty', resolution: 'Defeated a fierce beast and claimed the reward', health: -2, currency: 15, creativity: 7 },
      { action: 'challenge bandits to combat', resolution: 'Fought off bandits and took their treasure', health: -3, currency: 20, creativity: 8 },
      { action: 'defend against ambush', resolution: 'Successfully repelled attackers and looted their supplies', health: -1, currency: 10, creativity: 6 },
    ]
  },
  exploration: {
    valid: [
      { action: 'explore the forest for treasure', resolution: 'Discovered a hidden chest containing gold coins', health: 0, currency: 12, creativity: 8 },
      { action: 'search for ancient ruins', resolution: 'Found ruins with valuable artifacts', health: 0, currency: 18, creativity: 9 },
      { action: 'investigate mysterious cave', resolution: 'Explored cave and found merchant stash', health: -1, currency: 14, creativity: 8 },
    ]
  },
  movement: {
    valid: [
      { action: 'travel north to find resources', resolution: 'Journeyed north and discovered new opportunities', health: 0, currency: 5, creativity: 4 },
      { action: 'navigate through the terrain', resolution: 'Successfully traversed difficult terrain', health: -1, currency: 3, creativity: 5 },
      { action: 'scout the area ahead', resolution: 'Scouted safely and found a merchant path', health: 0, currency: 7, creativity: 6 },
    ]
  },
  creative: {
    valid: [
      { action: 'craft items from found materials', resolution: 'Created valuable goods and sold them', health: 0, currency: 10, creativity: 9 },
      { action: 'perform for travelers', resolution: 'Entertained a wealthy caravan and earned generous tips', health: 0, currency: 11, creativity: 10 },
      { action: 'brew potions from forest herbs', resolution: 'Brewed healing potions and sold to adventurers', health: 0, currency: 13, creativity: 9 },
      { action: 'set up a trap for game', resolution: 'Cleverly trapped valuable prey and sold the pelts', health: 0, currency: 9, creativity: 8 },
    ]
  }
};

function randomInt(min: number, max: number): number {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function randomChoice<T>(array: T[]): T {
  return array[Math.floor(Math.random() * array.length)];
}

function generateBoard(): Tile[][] {
  const board: Tile[][] = [];
  const terrainTypes: TerrainType[] = ['mountain', 'forest', 'desert', 'ocean', 'plains'];
  
  // Create regions for more realistic terrain distribution
  for (let y = 0; y < 10; y++) {
    const row: Tile[] = [];
    for (let x = 0; x < 10; x++) {
      let terrainType: TerrainType;
      
      // Create terrain regions based on position
      if (x < 3 && y < 3) {
        terrainType = 'mountain';
      } else if (x > 6 && y < 4) {
        terrainType = 'ocean';
      } else if (x > 6 && y > 6) {
        terrainType = 'desert';
      } else if (y > 6) {
        terrainType = 'forest';
      } else {
        terrainType = 'plains';
      }
      
      // Add some randomness
      if (Math.random() > 0.7) {
        terrainType = randomChoice(terrainTypes);
      }
      
      const config = TERRAIN_CONFIG[terrainType];
      row.push({
        x,
        y,
        terrainType,
        terrainEmoji: config.emoji,
        description: randomChoice(config.descriptions)
      });
    }
    board.push(row);
  }
  
  return board;
}

function generatePlayers(count: number, board: Tile[][]): Player[] {
  const players: Player[] = [];
  const usedPositions = new Set<string>();
  
  for (let i = 0; i < count; i++) {
    let x: number, y: number;
    
    // Find unique starting position
    do {
      x = randomInt(0, 9);
      y = randomInt(0, 9);
    } while (usedPositions.has(`${x},${y}`));
    
    usedPositions.add(`${x},${y}`);
    
    players.push({
      id: `player-${i + 1}`,
      name: PLAYER_NAMES[i % PLAYER_NAMES.length],
      emoji: PLAYER_EMOJIS[i % PLAYER_EMOJIS.length],
      health: 10,
      currency: 0,
      position: { x, y },
      validityScore: 0,
      creativityScore: 0,
      isActive: true
    });
  }
  
  return players;
}

function generatePlayerAction(
  player: Player,
  turnNumber: number,
  board: Tile[][]
): PlayerAction {
  const currentTile = board[player.position.y][player.position.x];
  const categories = Object.keys(ACTION_TEMPLATES) as (keyof typeof ACTION_TEMPLATES)[];
  let category = randomChoice(categories);
  
  // Bias actions based on terrain
  if (currentTile.terrainType === 'mountain' && Math.random() > 0.3) {
    category = 'mining';
  } else if (currentTile.terrainType === 'forest' && Math.random() > 0.4) {
    category = 'exploration';
  }
  
  const categoryActions = ACTION_TEMPLATES[category];
  const validActions = 'valid' in categoryActions ? categoryActions.valid : [];
  const invalidActions = 'invalid' in categoryActions ? categoryActions.invalid : [];
  
  // 85% chance of valid action
  const isValid = Math.random() > 0.15;
  const actionPool = isValid ? validActions : (invalidActions.length > 0 ? invalidActions : validActions);
  const template = randomChoice(actionPool) as { 
    action: string; 
    resolution: string; 
    health: number; 
    currency: number; 
    creativity: number;
  };
  
  return {
    playerId: player.id,
    playerName: player.name,
    actionDeclaration: template.action,
    resolution: template.resolution,
    healthChange: template.health,
    currencyChange: template.currency,
    validityScore: isValid ? randomInt(7, 10) : randomInt(1, 4),
    creativityScore: template.creativity,
    isValid
  };
}

function cloneBoard(board: Tile[][]): Tile[][] {
  return board.map(row => row.map(tile => ({ ...tile })));
}

function clonePlayers(players: Player[]): Player[] {
  return players.map(p => ({ ...p, position: { ...p.position } }));
}

function generateTurns(
  players: Player[],
  initialBoard: Tile[][],
  targetCurrency: number,
  maxTurns: number = 10
): Turn[] {
  const turns: Turn[] = [];
  let currentPlayers = clonePlayers(players);
  const board = cloneBoard(initialBoard);
  
  for (let turnNum = 0; turnNum < maxTurns; turnNum++) {
    const actions: PlayerAction[] = [];
    
    // Generate actions for each active player
    for (const player of currentPlayers) {
      if (!player.isActive) continue;
      
      const action = generatePlayerAction(player, turnNum, board);
      actions.push(action);
      
      // Apply action effects
      player.health += action.healthChange;
      player.currency += action.currencyChange;
      player.validityScore += action.validityScore;
      player.creativityScore += action.creativityScore;
      
      // Check if player died
      if (player.health <= 0) {
        player.isActive = false;
        player.health = 0;
      }
      
      // Randomly move player (30% chance)
      if (Math.random() > 0.7) {
        const directions = [
          { dx: -1, dy: 0 }, { dx: 1, dy: 0 },
          { dx: 0, dy: -1 }, { dx: 0, dy: 1 }
        ];
        const dir = randomChoice(directions);
        const newX = Math.max(0, Math.min(9, player.position.x + dir.dx));
        const newY = Math.max(0, Math.min(9, player.position.y + dir.dy));
        player.position.x = newX;
        player.position.y = newY;
      }
      
      // Check win condition
      if (player.currency >= targetCurrency) {
        turns.push({
          turnNumber: turnNum,
          actions,
          boardState: cloneBoard(board),
          playerStates: clonePlayers(currentPlayers)
        });
        return turns;
      }
    }
    
    turns.push({
      turnNumber: turnNum,
      actions,
      boardState: cloneBoard(board),
      playerStates: clonePlayers(currentPlayers)
    });
    
    // Check if all players are dead
    if (currentPlayers.every(p => !p.isActive)) {
      break;
    }
  }
  
  return turns;
}

export function generateGameRun(
  playerCount: number = 4,
  targetCurrency: number = 100,
  maxTurns: number = 10
): GameRun {
  const id = `game-${Date.now()}-${randomInt(1000, 9999)}`;
  const startTime = new Date(Date.now() - randomInt(1000000, 10000000)).toISOString();
  
  const initialBoard = generateBoard();
  const players = generatePlayers(playerCount, initialBoard);
  const turns = generateTurns(players, initialBoard, targetCurrency, maxTurns);
  
  // Determine winner
  const lastTurn = turns[turns.length - 1];
  const winner = lastTurn.playerStates.find(p => p.currency >= targetCurrency);
  const winnerId = winner?.id || null;
  
  const endTime = new Date(new Date(startTime).getTime() + turns.length * 60000).toISOString();
  
  return {
    id,
    startTime,
    endTime,
    winnerId,
    players: lastTurn.playerStates,
    turns,
    targetCurrency,
    initialBoardState: initialBoard
  };
}

export function generateMultipleGameRuns(count: number = 3): GameRun[] {
  const gameRuns: GameRun[] = [];
  
  for (let i = 0; i < count; i++) {
    const playerCount = randomInt(2, 4);
    const targetCurrency = randomInt(80, 120);
    const maxTurns = randomInt(7, 12);
    
    gameRuns.push(generateGameRun(playerCount, targetCurrency, maxTurns));
  }
  
  return gameRuns;
}

// Generate and export mock data
const mockGameRuns = generateMultipleGameRuns(3);
// const writePath = join(process.cwd(), 'src', 'scripts', 'mockGameData.json');
// fs.writeFileSync(writePath, JSON.stringify(mockGameRuns, null, 2), 'utf-8');

export { mockGameRuns };