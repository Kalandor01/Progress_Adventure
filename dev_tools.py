from enum import Enum
import json
import math
from os import listdir
from os.path import join, isdir
from sys import exc_info
from typing import Any, Callable, Literal
from zipfile import ZipFile
from datetime import datetime
from PIL import Image, ImageDraw

from utils import Color, make_date, make_time, stylized_text, press_key
from constants import                                                                   \
    ENCODING,                                                                           \
    MAIN_THREAD_NAME, TEST_THREAD_NAME, VISUALIZER_THREAD_NAME,                         \
    ROOT_FOLDER,                                                                        \
    SAVES_FOLDER_PATH, SAVE_EXT,                                                        \
    BACKUPS_FOLDER_PATH, OLD_BACKUP_EXT, BACKUP_EXT,                                    \
    SAVE_FILE_NAME_DATA,                                                                \
    SAVE_SEED,                                                                          \
    FILE_ENCODING_VERSION, CHUNK_SIZE,                                                  \
    SAVE_VERSION, TILE_NOISE_RESOLUTION, DOUBLE_KEYS
import tools as ts
from tools import sfm

import data_manager as dm
from chunk_manager import World, Save_data, Terrain_types, Structure_types, Population_types, Tile
from save_manager import _load_player_json

def decode_save_file(save_name:str, save_name_pre=SAVES_FOLDER_PATH, save_num=SAVE_SEED, save_ext=SAVE_EXT):
    """
    Decodes a save file into a normal json.
    """
    try:
        save_data = sfm.decode_save(save_num, join(save_name_pre, save_name), save_ext, ENCODING)
    except FileNotFoundError:
        print(f"decode_save_file: FILE {save_name} NOT FOUND!")
    else:
        with open(f'{save_name}.decoded.json', "w") as f:
            for line in save_data:
                f.write(line + "\n")


def encode_save_file(save_name:str, pre_save_name=SAVES_FOLDER_PATH, save_num=SAVE_SEED, save_ext=SAVE_EXT):
    """
    Encodes a json file into a .sav file.
    """
    try:
        with open(f'{save_name}.decoded.json', "r") as f:
            save_data = f.readlines()
        save_data_new = []
        for line in save_data:
            save_data_new.append(line.replace("\n", ""))
    except FileNotFoundError:
        print(f"encode_save_file: FILE {save_name} NOT FOUND!")
    else:
        sfm.encode_save(save_data_new, save_num, join(pre_save_name, save_name), save_ext, ENCODING, FILE_ENCODING_VERSION)


def recompile_save_file(save_name:str, new_save_name:str, pre_save_name=SAVES_FOLDER_PATH, new_pre_save_name=SAVES_FOLDER_PATH, save_ext=SAVE_EXT, new_save_ext=SAVE_EXT, save_num=SAVE_SEED, new_save_num=SAVE_SEED):
    """
    Recompiles a save file to a different name/number.
    """
    if new_save_name is None:
        new_save_name = save_name
    try:
        save_data = sfm.decode_save(save_num, join(pre_save_name, save_name), save_ext, ENCODING)
    except FileNotFoundError:
        print(f"recompile_save_file: FILE {save_name} NOT FOUND!")
        return False
    else:
        sfm.encode_save(save_data, new_save_num, join(new_pre_save_name, new_save_name), new_save_ext, ENCODING, FILE_ENCODING_VERSION)
        return True


def unzipp(zip_from_path:str, zip_to_path:str):
    if isdir(f"{zip_to_path}.{BACKUP_EXT}"):
        with ZipFile(f"{zip_to_path}.{BACKUP_EXT}", 'r') as zip_ref:
            zip_ref.extractall(zip_from_path)
    else:
        print(f"unzip: FILE {zip_to_path}.{BACKUP_EXT} NOT FOUND")


def _old_file_reader(save_name:str="save*", save_ext:str=OLD_BACKUP_EXT, dir_name:str=BACKUPS_FOLDER_PATH, decode_until:int=1):
    """
    sfm.file_reader but for backups
    """
    from os import path, listdir

    # get existing file numbers
    file_names = listdir(dir_name)
    existing_files:list[list[str|int]] = []
    for name in file_names:
        if path.isfile(path.join(dir_name, name)) and name.find(save_ext) and name.find(save_name.replace("*", "")):
            try: file_number = int(name.replace(f".{save_ext}", "").split(save_name.replace("*", ""))[1])
            except ValueError: continue
            except IndexError: continue
            existing_files.append([name, file_number])
    existing_files.sort()

    file_data = []
    for files in existing_files:
        try:
            try:
                data = sfm.decode_save(int(files[1]), path.join(dir_name, str(files[0])), "", decode_until=decode_until)
            except ValueError:
                data = -1
        except FileNotFoundError: print("not found " + str(files))
        else:
            file_data.append([str(files[0]).replace("." + OLD_BACKUP_EXT, ""), data])
    return file_data

def _get_saves_data():
    """
    main.get_saves_data but for backups
    """

    def _process_file(data:tuple[str, list[str] | Literal[-1]], old_files=False):
        if data[1] == -1:
            if not old_files:
                errored_new.append(data)
            elif data in errored_new:
                errored_both.append(data)
        else:
            try:
                data[1] = json.loads(data[1][0])
                data_processed = ""
                data_processed += f"\"{data[0]}\"{'(old)' if old_files else ''}: {data[1]['player_name']}\n"
                last_access = data[1]["last_access"]
                data_processed += f"Last opened: {make_date(last_access, '.')} {make_time(last_access[3:])}"
                # check version
                try: save_version:str = data[1]["save_version"]
                except KeyError: save_version = "0.0"
                data_processed += stylized_text(f" v.{save_version}", (Color.GREEN if save_version == SAVE_VERSION else Color.RED))
                if old_files:
                    file_number = int(data[0].replace(f".{OLD_BACKUP_EXT}", "").split("save")[1])
                else:
                    file_number = SAVE_SEED
                datas_processed.append([data[0], data_processed, file_number])
            except (TypeError, IndexError):
                press_key(f"\"{data[0]}\" could not be parsed!")

    ts.recreate_backups_folder()
    ts.recreate_saves_folder()
    # read saves
    datas = sfm.file_reader(-1, None, OLD_BACKUP_EXT, BACKUPS_FOLDER_PATH, save_num=SAVE_SEED)
    datas_old = _old_file_reader()
    errored_new = []
    errored_both = []
    # process file data
    datas_processed = []
    for file_data in datas:
        _process_file(file_data)
    for file_data in datas_old:
        _process_file(file_data, True)
    for wrong in errored_both:
        press_key(f"\"{wrong[0]}\" is corrupted!")
    return datas_processed

def load_backup_menu():
    """
    W.I.P. Backup loading menu.
    """
    files_data = _get_saves_data()
    if len(files_data) > 0:
        while True:
            # get data from file_data
            list_data = []
            for data in files_data:
                list_data.append(data[1])
                list_data.append(None)
            option = sfm.UI_list_s(list_data, " Backup loading", True, True, True).display()
            # load
            if option == -1:
                break
            else:
                file_name = str(files_data[int(option)][0])
                save_num = files_data[int(option)][2]
                if recompile_save_file(file_name, file_name, BACKUPS_FOLDER_PATH, SAVES_FOLDER_PATH, OLD_BACKUP_EXT, SAVE_EXT, save_num):
                    press_key("\n" + file_name + " loaded!")
    else:
        press_key("No backups found!")


# thread_1 = threading.Thread(target="function", name="Thread name", args=["argument list"])
# thread_1.start()
# merge main and started thread 1?
# thread_1.join()

class Self_Checks:

    def begin_check(self, check_function:Callable, separate=True):
        check_name = check_function.__name__.capitalize().replace("_", " ")
        if separate:
            ts.log_separator()
        print(end=check_name + "...")
        ts.logger(check_name, "Running...")
        return check_name


    def _give_result(self, check_name:str, result_type=ts.Log_type.FAIL):
        print(result_type.name)
        ts.logger(check_name,
            result_type.name + (": " + str(exc_info()) if result_type==ts.Log_type.FATAL else ""),
            result_type)


    def check(self, check_function:Callable, separate=True):
        ts.threading.current_thread().name = TEST_THREAD_NAME
        check_name = self.begin_check(check_function, separate)

        try:
            check_function(check_name)
        except:
            self._give_result(check_name, ts.Log_type.FATAL)


    def run_all_tests(self):
        ts.log_separator()
        self.check(self.initialization_check, False)
        self.check(self.settings_checks, False)
        # self.check(self.save_file_checks, False)


    def initialization_check(self, check_name:str):
        ts.check_package_versions()

        # GLOBAL VARIABLES
        dm.Settings()
        dm.Settings.update_keybinds()
        dm.Globals(False, False, False, False)
        
        self._give_result(check_name, ts.Log_type.PASS)


    def settings_checks(self, check_name:str):
        good = False
        dm.Settings()
        dm.Settings.update_keybinds()
        
        if dm.Settings.auto_save == True or dm.Settings.auto_save == False:
            if dm.Settings.DOUBLE_KEYS == DOUBLE_KEYS and type(dm.Settings.keybinds) is dict:
                self._give_result(check_name, ts.Log_type.PASS)
                good = True
        if not good:
            self._give_result(check_name, ts.Log_type.FAIL)


    # def save_file_checks(self, check_name:str):
    #     self.give_result(check_name, ts.Log_type.PASS)
    #     self.give_result(check_name, ts.Log_type.FAIL)


class Content_colors(Enum):
    ERROR =         (255, 0, 255, 255)
    EMPTY =         (0, 0, 0, 0)
    RED =           (255, 0, 0, 255)
    GREEN =         (0, 255, 0, 255)
    BLUE =          (0, 0, 255, 255)
    BROWN =         (61, 42, 27, 255)
    SKIN =          (212, 154, 99, 255)
    LIGHT_BLUE =    (60, 60, 255, 255)
    LIGHT_GRAY =    (75, 75, 75, 255)
    LIGHT_BROWN =   (82, 56, 36, 255)
    LIGHTER_BLUE =  (99, 99, 255, 255)
    DARK_GREEN =    (28, 87, 25, 255)


class Terrain_colors(Enum):
    EMPTY = Content_colors.EMPTY.value
    FIELD = Content_colors.DARK_GREEN.value
    MOUNTAIN = Content_colors.LIGHT_GRAY.value
    OCEAN = Content_colors.LIGHT_BLUE.value
    SHORE = Content_colors.LIGHTER_BLUE.value


class Structure_colors(Enum):
    EMPTY = Content_colors.EMPTY.value
    BANDIT_CAMP = Content_colors.RED.value
    VILLAGE = Content_colors.LIGHT_BROWN.value
    KINGDOM = Content_colors.BROWN.value


class Population_colors(Enum):
    EMPTY = Content_colors.EMPTY.value
    HUMAN = Content_colors.SKIN.value
    ELF = Content_colors.DARK_GREEN.value
    DWARF = Content_colors.BROWN.value
    DEMON = Content_colors.RED.value


terrain_type_colors = {
                    Terrain_types.NONE: Terrain_colors.EMPTY,
                    Terrain_types.FIELD: Terrain_colors.FIELD,
                    Terrain_types.MOUNTAIN: Terrain_colors.MOUNTAIN,
                    Terrain_types.OCEAN: Terrain_colors.OCEAN,
                    Terrain_types.SHORE: Terrain_colors.SHORE
                    }
    
structure_type_colors = {
                    Structure_types.NONE: Structure_colors.EMPTY,
                    Structure_types.BANDIT_CAMP: Structure_colors.BANDIT_CAMP,
                    Structure_types.VILLAGE: Structure_colors.VILLAGE,
                    Structure_types.KINGDOM: Structure_colors.KINGDOM
                    }
    
population_type_colors = {
                    Population_types.NONE: Population_colors.EMPTY,
                    Population_types.HUMAN: Population_colors.HUMAN,
                    Population_types.ELF: Population_colors.ELF,
                    Population_types.DWARF: Population_colors.DWARF,
                    Population_types.DEMON: Population_colors.DEMON
                    }


def get_tile_color(tile:Tile, tile_type_counts:dict[str, int], type_colors_map="terrain", opacity_multi=None) -> tuple[dict[str, int], tuple[int, int, int, int]]:
    if type_colors_map == "structure":
        tcm = structure_type_colors
        subtype = tile.structure.subtype
    elif type_colors_map == "population":
        tcm = population_type_colors
        subtype = tile.population.subtype
    else:
        tcm = terrain_type_colors
        subtype = tile.terrain.subtype
    
    try: tile_type_counts[subtype.value] += 1
    except KeyError: tile_type_counts[subtype.value] = 1
    try: t_color:tuple[int, int, int, int] = tcm[subtype].value
    except KeyError: t_color = Content_colors.ERROR.value
    if opacity_multi is None:
        return (tile_type_counts, t_color)
    else:
        return (tile_type_counts, (t_color[0], t_color[1], t_color[2], int(t_color[3] * opacity_multi)))


def draw_world_tiles(type_colors="terrain", image_path="world.png"):
    """
    Genarates an image, representing the different types of tiles, and their placements in the world.\n
    Also returns the tile count for all tile types.\n
    `type_colors` sets witch map to export (terrain, structure, population).
    """
    tile_size = (1, 1)
    
    tile_type_counts = {"TOTAL": 0}
    
    corners = World._get_corners()
    size = ((corners[2] - corners[0] + 1) * tile_size[0], (corners[3] - corners[1] + 1) * tile_size[1])

    im = Image.new("RGBA", size, Content_colors.EMPTY.value)
    draw = ImageDraw.Draw(im, "RGBA")
    for chunk in World.chunks.values():
        for tile in chunk.tiles.values():
            x = (chunk.base_x - corners[0]) + tile.x
            y = (chunk.base_y - corners[1]) + tile.y
            start_x = int(x * tile_size[0])
            start_y = int(y * tile_size[1])
            end_x = int(x * tile_size[0] + tile_size[0] - 1)
            end_y = int(y * tile_size[1] + tile_size[1] - 1)
            # find type
            tile_type_counts["TOTAL"] += 1
            data = get_tile_color(tile, tile_type_counts, type_colors)
            tile_type_counts = data[0]
            draw.rectangle((start_x, start_y, end_x, end_y), data[1])
    im.save(image_path)
    # reorder tile_type_counts
    total = tile_type_counts.pop("TOTAL")
    tile_type_counts["TOTAL"] = total
    return tile_type_counts



def draw_combined_img(image_path="combined.png"):
    """
    Genarates an image, representing the different types of tiles with the layers overlayed, and their placements in the world.\n
    Also returns the tile count for all tile types.
    """
    tile_size = (1, 1)
    
    tile_type_counts = {"TOTAL": 0}

    corners = World._get_corners()
    size = ((corners[2] - corners[0] + 1) * tile_size[0], (corners[3] - corners[1] + 1) * tile_size[1])
    
    def make_transparrent_img(ttc:dict[str, int], type_colors="terrain", opacity=1/3):
        im = Image.new("RGBA", size, Content_colors.EMPTY.value)
        draw = ImageDraw.Draw(im, "RGBA")
        for chunk in World.chunks.values():
            for tile in chunk.tiles.values():
                x = (chunk.base_x - corners[0]) + tile.x
                y = (chunk.base_y - corners[1]) + tile.y
                start_x = int(x * tile_size[0])
                start_y = int(y * tile_size[1])
                end_x = int(x * tile_size[0] + tile_size[0] - 1)
                end_y = int(y * tile_size[1] + tile_size[1] - 1)
                # find type
                ttc["TOTAL"] += 1
                data = get_tile_color(tile, ttc, type_colors, opacity)
                ttc = data[0]
                draw.rectangle((start_x, start_y, end_x, end_y), data[1])
        return im
    

    terrain_img = make_transparrent_img(tile_type_counts, "terrain", 1)
    structure_img = make_transparrent_img(tile_type_counts, "structure", 1/2)
    population_img = make_transparrent_img(tile_type_counts, "population")
    terrain_img.paste(structure_img, (0, 0), structure_img)
    terrain_img.paste(population_img, (0, 0), population_img)

    terrain_img.save(image_path)
    # reorder tile_type_counts
    total = tile_type_counts.pop("TOTAL")
    tile_type_counts["TOTAL"] = total
    return tile_type_counts


"""
def _fill_separated_process(save_folder_path:str, corners:tuple[int, int, int, int]):
    world = cm.World()
    world.gen_tile(corners[0], corners[1])
    world.gen_tile(corners[2], corners[3])
    world.make_rectangle()
    world.fill_all_chunks("Filling chunks...")
    world.save_all_chunks_to_files(save_folder_path, True, "Saving...")


def fill_chunks_separated(save_folder_path:str, corners:tuple[int, int, int, int], split:tuple[int, int]|None=None):
    import multiprocessing as mp
    if split is None:
        sqrt_split = int(math.sqrt(mp.cpu_count()))
        split = (sqrt_split, sqrt_split)
    size = ((corners[2] - corners[0] + 1), (corners[3] - corners[1] + 1))
    split_size_x = int(size[0] / split[0])
    split_size_y = int(size[1] / split[1])
    min_x = corners[0]
    min_y = corners[1]
    max_x = corners[0] + split_size_x - 1
    max_y = corners[1] + split_size_y - 1
    for _ in range(split[0]):
        for _ in range(split[0]):
            this_corners = (min_x, min_y, max_x, max_y)
            process = mp.Process(target=_fill_separated_process, args=[save_folder_path, this_corners])
            process.start()
            _fill_separated_process(save_folder_path, this_corners)
            min_y = min(min_y + split_size_y, corners[3])
            max_y = min(max_y + split_size_y, corners[3])
        min_x = min(min_x + split_size_x, corners[2])
        max_x = min(max_x + split_size_x, corners[2])
"""
    


def save_visualizer(save_name:str):
    """
    Visualises the data in a save file
    """
    EXPORT_FOLDER = "visualised_saves"
    EXPORT_DATA_FILE = "data.txt"
    EXPORT_TERRAIN_FILE = "terrain.png"
    EXPORT_STRUCTURE_FILE = "structure.png"
    EXPORT_POPULATOIN_FILE = "population.png"
    EXPORT_COMBINED_FILE = "combined.png"
    
    ts.threading.current_thread().name = VISUALIZER_THREAD_NAME
    
    
    def make_img(type_colors:str, export_file:str):
        """`type_colors`: terrain, structure or population"""
        print("Generating image...", end="", flush=True)
        tile_type_counts = draw_world_tiles(type_colors, join(visualized_save_path, export_file))
        print("DONE!")
        text =  f"\nTile types:\n"
        for tt, count in tile_type_counts.items():
            text += f"\t{tt}: {count}\n"
        print(text)
    
    def make_combined_img(export_file:str):
        print("Generating image...", end="", flush=True)
        tile_type_counts = draw_combined_img(join(visualized_save_path, export_file))
        print("DONE!")
        text =  f"\nTile types:\n"
        for tt, count in tile_type_counts.items():
            text += f"\t{tt}: {count}\n"
        print(text)
    
    
    try:
        save_folder_path = join(SAVES_FOLDER_PATH, save_name)
        now = datetime.now()
        visualized_save_name = f"{save_name}_{make_date(now)}_{make_time(now, ';')}"
        display_visualized_save_path = join(EXPORT_FOLDER, visualized_save_name)
        visualized_save_path = join(ROOT_FOLDER, display_visualized_save_path)
        
        data = ts.decode_save_s(join(save_folder_path, SAVE_FILE_NAME_DATA, ), 1)
        
        # check save version
        try: save_version = str(data["save_version"])
        except KeyError: save_version = "0.0"
        load_continue = True
        if save_version != SAVE_VERSION:
            is_older = ts.is_up_to_date(save_version, SAVE_VERSION)
            ans = sfm.UI_list(["No", "Yes"], f"\"{save_name}\" is {('an older version' if is_older else 'a newer version')} than what it should be! ({save_version}->{SAVE_VERSION}) Do you want to continue?").display()
            if ans == 0:
                load_continue = False
        # load
        if load_continue:
            # display_name
            display_name = str(data["display_name"])
            # last access
            last_access:list[int] = data["last_access"]
            # player
            player_data:dict[str, Any] = data["player"]
            player = _load_player_json(player_data)
            # seeds
            seeds = data["seeds"]
            main_seed = ts.np.random.RandomState()
            world_seed = ts.np.random.RandomState()
            main_seed.set_state(ts.json_to_random_state(seeds["main_seed"]))
            world_seed.set_state(ts.json_to_random_state(seeds["world_seed"]))
            tile_type_noise_seeds = seeds["tile_type_noise_seeds"]
            Save_data(save_name, display_name, last_access, player, main_seed, world_seed, tile_type_noise_seeds)
            World()
            
            # display
            ttn_seed_txt = str(Save_data.tile_type_noise_seeds).replace(",", ",\n")
            text =  f"---------------------------------------------------------------------------------------------------------------\n"\
                    f"EXPORTED DATA FROM \"{save_name}\"\n"\
                    f"Loaded {SAVE_FILE_NAME_DATA}.{SAVE_EXT}:\n"\
                    f"Save name: {Save_data.save_name}\n"\
                    f"Display save name: {Save_data.display_save_name}\n"\
                    f"Last saved: {make_date(Save_data.last_access, '.')} {make_time(Save_data.last_access[3:])}\n"\
                    f"\nPlayer:\n{Save_data.player}\n"\
                    f"\nMain seed:\n{ts.random_state_to_json(Save_data.main_seed)}\n"\
                    f"\nWorld seed:\n{ts.random_state_to_json(Save_data.world_seed)}\n"\
                    f"\nTile type noise seeds:\n{ttn_seed_txt}"\
                    f"\n---------------------------------------------------------------------------------------------------------------"
            input(text)
            ans = sfm.UI_list(["Yes", "No"], f"Do you want export the data from \"{save_name}\" into \"{join(display_visualized_save_path, EXPORT_DATA_FILE)}\"?").display()
            if ans == 0:
                ts.recreate_folder(EXPORT_FOLDER)
                ts.recreate_folder(visualized_save_name, join(ROOT_FOLDER, EXPORT_FOLDER))
                with open(join(visualized_save_path, EXPORT_DATA_FILE), "a") as f:
                    f.write(text + "\n\n")
            
            ans = sfm.UI_list(["Yes", "No"], f"Do you want export the world data from \"{save_name}\" into an image at \"{display_visualized_save_path}\"?").display()
            if ans == 0:
                ts.recreate_folder(EXPORT_FOLDER)
                ts.recreate_folder(visualized_save_name, join(ROOT_FOLDER, EXPORT_FOLDER))
                # get chunks data
                World.load_all_chunks_from_folder(show_progress_text="Getting chunk data...")
                # fill
                ans = sfm.UI_list(["No", "Yes"], f"Do you want to fill in ALL tiles in ALL generated chunks?").display()
                if ans == 1:
                    ans = sfm.UI_list(["No", "Yes"], f"Do you want to generates the rest of the chunks in a way that makes the world rectangle shaped?").display()
                    if ans == 1:
                        print("Generating chunks...", end="", flush=True)
                        World.make_rectangle()
                        print("DONE!")
                    World.fill_all_chunks("Filling chunks...")
                # generate images
                # terrain
                ans = sfm.UI_list(["Yes", "No"], f"Do you want export the terrain data into \"{EXPORT_TERRAIN_FILE}\"?").display()
                if ans == 0:
                    make_img("terrain", EXPORT_TERRAIN_FILE)
                    input()
                # structure
                ans = sfm.UI_list(["Yes", "No"], f"Do you want export the structure data into \"{EXPORT_STRUCTURE_FILE}\"?").display()
                if ans == 0:
                    make_img("structure", EXPORT_STRUCTURE_FILE)
                    input()
                # population
                ans = sfm.UI_list(["Yes", "No"], f"Do you want export the population data into \"{EXPORT_POPULATOIN_FILE}\"?").display()
                if ans == 0:
                    make_img("population", EXPORT_POPULATOIN_FILE)
                    input()
                ans = sfm.UI_list(["Yes", "No"], f"Do you want export a combined image into \"{EXPORT_COMBINED_FILE}\"?").display()
                if ans == 0:
                    make_combined_img(EXPORT_COMBINED_FILE)
                    input()
    except FileNotFoundError:
        print(f"ERROR: {exc_info()[1]}")
    ts.threading.current_thread().name = MAIN_THREAD_NAME


def fill_world_segmented(save_folder_path:str, corners:tuple[int, int, int, int], save_num:int):
    """
    Generates chunks in a way that makes the world rectangle shaped.\n
    If `save_folder_path` is not None, it will try to load the chunks from the save folder first (calls `load_chunk_from_folder`).\n
    While generating, saves the world `save_num` times.
    HELL!!!
    """
    cl = (((corners[2] + 1) - corners[0]) // CHUNK_SIZE) * (((corners[3] + 1) - corners[1]) // CHUNK_SIZE)
    for x in range(corners[0], corners[2] + 1, CHUNK_SIZE):
        for y in range(corners[1], corners[3] + 1, CHUNK_SIZE):
            World.get_chunk(x, y).fill_chunk()
            print(f"\r({int((cl / save_num) / ((x+1) * (y+1)))}/{save_num})Filling chunks...{round((((x+1) * (y+1)) / save_num + 1) / (cl / save_num) * 100, 1)}%", end="", flush=True)
            if ((x+1) * (y+1)) % int(cl / save_num) == 0:
                print(f"\r({int((cl / save_num) / ((x+1) * (y+1)))}/{save_num})Filling chunks...DONE!           ")
                World.save_all_chunks_to_files(save_folder_path, True, f"({int((cl / save_num) / ((x+1) * (y+1)))}/{save_num})Saving...")
    World.save_all_chunks_to_files(save_folder_path, True, f"(FINAL)Saving...")
    print("DONE!")


def fill_world_simple(corners:tuple[int, int, int, int], save_name:str|None=None):
    """
    Fills all chunks in the world.
    """
    if save_name is None:
        save_name = Save_data.save_name
    save_folder_path = join(SAVES_FOLDER_PATH, save_name)
    World.get_tile(corners[0], corners[2], False, save_folder_path)
    World.get_tile(corners[1], corners[3], False, save_folder_path)
    print("Generating chunks...", end="", flush=True)
    World.make_rectangle(False, save_folder_path)
    print("DONE!")
    World.fill_all_chunks("Filling chunks...")


"""
def gen_named_area(world:cm.World, corners:tuple[int, int, int, int], save_name:str|None=None, show_progress_text:str|None=None):

    Gets all chunks in the specified area and generates a name for the contents.\n
    (as long as the content type is neighbouring the same content type they will have the same name)\n
    Can load chunks from save file if `save_name` is not None.\n
    If `show_progress_text` is not None, it writes out a how many tiles have been name out of the total.
   
    total = (corners[2] - corners[0] + 1) * (corners[3] - corners[1] + 1)
    generated = 0
    save_folder_path = None
    if save_name is not None:
        save_folder_path = join(SAVES_FOLDER_PATH, save_name)
    
    def name_terrain(content:cm.Terrain_content, pos:tuple[int, int]):
        if corners[0] <= pos[0] <= corners[2] and corners[1] <= pos[1] <= corners[3]:
            terrain = world.get_tile(pos[0], pos[1], save_folder_path).terrain
            if terrain.name is None:
                c_type = content.subtype
                c_name = content.name
                content_list = []
                content_list.append(content)
                while len(content_list) != 0:
                    content = content_list.pop(0)
                    if content.subtype == c_type:
                        content.name = c_name
                        
                        
                        
                        if corners[0] <= pos[0] + 1 <= corners[2] and corners[1] <= pos[1] <= corners[3]:
                            name_terrain(terrain, (pos[0] + 1, pos[1]))
                        if corners[0] <= pos[0] - 1 <= corners[2] and corners[1] <= pos[1] <= corners[3]:
                            name_terrain(terrain, (pos[0] - 1, pos[1]))
                        if corners[0] <= pos[0] <= corners[2] and corners[1] <= pos[1] + 1 <= corners[3]:
                            name_terrain(terrain, (pos[0], pos[1] + 1))
                        if corners[0] <= pos[0] <= corners[2] and corners[1] <= pos[1] - 1 <= corners[3]:
                            name_terrain(terrain, (pos[0], pos[1] - 1))
                    else:
                        cm._gen_content_name(terrain)
                        name_terrain(terrain, pos)
                    if show_progress_text is not None:
                        gen = generated
                        gen += 1
                        print(f"\r{show_progress_text}:terrain...{gen}/{total}", end="", flush=True)
    
    1. Set Q to the empty queue or stack.
  2. Add node to the end of Q.
  3. While Q is not empty:
  4.   Set n equal to the first element of Q.
  5.   Remove first element from Q.
  6.   If n is Inside:
         Set the n
         Add the node to the west of n to the end of Q.
         Add the node to the east of n to the end of Q.
         Add the node to the north of n to the end of Q.
         Add the node to the south of n to the end of Q.
  7. Continue looping until Q is exhausted.
  8. Return.
    
    
    def name_structure(content:cm.Structure_content, pos:tuple[int, int]):
        if corners[0] <= pos[0] <= corners[2] and corners[1] <= pos[1] <= corners[3]:
            structure = world.get_tile(pos[0], pos[1], save_folder_path).structure
            if structure.name is None:
                if structure.subtype == content.subtype:
                    structure.subtype = content.subtype
                else:
                    cm._gen_content_name(structure)
                if show_progress_text is not None:
                    gen = generated
                    gen += 1
                    print(f"\r{show_progress_text}:structure...{gen}/{total}", end="", flush=True)
                
                name_structure(structure, (pos[0] + 1, pos[1]))
                name_structure(structure, (pos[0] - 1, pos[1]))
                name_structure(structure, (pos[0], pos[1] + 1))
                name_structure(structure, (pos[0], pos[1] - 1))
    
    
    def name_population(content:cm.Population_content, pos:tuple[int, int]):
        if corners[0] <= pos[0] <= corners[2] and corners[1] <= pos[1] <= corners[3]:
            population = world.get_tile(pos[0], pos[1], save_folder_path).population
            if population.name is None:
                if population.subtype == content.subtype:
                    population.subtype = content.subtype
                else:
                    cm._gen_content_name(population)
                if show_progress_text is not None:
                    gen = generated
                    gen += 1
                    print(f"\r{show_progress_text}:population...{gen}/{total}", end="", flush=True)
                
                name_population(population, (pos[0] + 1, pos[1]))
                name_population(population, (pos[0] - 1, pos[1]))
                name_population(population, (pos[0], pos[1] + 1))
                name_population(population, (pos[0], pos[1] - 1))
    
    starting_pos = (corners[0], corners[2])
    tile = world.get_tile(starting_pos[0], starting_pos[1], save_folder_path)
    # terrain
    print(f"{show_progress_text}:terrain...0/{total}", end="", flush=True)
    name_terrain(tile.terrain, starting_pos)
    print(f"\r{show_progress_text}:terrain...DONE!           ")
    # structure
    print(f"{show_progress_text}:structure...0/{total}", end="", flush=True)
    name_structure(tile.structure, starting_pos)
    print(f"\r{show_progress_text}:structure...DONE!           ")
    # population
    print(f"{show_progress_text}:population...0/{total}", end="", flush=True)
    name_population(tile.population, starting_pos)
    print(f"\r{show_progress_text}:population...DONE!           ")
    # li = [1, 2, 3]
    # print(li.pop(0))
    # print(li.pop(0))
    # print(li.pop(0))
"""


# Self_Checks().run_all_tests()

# for folder in listdir(SAVES_FOLDER_PATH):
#     if isdir(join(SAVES_FOLDER_PATH, folder)):
#         save_visualizer(folder)

# save_visualizer("travel")


# import save_manager as sm
# test_save_name = "ttest"
# sd = dm.Save_data(test_save_name, "test save")
# ts.remove_save(test_save_name, False)
# fill_world_simple(sd.world, (-100, -100, 99, 99), sd.save_name)
# # fill_world_segmented(sd.world, join(SAVES_FOLDER_PATH, sd.save_name), (-100, -100, 99, 99), 10)
# sm.make_save(sd, show_progress_text="Saving...")
# save_visualizer(test_save_name)


import save_manager as sm
test_save_name_2 = "travel"
test_save_name_mod_2 = "travel_2"
sm.load_save(test_save_name_2, dm.Settings().keybind_mapping)
World.load_all_chunks_from_folder(show_progress_text="Loading chunks...")
ts.remove_save(test_save_name_mod_2, False)
fill_world_simple((-100, -100, 99, 99), Save_data.save_name)
Save_data.save_name = test_save_name_mod_2
sm.make_save(show_progress_text="Saving...")
save_visualizer(test_save_name_mod_2)



# from perlin_noise import PerlinNoise
# from matplotlib import pyplot as plt

# # noise4 = PerlinNoise(octaves=2**37, seed=1)
# noise3 = PerlinNoise(octaves=2**36, seed=1)
# noise2 = PerlinNoise(octaves=2**35, seed=1)
# noise = PerlinNoise(octaves=2**34, seed=1)
# offset = 0.0

# xpix, ypix = 500, 500
# pic = []
# for x in range(xpix):
#     row = []
#     for y in range(ypix):
#         noise_val = (noise([(x + TILE_NOISE_RESOLUTION / 2) / TILE_NOISE_RESOLUTION,
#                             (y + TILE_NOISE_RESOLUTION / 2) / TILE_NOISE_RESOLUTION])
#                             )
#         noise_val += (noise2([(x + TILE_NOISE_RESOLUTION / 2) / TILE_NOISE_RESOLUTION,
#                             (y + TILE_NOISE_RESOLUTION / 2) / TILE_NOISE_RESOLUTION])
#                             * 0.5)
#         noise_val += (noise3([(x + TILE_NOISE_RESOLUTION / 2) / TILE_NOISE_RESOLUTION,
#                             (y + TILE_NOISE_RESOLUTION / 2) / TILE_NOISE_RESOLUTION])
#                             * 0.25)
#         noise_val += 0.875
#         noise_val /= 1.75
#         row.append(noise_val)
#     pic.append(row)

# plt.imshow(pic, cmap='gray')
# plt.show()
