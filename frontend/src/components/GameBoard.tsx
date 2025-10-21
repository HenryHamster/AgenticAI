import { Tile, Player } from '@/types/game';
import TileCell from './TileCell';

interface GameBoardProps {
  boardState: Tile[][] | Tile[] | any; // Support both 2D array (legacy) and flat array (new format)
  players: Player[];
  boardSize?: number; // Optional board size hint (e.g., 3, 6, 10)
}

export default function GameBoard({ boardState, players, boardSize }: GameBoardProps) {
  // Calculate board dimensions
  const calculateBoardSize = (): number => {
    if (boardSize) return boardSize;
    
    // For 2D array format
    if (Array.isArray(boardState) && boardState.length > 0 && Array.isArray(boardState[0])) {
      return boardState[0].length; // Assume square board
    }
    
    // For flat array format, calculate from tile positions
    if (Array.isArray(boardState) && boardState.length > 0) {
      const positions = (boardState as Tile[]).map(tile => tile.position);
      const maxX = Math.max(...positions.map(pos => Math.abs(pos[0])));
      const maxY = Math.max(...positions.map(pos => Math.abs(pos[1])));
      const worldSize = Math.max(maxX, maxY);
      return worldSize * 2 + 1; // Convert world_size to board_size
    }
    
    return 10; // Default fallback
  };

  const gridSize = calculateBoardSize();

  // Create a map of player positions for quick lookup
  const playerPositionMap = new Map<string, Player>();
  players.forEach(player => {
    // Handle both array [x, y] and object {x, y} position formats
    const x = Array.isArray(player.position) ? player.position[0] : (player.position as any).x;
    const y = Array.isArray(player.position) ? player.position[1] : (player.position as any).y;
    const key = `${x},${y}`;
    playerPositionMap.set(key, player);
  });

  return (
    <div className="w-full max-w-3xl mx-auto">
      <div 
        className="grid gap-0.5 sm:gap-1 bg-gray-400 p-0.5 sm:p-1 rounded-lg shadow-xl"
        style={{ 
          gridTemplateColumns: `repeat(${gridSize}, minmax(0, 1fr))` 
        }}
      >
        {Array.isArray(boardState) && boardState.length > 0 && Array.isArray(boardState[0]) ? (
          // Handle 2D array (legacy format)
          (boardState as Tile[][]).map((row: Tile[], y: number) =>
            row.map((tile: Tile, x: number) => {
              const playerAtTile = playerPositionMap.get(`${x},${y}`);
              return (
                <TileCell
                  key={`${x}-${y}`}
                  tile={tile}
                  player={playerAtTile}
                />
              );
            })
          )
        ) : Array.isArray(boardState) ? (
          // Handle flat array of tiles (new format)
          (boardState as Tile[]).map((tile: Tile) => {
            const x = tile.position[0];
            const y = tile.position[1];
            const playerAtTile = playerPositionMap.get(`${x},${y}`);
            return (
              <TileCell
                key={`${x}-${y}`}
                tile={tile}
                player={playerAtTile}
              />
            );
          })
        ) : null}
      </div>
    </div>
  );
}
