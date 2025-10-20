import { Tile, Player } from '@/types/game';

interface TileCellProps {
  tile: Tile;
  player?: Player;
}

export default function TileCell({ tile, player }: TileCellProps) {
  // Extract tile coordinates from either array or object format
  const tileX = Array.isArray(tile.position) ? tile.position[0] : (tile as any).x;
  const tileY = Array.isArray(tile.position) ? tile.position[1] : (tile as any).y;
  const terrainEmoji = tile.terrainEmoji || '🏞️';
  const playerEmoji = player?.emoji || '🧙';
  const playerName = player?.name || player?.uid || 'Player';
  
  return (
    <div 
      className="relative aspect-square border border-gray-300 bg-gradient-to-br from-gray-50 to-gray-100 hover:shadow-lg transition-shadow group cursor-pointer"
      title={tile.description}
    >
      {/* Terrain emoji */}
      <div className="absolute inset-0 flex items-center justify-center text-lg sm:text-xl md:text-2xl">
        {terrainEmoji}
      </div>
      
      {/* Player emoji if present */}
      {player && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-xl sm:text-2xl md:text-3xl drop-shadow-lg animate-bounce-subtle">
            {playerEmoji}
          </div>
        </div>
      )}
      
      {/* Hover tooltip */}
      <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 min-w-[200px] max-w-[300px] bg-black/95 text-white text-base sm:text-lg px-4 py-3 sm:py-4 opacity-0 group-hover:opacity-100 transition-opacity z-50 shadow-lg leading-relaxed rounded-md whitespace-normal pointer-events-none">
        {tile.description}
        {player && <div className="font-bold mt-2">{playerName}</div>}
      </div>
      
      {/* Coordinates (subtle) */}
      <div className="absolute top-0 right-0 text-[7px] sm:text-[8px] text-gray-400 p-0.5">
        {tileX},{tileY}
      </div>
    </div>
  );
}
