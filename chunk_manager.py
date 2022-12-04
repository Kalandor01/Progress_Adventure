from tools import CHUNK_SIZE, logger, Log_type

class Tile:
    def __init__(self, x:int, y:int, content):
        self.x = int(x) % CHUNK_SIZE
        self.y = int(y) % CHUNK_SIZE
        self.content = content
        
        
    def to_json(self):
        """Returns a json representation of the `Tile`."""
        tile_json = {"x": self.x, "y": self.y, "content": self.content}
        return tile_json
        


class Chunk:
    def __init__(self, base_x:int, base_y:int, tiles:list[Tile]=None):
        self.base_x = int(base_x) // CHUNK_SIZE
        self.base_y = int(base_y) // CHUNK_SIZE
        logger("Generating chunk", f"base_x: {self.base_x} , base_y: {self.base_y}")
        self.tiles:list[Tile] = []
        if tiles is not None:
            for tile in tiles:
                self.tiles.append(tile)
    

    def to_json(self):
        """Returns a json representation of the `Chunk`."""
        chunk_json = {"tiles": []}
        for tile in self.tiles:
            chunk_json["tiles"].append(tile.to_json())
        return chunk_json
    

    def find_tile(self, x:int, y:int):
        """
        Returns the `Tile` if it exists.\n
        Otherwise it returns `None`.
        """
        x_con = x % CHUNK_SIZE
        y_con = y % CHUNK_SIZE
        for tile in self.tiles:
            if tile.x == x_con and tile.y == y_con:
                return tile
        return None

    
    def gen_tile(self, x:int, y:int):
        """Generates a new `Tile` in the specified location."""
        x_con = x % CHUNK_SIZE
        y_con = y % CHUNK_SIZE
        new_tile = Tile(x_con, y_con, None)
        self.tiles.append(new_tile)
        logger("Generating tile", f"x: {x} , y: {y}")
        return new_tile



    def get_tile(self, x:int, y:int):
        """
        Returns the `Tile` if it exists.\n
        Otherwise it generates a new one.
        """
        tile = self.find_tile(x, y)
        if tile is None:
            return self.gen_tile(x, y)
        else:
            return tile
        

class World:
    def __init__(self, chunks:list[Chunk]=None):
        logger("Generating World")
        self.chunks:list[Chunk] = []
        if chunks is not None:
            for chunk in chunks:
                self.chunks.append(chunk)
    

    def find_chunk(self, x:int, y:int):
        """
        Returns the `Chunk` if it exists.\n
        Otherwise it returns `None`.
        """
        x_con = x // CHUNK_SIZE
        y_con = y // CHUNK_SIZE
        for chunk in self.chunks:
            if chunk.base_x == x_con and chunk.base_y == y_con:
                return chunk
        return None
    
    
    def gen_chunk(self, x:int, y:int):
        """Generates a new `Chunk` in the specified location."""
        x_con = x // CHUNK_SIZE
        y_con = y // CHUNK_SIZE
        new_chunk = Chunk(x_con, y_con)
        self.chunks.append(new_chunk)
        logger("Generating chunk", f"x: {x_con} , y: {y_con}")
        return new_chunk
    
    
    def get_chunk(self, x:int, y:int):
        """
        Returns the `Chunk` if it exists.\n
        Otherwise it generates a new one.
        """
        chunk = self.find_chunk(x, y)
        if chunk is None:
            chunk = self.gen_chunk(x, y)
        return chunk


    def find_tile(self, x:int, y:int):
        """
        Returns the `Tile` if it, and the `Chunk` it's suposed to be in, exists.\n
        Otherwise it returns `None`.
        """
        chunk = self.find_chunk(x, y)
        if chunk is not None:
            return chunk.find_tile(x, y)
        else:
            return None


    def gen_tile(self, x:int, y:int):
        """
        Generates a new `Tile`.\n
        Generates a new `Chunk` if that also doesn't exist.
        """
        chunk = self.get_chunk(x, y)
        new_tile = chunk.gen_tile(x, y)
        return new_tile


    def get_tile(self, x:int, y:int):
        """
        Returns the `Tile` if it exists.\n
        Otherwise it generates a new `Tile` and a new `Chunk`, if that also doesn't exist.
        """
        tile = self.find_tile(x, y)
        if tile is None:
            tile = self.gen_tile(x, y)
        return tile