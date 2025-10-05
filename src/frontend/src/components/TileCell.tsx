import { Tile, Player } from '@/types/game';

interface TileCellProps {
  tile: Tile;
  player?: Player;
}

export default function TileCell({ tile, player }: TileCellProps) {
  return (
    <div 
      className="relative aspect-square border border-gray-300 bg-gradient-to-br from-gray-50 to-gray-100 hover:shadow-lg transition-shadow group cursor-pointer"
      title={tile.description}
    >
      {/* Terrain emoji */}
      <div className="absolute inset-0 flex items-center justify-center text-lg sm:text-xl md:text-2xl">
        {tile.terrainEmoji}
      </div>
      
      {/* Player emoji if present */}
      {player && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-xl sm:text-2xl md:text-3xl drop-shadow-lg animate-bounce-subtle">
            {player.emoji}
          </div>
        </div>
      )}
      
      {/* Hover tooltip */}
      <div className="absolute bottom-0 left-0 right-0 bg-black/90 text-white text-[10px] sm:text-xs p-1 opacity-0 group-hover:opacity-100 transition-opacity z-10 line-clamp-2">
        {tile.description}
        {player && <div className="font-bold mt-0.5">{player.name}</div>}
      </div>
      
      {/* Coordinates (subtle) */}
      <div className="absolute top-0 right-0 text-[7px] sm:text-[8px] text-gray-400 p-0.5">
        {tile.x},{tile.y}
      </div>
    </div>
  );
}
