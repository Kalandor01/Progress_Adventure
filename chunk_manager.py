from tools import CHUNK_SIZE, logger, Log_type

class Tile:
    def __init__(self, x:int, y:int, content):
        self.x = int(x) % CHUNK_SIZE
        self.y = int(y) % CHUNK_SIZE
        self.content = content
        


class Chunk:
    def __init__(self, base_x:int, base_y:int, tiles:list[Tile]=None):
        self.base_x = int(base_x) // CHUNK_SIZE
        self.base_y = int(base_y) // CHUNK_SIZE
        logger("Generating chunk", f"base_x: {self.base_x} , base_y: {self.base_y}")
        self.tiles:list[Tile] = []
        for tile in tiles:
            self.tiles.append(tile)
    

    def to_json(self):
        chunk_json = {}
        return chunk_json
    

    def find_tile(self, x:int, y:int):
        x_con = x % CHUNK_SIZE
        y_con = y % CHUNK_SIZE
        for tile in self.tiles:
            if tile.x == x_con and tile.y == y_con:
                return tile
        return None

    
    def gen_tile(self, x:int, y:int):
        x_con = x % CHUNK_SIZE
        y_con = y % CHUNK_SIZE
        new_tile = Tile(x_con, y_con, None)
        self.tiles.append(new_tile)
        logger("Generating tile", f"x: {x} , y: {y}")
        return new_tile



    def get_tile(self, x:int, y:int):
        chunk = self.find_tile(x, y)
        if chunk is None:
            return self.gen_tile(x, y)
        else:
            return chunk