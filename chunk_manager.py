from os.path import join
from typing import Any
from copy import deepcopy

from constants import CHUNK_SIZE, CHUNK_FILE_NAME, CHUNK_FILE_NAME_SEP, SAVE_FOLDER_NAME_CHUNKS, SAVE_EXT
from tools import r, logger, decode_save_s, encode_save_s, Log_type
from data_manager import Save_data


class Base_content:
    def __init__(self, data:dict[str, Any]|None=None):
        self.type = "blank"
    

    def _visit(self, tile:'Tile', save_data:Save_data):
        tile.visited += 1
        logger(f"Player visited \"{self.type}\"", f"x: {tile.x}, y: {tile.y}, visits: {tile.visited}")
    
    
    def to_json(self):
        """Returns a json representation of the `Content`."""
        content_json:dict[str, Any] = {"type": self.type}
        return content_json


class Field_content(Base_content):
    def __init__(self, data:dict[str, Any]|None=None):
        super().__init__()
        self.type = "field"


    def _visit(self, tile:'Tile', save_data:Save_data):
        super()._visit(tile, save_data)
        print(f"{save_data.player.full_name} entered a {self.type}.")


class Fight_content(Base_content):
    def __init__(self, data:dict[str, Any]|None=None):
        super().__init__()
        self.type = "fight"
        if data is not None:
            try: self.fight = str(data["fight"])
            except KeyError: self.fight = "test"
        else:
            self.fight = "test"
    
    

    def _visit(self, tile:'Tile', save_data:Save_data):
        super()._visit(tile, save_data)
        print(f"{save_data.player.full_name} entered a {self.type}.")
        print(self.fight)
    
    
    def to_json(self):
        content_json = super().to_json()
        content_json["fight"] = self.fight
        return content_json


def _nornalise_weights(weights:list[int|float]):
    sum_w = sum(weights)
    return [w / sum_w for w in weights]


# all content types for `_get_content()`
_content_types = [
                        "_",
                        "blank",
                        "field",
                        "fight"
                ]
# content classes to map to `_content_types`
_content_map_objects = [
                        Field_content,
                        Field_content,
                        Field_content,
                        Fight_content
                    ]
# all randomly selectable content classes in `_gen_content()`
_content_objects = [
                                        Field_content,
                                        Fight_content
                ]
# the chances for content classes to be selected for each selectable content in `_content_objects`
_content_weights_raw:list[int|float] = [
                                        20,
                                        1
                                    ]
_content_weights = _nornalise_weights(_content_weights_raw)


def _gen_content():
    """Generates a random content for a tile"""
    content:type[Base_content] = r.choice(_content_objects, 1, p=_content_weights)[0]
    return content()


def _get_content(content_type:str):
    """Get the content class from the content type."""
    # get content type index
    try: content_index = _content_types.index(content_type)
    except ValueError: content_index = 0
    # get content class
    content:type[Base_content] = _content_map_objects[content_index]
    return content


def _load_content(content_json:dict[str, Any]|None):
    """Load a content object from the content json."""
    # get content type
    if content_json is not None:
        try: content_type = content_json["type"]
        except KeyError: content_type = "_"
    else:
        content_type = "_"
    # get content
    content_class = _get_content(content_type)
    return content_class(content_json)


class Tile:
    def __init__(self, x:int, y:int, visited:int|None=None, content:Base_content|None=None):
        self.x = int(x) % CHUNK_SIZE
        self.y = int(y) % CHUNK_SIZE
        if visited is None:
            visited = 0
        self.visited = visited
        if content is None:
            content = _gen_content()
        self.content = content


    def visit(self, save_data:Save_data):
        return self.content._visit(self, save_data)


    def to_json(self):
        """Returns a json representation of the `Tile`."""
        content_json = None
        if self.content is not None:
            content_json = self.content.to_json()
        
        tile_json:dict[str, Any] = {"x": self.x, "y": self.y, "visited": self.visited, "content": content_json}
        return tile_json


class Chunk:
    def __init__(self, base_x:int, base_y:int, tiles:dict[str, Tile]|None=None):
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
        new_tile = Tile(x_con, y_con)
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


    def save_to_file(self, save_folder_path:str):
        """Saves the chunk's data a file in the save folder."""
        chunk_data = self.to_json()
        chunk_file_name = f"{CHUNK_FILE_NAME}{CHUNK_FILE_NAME_SEP}{self.base_x}{CHUNK_FILE_NAME_SEP}{self.base_y}"
        encode_save_s(chunk_data, join(save_folder_path, SAVE_FOLDER_NAME_CHUNKS, chunk_file_name))
        logger("Saved chunk", f"{chunk_file_name}.{SAVE_EXT}")
        

class World:
    def __init__(self, chunks:dict[str, Chunk]|None=None):
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
        try: visited = int(tile["visited"])
        except KeyError: visited = None
        content = tile["content"]
        tile_name = f"{x}_{y}"
        content_obj = _load_content(content)
        tile_obj = Tile(x, y, visited, content_obj)
        return {tile_name: tile_obj}


    def save_all_chunks_to_files(self, save_folder_path:str, remove_chunks=False):
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
            chunk_data[chunk].save_to_file(save_folder_path)


    def find_chunk_in_folder(self, x:int, y:int, save_folder_path:str):
        """
        Returns the `Chunk` if it exists in the chunks folder.\n
        Otherwise it returns `None`.
        """
        base_x = x // CHUNK_SIZE * CHUNK_SIZE
        base_y = y // CHUNK_SIZE * CHUNK_SIZE
        chunk_file_name = f"{CHUNK_FILE_NAME}{CHUNK_FILE_NAME_SEP}{base_x}{CHUNK_FILE_NAME_SEP}{base_y}"
        try:
            chunk_data = decode_save_s(join(save_folder_path, SAVE_FOLDER_NAME_CHUNKS, chunk_file_name))
        except FileNotFoundError:
            return None
        else:
            tiles = {}
            for tile in chunk_data["tiles"]:
                tiles.update(self._load_tile_json(tile))
            chunk = Chunk(base_x, base_y, tiles)
            return chunk
    

    def load_chunk_from_folder(self, x:int, y:int, save_folder_path:str, append_mode=True):
        """
        Returns the `Chunk` if it exists in the chunks folder, and adds it to the `chunks` dict.\n
        Otherwise it generates a new `Chunk` object.\n
        If `append_mode` is True and the chunk already exists in the `chunks` dict, it appends the tiles from the loaded chunk to the one it the dict.
        """
        chunk = self.find_chunk_in_folder(x, y, save_folder_path)
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


    def get_tile(self, x:int, y:int, save_folder_path:str|None=None):
        """
        Returns the `Tile` if it exists in the `chunks` list or in the chunks folder.\n
        Otherwise it generates a new `Tile` and a new `Chunk`, if that also doesn't exist.
        """
        chunk = self.find_chunk(x, y)
        if chunk is None:
            if save_folder_path is not None:
                chunk = self.load_chunk_from_folder(x, y, save_folder_path)
                tile = chunk.get_tile(x, y)
            else:
                tile = self.gen_tile(x, y)
        else:
            tile = chunk.get_tile(x, y)
        return tile