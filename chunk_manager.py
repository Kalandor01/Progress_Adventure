from enum import Enum
from os.path import join
from typing import Any
from copy import deepcopy

from constants import                                           \
    SAVE_EXT, SAVE_FOLDER_NAME_CHUNKS, CHUNK_SIZE,              \
    CHUNK_FILE_NAME, CHUNK_FILE_NAME_SEP, TILE_NOISE_RESOLUTION
from tools import world_seed, noise_generators, logger, decode_save_s, encode_save_s, Log_type
from data_manager import Save_data


class Content_types(Enum):
    NONE =          "none"
    TERRAIN =       "terrain"
    STRUCTURE =     "structure"
    POPULATION =    "population"


class Terrain_types(Enum):
    NONE =      "none"
    FIELD =     "field"
    MOUNTAIN =  "mountain"
    OCEAN =     "ocean"
    SHORE =     "shore"


class Structure_types(Enum):
    NONE =          "none"
    VILLAGE =       "village"
    KINGDOM =       "kingdom"
    BANDIT_CAMP =   "bandit_camp"


class Population_types(Enum):
    NONE =      "none"
    HUMAN =     "human"
    DWARF =     "dwarf"
    ELF =       "elf"
    DEMON =     "demon"


class Base_content:
    def __init__(self, data:dict[str, Any]|None=None):
        self.type = Content_types.NONE


    def _visit(self, tile:'Tile', save_data:Save_data):
        logger(f"Player visited \"{self.type}\"", f"x: {tile.x}, y: {tile.y}, visits: {tile.visited}")


    def to_json(self):
        """Returns a json representation of the `Content`."""
        content_json:dict[str, Any] = {"type": self.type.value}
        return content_json
    
    
class Terrain_content(Base_content):
    def __init__(self, data:dict[str, Any]|None=None):
        super().__init__(data)
        self.type = Content_types.TERRAIN
        self.subtype = Terrain_types.NONE


    def _visit(self, tile:'Tile', save_data:Save_data):
        logger(f"Player visited \"{self.type}\": \"{self.subtype}\"", f"x: {tile.x}, y: {tile.y}, visits: {tile.visited}")


    def to_json(self):
        """Returns a json representation of the `Terrain`."""
        terrain_json = super().to_json()
        terrain_json["subtype"] = self.subtype.value
        return terrain_json


class Structure_content(Base_content):
    def __init__(self, data:dict[str, Any]|None=None):
        super().__init__(data)
        self.type = Content_types.STRUCTURE
        self.subtype = Structure_types.NONE


    def _visit(self, tile:'Tile', save_data:Save_data):
        logger(f"Player visited \"{self.type}\": \"{self.subtype}\"", f"x: {tile.x}, y: {tile.y}, visits: {tile.visited}")


    def to_json(self):
        """Returns a json representation of the `Structure`."""
        structure_json = super().to_json()
        structure_json["subtype"] = self.subtype.value
        return structure_json


class Population_content(Base_content):
    def __init__(self, data:dict[str, Any]|None=None):
        super().__init__(data)
        self.type = Content_types.POPULATION
        self.subtype = Population_types.NONE
        if data is not None:
            try: self._set_amount(data["amount"])
            except KeyError: self._set_amount()
        else:
            self._set_amount()


    def _set_amount(self, population:int|range|None=None):
        if isinstance(population, int):
            self.amount = population
        elif isinstance(population, range):
            self.amount = world_seed.randint(population.start, population.stop)
        else:
            self.amount = world_seed.randint(1, 1000)


    def _visit(self, tile:'Tile', save_data:Save_data):
        logger(f"Player visited \"{self.type}\": \"{self.subtype}\"", f"x: {tile.x}, y: {tile.y}, visits: {tile.visited}")
        if self.subtype != Population_types.NONE and self.amount > 0:
            print(f"There {'is' if self.amount == 1 else 'are'} {self.amount} {self.subtype.value}{'' if self.amount == 1 else 's'} here.")
        if self.subtype != Population_types.NONE and tile.structure.subtype != Structure_types.NONE:
            if tile.structure.subtype == Structure_types.BANDIT_CAMP:
                if save_data.world_seed.rand() < 0.75:
                    print("fight")
            elif tile.structure.subtype in [Structure_types.VILLAGE, Structure_types.KINGDOM]:
                if save_data.world_seed.rand() < 0.01:
                    print("fight")


    def to_json(self):
        """Returns a json representation of the `Population`."""
        population_json = super().to_json()
        population_json["subtype"] = self.subtype.value
        population_json["amount"] = self.amount
        return population_json


class Field_terrain(Terrain_content):
    def __init__(self, data:dict[str, Any]|None=None):
        super().__init__(data)
        self.subtype = Terrain_types.FIELD


    def _visit(self, tile:'Tile', save_data:Save_data):
        super()._visit(tile, save_data)
        print(f"{save_data.player.full_name} entered a field.")


class Mountain_terrain(Terrain_content):
    def __init__(self, data:dict[str, Any]|None=None):
        super().__init__(data)
        self.subtype = Terrain_types.MOUNTAIN
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
        print(f"{save_data.player.full_name} climbed a mountain.")
        print(f"The mountain is {self.height}m tall.")


    def to_json(self):
        terrain_json = super().to_json()
        terrain_json["height"] = self.height
        return terrain_json


class Ocean_terrain(Terrain_content):
    def __init__(self, data:dict[str, Any]|None=None):
        super().__init__(data)
        self.subtype = Terrain_types.OCEAN
        if data is not None:
            try: self._set_depth(data["depth"])
            except KeyError: self._set_depth()
        else:
            self._set_depth()

    
    def _set_depth(self, depth:int|None=None):
        if depth is None:
            self.depth = world_seed.randint(100, 20000)
        else:
            self.depth = int(depth)
    

    def _visit(self, tile:'Tile', save_data:Save_data):
        super()._visit(tile, save_data)
        print(f"{save_data.player.full_name} entered an ocean.")
        print(f"The ocean is {self.depth}m deep.")


    def to_json(self):
        terrain_json = super().to_json()
        terrain_json["depth"] = self.depth
        return terrain_json


class Shore_terrain(Terrain_content):
    def __init__(self, data:dict[str, Any]|None=None):
        super().__init__(data)
        self.subtype = Terrain_types.SHORE
        if data is not None:
            try: self._set_depth(data["depth"])
            except KeyError: self._set_depth()
        else:
            self._set_depth()

    
    def _set_depth(self, depth:int|None=None):
        if depth is None:
            self.depth = world_seed.randint(1, 100)
        else:
            self.depth = int(depth)
    

    def _visit(self, tile:'Tile', save_data:Save_data):
        super()._visit(tile, save_data)
        print(f"{save_data.player.full_name} entered an shore.")
        print(f"The shore is {self.depth}m deep.")


    def to_json(self):
        terrain_json = super().to_json()
        terrain_json["depth"] = self.depth
        return terrain_json


class No_structure(Structure_content):
    def __init__(self, data:dict[str, Any]|None=None):
        super().__init__(data)
        self.subtype = Structure_types.NONE


    def _visit(self, tile:'Tile', save_data:Save_data):
        pass


class Bandit_camp_structure(Structure_content):
    def __init__(self, data:dict[str, Any]|None=None):
        super().__init__(data)
        self.subtype = Structure_types.BANDIT_CAMP


    def _visit(self, tile:'Tile', save_data:Save_data):
        print(f"{save_data.player.full_name} entered a bandit camp.")
        super()._visit(tile, save_data)


class Village_structure(Structure_content):
    def __init__(self, data:dict[str, Any]|None=None):
        super().__init__(data)
        self.subtype = Structure_types.VILLAGE
        if data is not None:
            try: self._set_population(data["population"])
            except KeyError: self._set_population()
        else:
            self._set_population()


    def _set_population(self, population:int|None=None):
        if population is None:
            self.population = world_seed.randint(50, 10000)
        else:
            self.population = int(population)


    def _visit(self, tile:'Tile', save_data:Save_data):
        super()._visit(tile, save_data)
        print(f"{save_data.player.full_name} entered a village.")
        print(f"The village has a population of {self.population} people.")


    def to_json(self):
        structure_json = super().to_json()
        structure_json["population"] = self.population
        return structure_json


class Kingdom_structure(Structure_content):
    def __init__(self, data:dict[str, Any]|None=None):
        super().__init__(data)
        self.subtype = Structure_types.KINGDOM
        if data is not None:
            try: self._set_population(data["population"])
            except KeyError: self._set_population()
        else:
            self._set_population()


    def _set_population(self, population:int|None=None):
        if population is None:
            self.population = world_seed.randint(10000, 10000000)
        else:
            self.population = int(population)


    def _visit(self, tile:'Tile', save_data:Save_data):
        super()._visit(tile, save_data)
        print(f"{save_data.player.full_name} entered a kingdom.")
        print(f"The kingdom has a population of {self.population} people.")


    def to_json(self):
        structure_json = super().to_json()
        structure_json["population"] = self.population
        return structure_json


class No_population(Population_content):
    def __init__(self, data:dict[str, Any]|None=None):
        super().__init__(data)
        self.subtype = Population_types.NONE
        self.amount = 0
    
    
    def _visit(self, tile:'Tile', save_data:Save_data):
        pass


class Human_population(Population_content):
    def __init__(self, data:dict[str, Any]|None=None):
        super().__init__(data)
        self.subtype = Population_types.HUMAN


class Elf_population(Population_content):
    def __init__(self, data:dict[str, Any]|None=None):
        super().__init__(data)
        self.subtype = Population_types.ELF


class Dwarf_population(Population_content):
    def __init__(self, data:dict[str, Any]|None=None):
        super().__init__(data)
        self.subtype = Population_types.DWARF


class Demon_population(Population_content):
    def __init__(self, data:dict[str, Any]|None=None):
        super().__init__(data)
        self.subtype = Population_types.DEMON


# mapps all terrain types to terrain classes for `_get_terrain()`
_terrain_type_map:dict[str, type[Terrain_content]] = {
                    Terrain_types.NONE.value: Field_terrain,
                    Terrain_types.FIELD.value: Field_terrain,
                    Terrain_types.MOUNTAIN.value: Mountain_terrain,
                    Terrain_types.OCEAN.value: Ocean_terrain,
                    Terrain_types.SHORE.value: Shore_terrain
                }

# mapps all structure types to structure classes for `_get_structure()`
_structure_type_map:dict[str, type[Structure_content]] = {
                    Structure_types.NONE.value: No_structure,
                    Structure_types.BANDIT_CAMP.value: Bandit_camp_structure,
                    Structure_types.VILLAGE.value: Village_structure,
                    Structure_types.KINGDOM.value: Kingdom_structure
                }

# mapps all population types to population classes for `_get_population()`
_population_type_map:dict[str, type[Population_content]] = {
                    Population_types.NONE.value: No_population,
                    Population_types.HUMAN.value: Human_population,
                    Population_types.DWARF.value: Dwarf_population,
                    Population_types.ELF.value: Elf_population,
                    Population_types.DEMON.value: Demon_population
                }


# all randomly selectable terrain classes in `_gen_terrain()` with the properties of that terrain class
_terrain_properties:dict[type[Terrain_content], dict[str, float]] = {
                                            Mountain_terrain:
                                            {
                                                "height": 1.0,
                                            },
                                            Field_terrain:
                                            {
                                                "height": 0.5,
                                            },
                                            Shore_terrain:
                                            {
                                                "height": 0.325,
                                            },
                                            Ocean_terrain:
                                            {
                                                "height": 0.29,
                                            },
                                        }

# all randomly selectable structure classes in `_gen_structure()` with the properties of that structure class
_structure_properties:dict[type[Structure_content], dict[str, float]] = {
                                            No_structure:
                                            {
                                                "population": 0.0
                                            },
                                            Bandit_camp_structure:
                                            {
                                                "hostility": 1.0,
                                                "population": 0.3
                                            },
                                            Village_structure:
                                            {
                                                "hostility": 0.0,
                                                "population": 0.6
                                            },
                                            Kingdom_structure:
                                            {
                                                "hostility": 0.0,
                                                "population": 0.8
                                            },
                                        }

# all randomly selectable population classes in `_gen_population()` with the properties of that population class
_population_properties:dict[type[Population_content], dict[str, float]] = {
                                            No_population:
                                            {
                                                "population": 0.1
                                            },
                                            Human_population:
                                            {
                                                "height": 0.6,
                                                "temperature": 0.6,
                                                "humidity": 0.4,
                                                "hostility": 0.3,
                                            },
                                            Elf_population:
                                            {
                                                "height": 1.0,
                                                "temperature": 0.5,
                                                "humidity": 0.75,
                                                "hostility": 0.3,
                                            },
                                            Dwarf_population:
                                            {
                                                "height": 0.1,
                                                "temperature": 0.6,
                                                "humidity": 0.3,
                                                "hostility": 0.6,
                                            },
                                            Demon_population:
                                            {
                                                "height": 0.1,
                                                "temperature": 0.9,
                                                "humidity": 0.1,
                                                "hostility": 0.9,
                                            },
                                        }


# Offsets for the calculated noise value in `_get_nose_values()`.
_tile_type_noise_offsets:dict[str, float] = {
    "height": 0,
    "temperature": 0,
    "humidity": 0,
    "hostility": -0.1,
    "population": -0.1
}
# If difference is larger than this the structure/poupation will not generate. Used in `calculate_closest()`
_no_structure_difference_limit = 0.3
_no_population_difference_limit = 0.2


def _get_nose_values(absolute_x:int, absoulte_y:int):
    """Gets the noise values for each perlin noise generator at a specific point, and normalises it between 0 and 1."""
    noise_values:dict[str, float] = {}
    for name, noises in noise_generators.items():
        noise_values[name] = (noises[0]([(absolute_x + TILE_NOISE_RESOLUTION / 2) / TILE_NOISE_RESOLUTION,
                                    (absoulte_y + TILE_NOISE_RESOLUTION / 2) / TILE_NOISE_RESOLUTION])
                                    )
        noise_values[name] += (noises[1]([(absolute_x + TILE_NOISE_RESOLUTION / 2) / TILE_NOISE_RESOLUTION,
                                    (absoulte_y + TILE_NOISE_RESOLUTION / 2) / TILE_NOISE_RESOLUTION])
                                    * 0.5)
        noise_values[name] += (noises[2]([(absolute_x + TILE_NOISE_RESOLUTION / 2) / TILE_NOISE_RESOLUTION,
                                    (absoulte_y + TILE_NOISE_RESOLUTION / 2) / TILE_NOISE_RESOLUTION])
                                    * 0.25)
        noise_values[name] = (noise_values[name] + 0.875 + _tile_type_noise_offsets[name]) / 1.75
    return noise_values


def _calculate_closest(noise_values:dict[str, float], content_properties:dict[type[Base_content], dict[str, float]]):
    """Calculates the best tile type for the space depending on the perlin noise values."""
    min_diff_content = list(content_properties.keys())[0]
    min_diff = 1000000
    for content_type, properties in content_properties.items():
        sum_diff = 0
        property_num = 0
        for name in properties:
            try:
                sum_diff += abs(properties[name] - noise_values[name])
                property_num += 1
            except KeyError:
                pass
        prop_dif = sum_diff / property_num
        if prop_dif < min_diff:
            min_diff = prop_dif
            min_diff_content = content_type
    # no content if difference is too big
    if content_properties == _structure_properties and min_diff >= _no_structure_difference_limit:
        min_diff_content = No_structure
    elif content_properties == _population_properties and min_diff >= _no_population_difference_limit:
        min_diff_content = No_population
    return min_diff_content()


def _get_content(content_type:str, type_map:dict[str, type[Base_content]]) -> type[Base_content]:
    """Get the content class from the content type and type map."""
    # get content type index
    try: return type_map[content_type]
    except KeyError:
        logger("Unknown content type", f'type: "{content_type}"', Log_type.ERROR)
        return list(type_map.values())[0]


def _load_content(content_json:dict[str, Any]|None, type_map:dict[str, type[Base_content]]):
    """Load a content object from the content json."""
    # get content type
    if content_json is not None:
        try: content_type = content_json["subtype"]
        except KeyError: content_type = list(type_map.keys())[0]
    else:
        content_type = list(type_map.keys())[0]
    # get content
    content_class = _get_content(content_type, type_map)
    return content_class(content_json)


class Tile:
    def __init__(self, absolute_x:int, absoulte_y:int, visited:int|None=None, terrain:Terrain_content|None=None, structure:Structure_content|None=None, population:Population_content|None=None):
        global _no_structure_difference_limit
        global _no_population_difference_limit
        """
        If `content` is None, the x and y must be absolute coordinates.
        """
        self.x = int(absolute_x) % CHUNK_SIZE
        self.y = int(absoulte_y) % CHUNK_SIZE
        if visited is None:
            visited = 0
        self.visited = visited
        if terrain is None or structure is None or population is None:
            noise_values = _get_nose_values(absolute_x, absoulte_y)
            if terrain is None:
                gen_terrain:Terrain_content = _calculate_closest(noise_values, _terrain_properties)
                terrain = gen_terrain
            if structure is None:
                # less structures on water
                reset_no_sdl = _no_structure_difference_limit
                if terrain.subtype == Terrain_types.OCEAN:
                    _no_structure_difference_limit -= 0.1
                elif terrain.subtype == Terrain_types.SHORE:
                    _no_structure_difference_limit -= 0.05
                gen_structure:Structure_content = _calculate_closest(noise_values, _structure_properties)
                structure = gen_structure
                _no_structure_difference_limit = reset_no_sdl
            if population is None:
                # less population on not structures
                reset_no_pdl = _no_population_difference_limit
                if structure.subtype == Structure_types.NONE:
                    _no_population_difference_limit -= 0.1
                gen_population:Population_content = _calculate_closest(noise_values, _population_properties)
                population = gen_population
                _no_population_difference_limit = reset_no_pdl
        self.terrain = terrain
        self.structure = structure
        self.population = population


    def visit(self, save_data:Save_data):
        self.visited += 1
        self.terrain._visit(self, save_data)
        self.structure._visit(self, save_data)
        self.population._visit(self, save_data)


    def to_json(self):
        """Returns a json representation of the `Tile`."""
        terrain_json = self.terrain.to_json()
        structure_json = self.structure.to_json()
        population_json = self.population.to_json()
        
        tile_json:dict[str, Any] = {
            "x": self.x,
            "y": self.y,
            "visited": self.visited,
            "terrain": terrain_json,
            "structure": structure_json,
            "population": population_json
        }
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
        try:
            terrain = tile["terrain"]
            structure = tile["structure"]
            population = tile["population"]
        except KeyError:
            terrain = tile["content"]
            if terrain is not None:
                try: terrain["subtype"] = terrain["type"]
                except KeyError:
                    terrain = None
            else:
                terrain = None
            structure = None
            population = None
        tile_name = f"{x}_{y}"
        terrain_obj:Terrain_content = _load_content(terrain, _terrain_type_map)
        structure_obj:Structure_content = _load_content(structure, _structure_type_map)
        population_obj:Population_content = _load_content(population, _population_type_map)
        tile_obj = Tile(x, y, visited, terrain_obj, structure_obj, population_obj)
        return {tile_name: tile_obj}


    def save_all_chunks_to_files(self, save_folder_path:str, remove_chunks=False, show_progress_text:str|None=None):
        """
        Saves all chunks to the save file.\n
        If `remove_chunks` is True, it also removes the chunks from the chunks list.\n
        If `show_progress_text` is not None, it writes out a progress percentage while saving.
        """
        if remove_chunks:
            if show_progress_text is not None:
                print(f"{show_progress_text}COPYING...\r", end="", flush=True)
            chunk_data = deepcopy(self.chunks)
            self.chunks.clear()
        else:
            chunk_data = self.chunks
        if show_progress_text is not None:
            cl = len(chunk_data)
            print(show_progress_text + "              ", end="", flush=True)
            for x, chunk in enumerate(chunk_data.values()):
                chunk.save_to_file(save_folder_path)
                print(f"\r{show_progress_text}{round((x + 1) / cl * 100, 1)}%", end="", flush=True)
            print(f"\r{show_progress_text}DONE!                       ")
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
