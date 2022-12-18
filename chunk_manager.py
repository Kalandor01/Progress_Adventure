from os.path import join
from typing import Any
from copy import deepcopy

from constants import CHUNK_SIZE, SAVE_FOLDER_NAME_CHUNKS, SAVE_EXT
from tools import logger, decode_save_s, encode_save_s, Log_type


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
    def __init__(self, base_x:int, base_y:int, tiles:dict[str, Tile]=None):
        self.base_x = int(base_x) // CHUNK_SIZE * CHUNK_SIZE
        self.base_y = int(base_y) // CHUNK_SIZE * CHUNK_SIZE
        logger("Creating chunk", f"base_x: {self.base_x} , base_y: {self.base_y}")
        self.tiles:dict[str, Tile] = {}
        if tiles is not None:
            self.tiles = tiles


    def to_json(self):
        """Returns a json representation of the `Chunk`."""
        chunk_json = {"tiles": []}
        for tile in self.tiles:
            chunk_json["tiles"].append(self.tiles[tile].to_json())
        return chunk_json


    def find_tile(self, x:int, y:int):
        """
        Returns the `Tile` if it exists.\n
        Otherwise it returns `None`.
        """
        x_con = x % CHUNK_SIZE
        y_con = y % CHUNK_SIZE
        tile_name = f"{x_con}_{y_con}"
        if tile_name in self.tiles.keys():
            return self.tiles[tile_name]
        else:
            return None


    def gen_tile(self, x:int, y:int):
        """Generates a `Tile` in the specified location."""
        x_con = x % CHUNK_SIZE
        y_con = y % CHUNK_SIZE
        new_tile_name = f"{x_con}_{y_con}"
        new_tile = Tile(x_con, y_con, None)
        self.tiles[new_tile_name] = new_tile
        logger("Creating tile", f"x: {x} , y: {y}", Log_type.DEBUG)
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
        encode_save_s(chunk_data, join(save_folder, SAVE_FOLDER_NAME_CHUNKS, chunk_file_name))
        logger("Saved chunk", f"{chunk_file_name}.{SAVE_EXT}")
        

class World:
    def __init__(self, chunks:dict[str, Chunk]=None):
        logger("Generating World")
        self.chunks:dict[str, Chunk] = {}
        if chunks is not None:
            self.chunks = chunks
    

    def find_chunk(self, x:int, y:int):
        """
        Returns the `Chunk` if it exists.\n
        Otherwise it returns `None`.
        """
        x_con = x // CHUNK_SIZE * CHUNK_SIZE
        y_con = y // CHUNK_SIZE * CHUNK_SIZE
        chunk_name = f"{x_con}_{y_con}"
        if chunk_name in self.chunks.keys():
            return self.chunks[chunk_name]
        else:
            return None
    
    
    def gen_chunk(self, x:int, y:int):
        """Generates a new `Chunk` in the specified location."""
        x_con = x // CHUNK_SIZE * CHUNK_SIZE
        y_con = y // CHUNK_SIZE * CHUNK_SIZE
        new_chunk_name = f"{x_con}_{y_con}"
        new_chunk = Chunk(x_con, y_con)
        self.chunks[new_chunk_name] = new_chunk
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


    def _load_tile_json(self, tile:dict[str, Any]):
        """Converts the tile json to dict format."""
        x = int(tile["x"])
        y = int(tile["y"])
        content = tile["content"]
        tile_name = f"{x}_{y}"
        tile_obj = Tile(x, y, content)
        return {tile_name: tile_obj}


    def save_all_chunks_to_files(self, save_folder:str, remove_chunks=False):
        """
        Saves all chunks to the save file.\n
        If `remove_chunks` is True, it also removes the chunks from the chunks list.
        """
        if remove_chunks:
            chunk_data = deepcopy(self.chunks)
            self.chunks.clear()
        else:
            chunk_data = self.chunks
        for chunk in chunk_data:
            chunk_data[chunk].save_to_file(save_folder)


    def find_chunk_in_folder(self, x:int, y:int, save_folder:str):
        """
        Returns the `Chunk` if it exists in the chunks folder.\n
        Otherwise it returns `None`.
        """
        base_x = x // CHUNK_SIZE * CHUNK_SIZE
        base_y = y // CHUNK_SIZE * CHUNK_SIZE
        chunk_file_name = f"chunk_{base_x}_{base_y}"
        try:
            chunk_data = decode_save_s(join(save_folder, SAVE_FOLDER_NAME_CHUNKS, chunk_file_name))
        except FileNotFoundError:
            return None
        else:
            tiles = {}
            for tile in chunk_data["tiles"]:
                tiles.update(self._load_tile_json(tile))
            chunk = Chunk(base_x, base_y, tiles)
            return chunk
    

    def load_chunk_from_folder(self, x:int, y:int, save_folder:str, append_mode=True):
        """
        Returns the `Chunk` if it exists in the chunks folder, and adds it to the `chunks` dict.\n
        Otherwise it generates a new `Chunk` object.\n
        If `append_mode` is True and the chunk already exists in the `chunks` dict, it appends the tiles from the loaded chunk to the one it the dict.
        """
        chunk = self.find_chunk_in_folder(x, y, save_folder)
        if chunk is not None:
            base_x = x // CHUNK_SIZE * CHUNK_SIZE
            base_y = y // CHUNK_SIZE * CHUNK_SIZE
            chunk_name = f"{base_x}_{base_y}"
            # append mode
            appended = False
            existing_chunk = self.find_chunk(x, y)
            if append_mode and existing_chunk is not None:
                appended = True
                chunk.tiles.update(existing_chunk.tiles)
                existing_chunk.tiles = chunk.tiles
                chunk = existing_chunk
            else:
                self.chunks[chunk_name] = chunk
            logger(f"{'Appended' if appended else 'Loaded'} chunk from file", f"{chunk_name}.{SAVE_EXT}", Log_type.DEBUG)
        else:
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


    def get_tile(self, x:int, y:int, save_folder:str=None):
        """
        Returns the `Tile` if it exists in the `chunks` list or in the chunks folder.\n
        Otherwise it generates a new `Tile` and a new `Chunk`, if that also doesn't exist.
        """
        chunk = self.find_chunk(x, y)
        if chunk is None:
            if save_folder is not None:
                chunk = self.load_chunk_from_folder(x, y, save_folder)
                tile = chunk.get_tile(x, y)
            else:
                tile = self.gen_tile(x, y)
        else:
            tile = chunk.get_tile(x, y)
        return tile