import os

from tools import CHUNK_SIZE, SAVE_FOLDER_NAME_CHUNKS, SAVE_EXT, logger, decode_save_s, encode_save_s, Log_type


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

    
    def save_to_file(self, save_folder:str):
        """Saves the chunk's data a file in the save folder."""
        chunk_data = self.to_json()
        chunk_file_name = f"chunk_{self.base_x}_{self.base_y}"
        encode_save_s(chunk_data, os.path.join(save_folder, SAVE_FOLDER_NAME_CHUNKS, chunk_file_name))
        logger("Saved chunk", f"chunk_{self.base_x}_{self.base_y}.{SAVE_EXT}")
        

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


    def _load_tile_json(self, tile:dict):
        """Converts the tile json to object format."""
        x = int(tile["x"])
        y = int(tile["y"])
        content = tile["content"]
        tile_obj = Tile(x, y, content)
        return tile_obj


    def save_all_chunks_to_files(self, save_folder:str, remove_chunks=False):
        """
        Saves all chunks to the save file.\n
        If `remove_chunks` is True, it also removes the chunks from the chunks list.
        """
        for chunk in self.chunks:
            chunk.save_to_file(save_folder)
        if remove_chunks:
            self.chunks.clear()


    def get_chunk_in_folder(self, x:int, y:int, save_folder:str):
        """
        Returns the `Chunk` if it exists in the chunks folder.\n
        Otherwise it generates a new `Chunk` object.
        """
        base_x = x // CHUNK_SIZE
        base_y = y // CHUNK_SIZE
        chunk_file_name = f"chunk_{base_x}_{base_y}"
        try:
            chunk_data = decode_save_s(os.path.join(save_folder, SAVE_FOLDER_NAME_CHUNKS, chunk_file_name))
        except FileNotFoundError:
            chunk = self.gen_chunk(x, y)
        else:
            tiles = []
            for tile in chunk_data["tiles"]:
                tiles.append(self._load_tile_json(tile))
            chunk = Chunk(base_x, base_y, tiles)
        if self.find_chunk(x, y) is not None:
            self.chunks.append(chunk)
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