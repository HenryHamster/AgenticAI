import { Tile, Player } from '@/types/game';
import TileCell from './TileCell';

interface GameBoardProps {
  boardState: Tile[][];
  players: Player[];
}

export default function GameBoard({ boardState, players }: GameBoardProps) {
  // Create a map of player positions for quick lookup
  const playerPositionMap = new Map<string, Player>();
  players.forEach(player => {
    const key = `${player.position.x},${player.position.y}`;
    playerPositionMap.set(key, player);
  });

  return (
    <div className="w-full max-w-3xl mx-auto">
      <div className="grid grid-cols-10 gap-0.5 sm:gap-1 bg-gray-400 p-0.5 sm:p-1 rounded-lg shadow-xl">
        {boardState.map((row, y) =>
          row.map((tile, x) => {
            const playerAtTile = playerPositionMap.get(`${x},${y}`);
            return (
              <TileCell
                key={`${x}-${y}`}
                tile={tile}
                player={playerAtTile}
              />
            );
          })
        )}
      </div>
    </div>
  );
}
