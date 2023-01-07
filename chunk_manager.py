from enum import Enum
from os.path import join
from typing import Any
from copy import deepcopy
from perlin_noise import PerlinNoise

from constants import                                           \
    SAVE_EXT, SAVE_FOLDER_NAME_CHUNKS, CHUNK_SIZE,              \
    CHUNK_FILE_NAME, CHUNK_FILE_NAME_SEP, TILE_NOISE_RESOLUTION
from tools import world_seed, tile_type_noise_seeds, logger, decode_save_s, encode_save_s, Log_type
from data_manager import Save_data


class Content_types(Enum):
    NONE =      "_"
    BLANK =     "blank"
    FIELD =     "field"
    MOUNTAIN =  "mountain"
    FIGHT =     "fight"
    VILLAGE =   "village"


class Base_content:
    def __init__(self, data:dict[str, Any]|None=None):
        self.type = Content_types.BLANK


    def _visit(self, tile:'Tile', save_data:Save_data):
        tile.visited += 1
        logger(f"Player visited \"{self.type}\"", f"x: {tile.x}, y: {tile.y}, visits: {tile.visited}")


    def to_json(self):
        """Returns a json representation of the `Content`."""
        content_json:dict[str, Any] = {"type": self.type.value}
        return content_json


class Field_content(Base_content):
    def __init__(self, data:dict[str, Any]|None=None):
        super().__init__()
        self.type = Content_types.FIELD


    def _visit(self, tile:'Tile', save_data:Save_data):
        super()._visit(tile, save_data)
        print(f"{save_data.player.full_name} entered a {self.type.value}.")


class Mountain_content(Base_content):
    def __init__(self, data:dict[str, Any]|None=None):
        super().__init__()
        self.type = Content_types.MOUNTAIN
        if data is not None:
            try: self._set_height(data["height"])
            except KeyError: self._set_height()
        else:
            self._set_height()

    
    def _set_height(self, height:int|None=None):
        if height is None:
            self.height = world_seed.randint(500, 10000)
        else:
            self.height = int(height)
    

    def _visit(self, tile:'Tile', save_data:Save_data):
        super()._visit(tile, save_data)
        print(f"{save_data.player.full_name} climbed a {self.type.value}.")
        print(f"The {self.type.value} is {self.height}m tall.")


    def to_json(self):
        content_json = super().to_json()
        content_json["height"] = self.height
        return content_json
    

class Fight_content(Base_content):
    def __init__(self, data:dict[str, Any]|None=None):
        super().__init__()
        self.type = Content_types.FIGHT
        if data is not None:
            try: self._set_fight(data["fight"])
            except KeyError: self._set_fight()
        else:
            self._set_fight()


    def _set_fight(self, fight:str|None=None):
        if fight is None:
            self.fight = "test"
        else:
            self.fight = str(fight)


    def _visit(self, tile:'Tile', save_data:Save_data):
        super()._visit(tile, save_data)
        print(f"{save_data.player.full_name} entered a {self.type.value}.")
        print(self.fight)


    def to_json(self):
        content_json = super().to_json()
        content_json["fight"] = self.fight
        return content_json


class Village_content(Base_content):
    def __init__(self, data:dict[str, Any]|None=None):
        super().__init__()
        self.type = Content_types.VILLAGE
        if data is not None:
            try: self._set_population(data["population"])
            except KeyError: self._set_population()
        else:
            self._set_population()


    def _set_population(self, population:int|None=None):
        if population is None:
            self.population = world_seed.randint(100, 100000)
        else:
            self.population = int(population)


    def _visit(self, tile:'Tile', save_data:Save_data):
        super()._visit(tile, save_data)
        print(f"{save_data.player.full_name} entered a {self.type.value}.")
        print(f"The {self.type.value} has a population of {self.population} people.")


    def to_json(self):
        content_json = super().to_json()
        content_json["population"] = self.population
        return content_json


# mapps all content types to content classes for `_get_content()`
_content_type_map:dict[str, type[Base_content]] = {
                    Content_types.NONE.value: Field_content,
                    Content_types.BLANK.value: Field_content,
                    Content_types.FIELD.value: Field_content,
                    Content_types.MOUNTAIN.value: Mountain_content,
                    Content_types.FIGHT.value: Fight_content,
                    Content_types.VILLAGE.value: Village_content
                }

# all randomly selectable content classes in `_gen_content()` with the properties of that content class
_content_properties:dict[type[Base_content], dict[str, float]] = {
                                            Field_content:
                                            {
                                                "danger": 0.0,
                                                "height": 0.5,
                                                "temperature": 0.5,
                                                "humidity": 0.5,
                                                "population": 0.1
                                            },
                                            Mountain_content:
                                            {
                                                "danger": 0.1,
                                                "height": 1.0,
                                                "temperature": 0.25,
                                                "humidity": 0.3,
                                                "population": 0.0
                                            },
                                            Fight_content:
                                            {
                                                "danger": 1.0,
                                                "height": 0.5,
                                                "temperature": 0.5,
                                                "humidity": 0.5,
                                                "population": 0.8
                                            },
                                            Village_content:
                                            {
                                                "danger": 0.1,
                                                "height": 0.5,
                                                "temperature": 0.6,
                                                "humidity": 0.6,
                                                "population": 1.0
                                            },
                                        }


# Offsets for the calculated noise value in `_get_nose_values()`.
tile_type_noise_offsets:dict[str, float] = {
    "danger": -0.1,
    "height": 0,
    "temperature": 0,
    "humidity": 0,
    "population": -0.1
}


def recalculate_noise_generators(ttn_seeds:dict[str, int]):
    """Recalculate perlin noise generators for tile generation."""
    perlin_danger = PerlinNoise(octaves=2**36, seed=ttn_seeds["danger"])
    perlin_height = PerlinNoise(octaves=2**35, seed=ttn_seeds["height"])
    perlin_temperature = PerlinNoise(octaves=2**34, seed=ttn_seeds["temperature"])
    perlin_humidity = PerlinNoise(octaves=2**34, seed=ttn_seeds["humidity"])
    perlin_population = PerlinNoise(octaves=2**36, seed=ttn_seeds["population"])
    
    tile_type_noises = {
        "danger": perlin_danger,
        "height": perlin_height,
        "temperature": perlin_temperature,
        "humidity": perlin_humidity,
        "population": perlin_population
    }
    return tile_type_noises


# noise generators for tile generation
_tile_type_noises = recalculate_noise_generators(tile_type_noise_seeds)


def _get_nose_values(absolute_x:int, absoulte_y:int):
    """Gets the noise values for each perlin noise generator at a specific point, and normalises it between 0 and 1."""
    noise_values:dict[str, float] = {}
    for name, noise in _tile_type_noises.items():
        noise_values[name] = (noise([(absolute_x + TILE_NOISE_RESOLUTION / 2) / TILE_NOISE_RESOLUTION,
                                    (absoulte_y + TILE_NOISE_RESOLUTION / 2) / TILE_NOISE_RESOLUTION])
                                    + 0.5 + tile_type_noise_offsets[name])
    return noise_values


def _calculate_closest(noise_values:dict[str, float]):
    """Calculates the best tile type for the space depending on the perlin noise values."""
    min_diff_content = Field_content
    min_diff = 1000000
    for content_type, properties in _content_properties.items():
        sum_diff = 0
        for name in properties:
            try:
                sum_diff += abs(properties[name] - noise_values[name])
            except KeyError:
                pass
        if sum_diff < min_diff:
            min_diff = sum_diff
            min_diff_content = content_type
    return min_diff_content
        


def _gen_content(absolute_x:int, absoulte_y:int):
    """Generates a random content for a tile."""
    noise_values = _get_nose_values(absolute_x, absoulte_y)
    content:type[Base_content] = _calculate_closest(noise_values)
    return content()


def _get_content(content_type:str) -> type[Base_content]:
    """Get the content class from the content type."""
    # get content type index
    try: return _content_type_map[content_type]
    except KeyError:
        logger("Unknown content type", f'type: "{content_type}"', Log_type.ERROR)
        return Field_content


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
    def __init__(self, absolute_x:int, absoulte_y:int, visited:int|None=None, content:Base_content|None=None):
        """
        If `content` is None, the x and y must be absolute coordinates.
        """
        self.x = int(absolute_x) % CHUNK_SIZE
        self.y = int(absoulte_y) % CHUNK_SIZE
        if visited is None:
            visited = 0
        self.visited = visited
        if content is None:
            content = _gen_content(absolute_x, absoulte_y)
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


    def gen_tile(self, absolute_x:int, absolute_y:int):
        """Generates a `Tile` in the specified location."""
        x_con = absolute_x % CHUNK_SIZE
        y_con = absolute_y % CHUNK_SIZE
        new_tile_name = f"{x_con}_{y_con}"
        new_tile = Tile(absolute_x, absolute_y)
        self.tiles[new_tile_name] = new_tile
        logger("Creating tile", f"x: {x_con} , y: {y_con}", Log_type.DEBUG)
        return new_tile


    def get_tile(self, absolute_x:int, absolute_y:int):
        """
        Returns the `Tile` if it exists.\n
        Otherwise it generates a new one.
        """
        tile = self.find_tile(absolute_x, absolute_y)
        if tile is None:
            return self.gen_tile(absolute_x, absolute_y)
        else:
            return tile


    def save_to_file(self, save_folder_path:str):
        """Saves the chunk's data into a file in the save folder."""
        chunk_data = self.to_json()
        chunk_file_name = f"{CHUNK_FILE_NAME}{CHUNK_FILE_NAME_SEP}{self.base_x}{CHUNK_FILE_NAME_SEP}{self.base_y}"
        encode_save_s(chunk_data, join(save_folder_path, SAVE_FOLDER_NAME_CHUNKS, chunk_file_name))
        logger("Saved chunk", f"{chunk_file_name}.{SAVE_EXT}")


    def fill_chunk(self):
        """
        Generates ALL not yet generated tiles.
        """
        for x in range(CHUNK_SIZE):
            for y in range(CHUNK_SIZE):
                self.get_tile(self.base_x + x, self.base_y + y)


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


    def save_all_chunks_to_files(self, save_folder_path:str, remove_chunks=False, show_progress_text:str|None=None):
        """
        Saves all chunks to the save file.\n
        If `remove_chunks` is True, it also removes the chunks from the chunks list.\n
        If `show_progress_text` is not None, it writes out a progress percentage while saving.
        """
        if remove_chunks:
            chunk_data = deepcopy(self.chunks)
            self.chunks.clear()
        else:
            chunk_data = self.chunks
        if show_progress_text is not None:
            cl = len(chunk_data)
            print(show_progress_text, end="", flush=True)
            for x, chunk in enumerate(chunk_data.values()):
                chunk.save_to_file(save_folder_path)
                print(f"\r{show_progress_text}{round((x + 1) / cl * 100, 1)}%", end="", flush=True)
            print(f"\r{show_progress_text}DONE!             ")
        else:
            for chunk in chunk_data.values():
                chunk.save_to_file(save_folder_path)


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


    def gen_tile(self, absolute_x:int, absolute_y:int):
        """
        Generates a new `Tile`.\n
        Generates a new `Chunk` if that also doesn't exist.
        """
        chunk = self.get_chunk(absolute_x, absolute_y)
        new_tile = chunk.gen_tile(absolute_x, absolute_y)
        return new_tile


    def get_tile(self, absolute_x:int, absolute_y:int, save_folder_path:str|None=None):
        """
        Returns the `Tile` if it exists in the `chunks` list or in the chunks folder.\n
        Otherwise it generates a new `Tile` and a new `Chunk`, if that also doesn't exist.
        """
        chunk = self.find_chunk(absolute_x, absolute_y)
        if chunk is None:
            if save_folder_path is not None:
                chunk = self.load_chunk_from_folder(absolute_x, absolute_y, save_folder_path)
                tile = chunk.get_tile(absolute_x, absolute_y)
            else:
                tile = self.gen_tile(absolute_x, absolute_y)
        else:
            tile = chunk.get_tile(absolute_x, absolute_y)
        return tile
    
    
    def fill_all_chunks(self, show_progress_text:str|None=None):
        """
        Generates ALL not yet generated tiles in ALL chunks.\n
        If `show_progress_text` is not None, it writes out a progress percentage while generating.
        """
        if show_progress_text is not None:
            chunks = self.chunks.values()
            cl = len(chunks)
            print(show_progress_text, end="", flush=True)
            for x, chunk in enumerate(chunks):
                chunk.fill_chunk()
                print(f"\r{show_progress_text}{round((x + 1) / cl * 100, 1)}%", end="", flush=True)
            print(f"\r{show_progress_text}DONE!             ")
        else:
            for chunk in self.chunks.values():
                chunk.fill_chunk()


    def _get_corners(self):
        """
        Returns the four corners of the world.\n
        (-x, -y, +x, +y)
        """
        min_x = 0
        min_y = 0
        max_x = 0
        max_y = 0
        for chunk in self.chunks.values():
            if chunk.base_x < min_x:
                min_x = chunk.base_x
            if chunk.base_y < min_y:
                min_y = chunk.base_y
            if chunk.base_x > max_x:
                max_x = chunk.base_x
            if chunk.base_y > max_y:
                max_y = chunk.base_y
        max_x += CHUNK_SIZE - 1
        max_y += CHUNK_SIZE - 1
        return (min_x, min_y, max_x, max_y)
    
    
    def make_rectangle(self, save_folder_path:str|None=None, append_mode=True):
        """
        Generates chunks in a way that makes the world rectangle shaped.\n
        If `save_folder_path` is not None, it will try to load the chunks from the save folder first (calls `load_chunk_from_folder`).
        """
        corners = self._get_corners()
        search_folder = save_folder_path is not None
        for x in range(corners[0], corners[2] + 1, CHUNK_SIZE):
            for y in range(corners[1], corners[3] + 1, CHUNK_SIZE):
                if search_folder:
                    self.load_chunk_from_folder(x, y, save_folder_path, append_mode)
                else:
                    self.get_chunk(x, y)
