from enum import Enum
import json
from os import listdir
from os.path import join, isdir
from sys import exc_info
from typing import Any, Callable, Literal
from zipfile import ZipFile
from datetime import datetime
from PIL import Image, ImageDraw

from utils import Color, make_date, make_time, stylized_text
from constants import                                                                   \
    ENCODING,                                                                           \
    MAIN_THREAD_NAME, TEST_THREAD_NAME, VISUALIZER_THREAD_NAME,                         \
    ROOT_FOLDER,                                                                        \
    SAVES_FOLDER_PATH, SAVE_EXT,                                                        \
    BACKUPS_FOLDER_PATH, OLD_BACKUP_EXT, BACKUP_EXT,                                    \
    SAVE_FILE_NAME_DATA,                                                                \
    SAVE_SEED,                                                                          \
    FILE_ENCODING_VERSION,                                                              \
    SAVE_VERSION, TILE_NOISE_RESOLUTION
import tools as ts
from tools import sfm

import data_manager as dm
import chunk_manager as cm
from save_manager import _load_player_json, load_all_chunks

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
                data = sfm.decode_save(files[1], path.join(dir_name, files[0]), "", decode_until=decode_until)
            except ValueError:
                data = -1
        except FileNotFoundError: print("not found " + str(files))
        else:
            file_data.append([files[0].replace("." + OLD_BACKUP_EXT, ""), data])
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
                ts.press_key(f"\"{data[0]}\" could not be parsed!")

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
        ts.press_key(f"\"{wrong[0]}\" is corrupted!")
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
                    ts.press_key("\n" + file_name + " loaded!")
    else:
        ts.press_key("No backups found!")


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
        GOOD_PACKAGES = True
        SETTINGS = dm.Settings(
            ts.settings_manager("auto_save"),
            ts.settings_manager("logging_level"),
            ts.settings_manager("keybinds"))
        SETTINGS.save_keybind_mapping()
        SAVE_DATA = dm.Save_data
        GLOBALS = dm.Globals(False, False, False, False)
        
        self._give_result(check_name, ts.Log_type.PASS)


    def settings_checks(self, check_name:str):
        good = False
        settings = dm.Settings(
                ts.settings_manager("auto_save"),
                ts.settings_manager("logging_level"),
                ts.settings_manager("keybinds"))
        settings.save_keybind_mapping()
        
        if settings.auto_save == True or settings.auto_save == False:
            if settings.DOUBLE_KEYS == ts.DOUBLE_KEYS and type(settings.keybinds) is dict:
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
                    cm.Terrain_types.NONE: Terrain_colors.EMPTY,
                    cm.Terrain_types.FIELD: Terrain_colors.FIELD,
                    cm.Terrain_types.MOUNTAIN: Terrain_colors.MOUNTAIN,
                    cm.Terrain_types.OCEAN: Terrain_colors.OCEAN,
                    cm.Terrain_types.SHORE: Terrain_colors.SHORE
                    }
    
structure_type_colors = {
                    cm.Structure_types.NONE: Structure_colors.EMPTY,
                    cm.Structure_types.BANDIT_CAMP: Structure_colors.BANDIT_CAMP,
                    cm.Structure_types.VILLAGE: Structure_colors.VILLAGE,
                    cm.Structure_types.KINGDOM: Structure_colors.KINGDOM
                    }
    
population_type_colors = {
                    cm.Population_types.NONE: Population_colors.EMPTY,
                    cm.Population_types.HUMAN: Population_colors.HUMAN,
                    cm.Population_types.ELF: Population_colors.ELF,
                    cm.Population_types.DWARF: Population_colors.DWARF,
                    cm.Population_types.DEMON: Population_colors.DEMON
                    }


def get_tile_color(tile:cm.Tile, tile_type_counts:dict[str, int], type_colors_map="terrain", opacity_multi=None) -> tuple[dict[str, int], tuple[int, int, int, int]]:
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


def draw_world_tiles(world:cm.World, type_colors="terrain", image_path="world.png"):
    """
    Genarates an image, representing the diferent types of tiles, and their placements in the world.\n
    Also returns the tile count for all tile types.\n
    `type_colors` sets witch map to export (terrain, structure, population).
    """
    tile_size = (1, 1)
    
    tile_type_counts = {"TOTAL": 0}
    
    corners = world._get_corners()
    size = ((corners[2] - corners[0] + 1) * tile_size[0], (corners[3] - corners[1] + 1) * tile_size[1])

    im = Image.new("RGBA", size, Content_colors.EMPTY.value)
    draw = ImageDraw.Draw(im, "RGBA")
    for chunk in world.chunks.values():
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



def draw_combined_img(world:cm.World, image_path="combined.png"):
    """
    Genarates an image, representing the diferent types of tiles with the layers overlayed, and their placements in the world.\n
    Also returns the tile count for all tile types.
    """
    tile_size = (1, 1)
    
    tile_type_counts = {"TOTAL": 0}

    corners = world._get_corners()
    size = ((corners[2] - corners[0] + 1) * tile_size[0], (corners[3] - corners[1] + 1) * tile_size[1])
    
    def make_transparrent_img(world:cm.World, ttc:dict[str, int], type_colors="terrain", opacity=1/3):
        im = Image.new("RGBA", size, Content_colors.EMPTY.value)
        draw = ImageDraw.Draw(im, "RGBA")
        for chunk in world.chunks.values():
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
    

    terrain_img = make_transparrent_img(world, tile_type_counts, "terrain", 1)
    structure_img = make_transparrent_img(world, tile_type_counts, "structure", 1/2)
    population_img = make_transparrent_img(world, tile_type_counts, "population")
    terrain_img.paste(structure_img, (0, 0), structure_img)
    terrain_img.paste(population_img, (0, 0), population_img)

    terrain_img.save(image_path)
    # reorder tile_type_counts
    total = tile_type_counts.pop("TOTAL")
    tile_type_counts["TOTAL"] = total
    return tile_type_counts


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
        tile_type_counts = draw_world_tiles(save_data.world, type_colors, join(visualized_save_path, export_file))
        print("DONE!")
        text =  f"\nTile types:\n"
        for tt, count in tile_type_counts.items():
            text += f"\t{tt}: {count}\n"
        print(text)
    
    def make_combined_img(export_file:str):
        print("Generating image...", end="", flush=True)
        tile_type_counts = draw_combined_img(save_data.world, join(visualized_save_path, export_file))
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
            save_data = dm.Save_data(save_name, display_name, last_access, player, main_seed, world_seed, tile_type_noise_seeds)
            
            # display
            ttn_seed_txt = str(save_data.tile_type_noise_seeds).replace(",", ",\n")
            text =  f"---------------------------------------------------------------------------------------------------------------\n"\
                    f"EXPORTED DATA FROM \"{save_name}\"\n"\
                    f"Loaded {SAVE_FILE_NAME_DATA}.{SAVE_EXT}:\n"\
                    f"Save name: {save_data.save_name}\n"\
                    f"Display save name: {save_data.display_save_name}\n"\
                    f"Last saved: {make_date(save_data.last_access, '.')} {make_time(save_data.last_access[3:])}\n"\
                    f"\nPlayer:\n{save_data.player}\n"\
                    f"\nMain seed:\n{ts.random_state_to_json(save_data.main_seed)}\n"\
                    f"\nWorld seed:\n{ts.random_state_to_json(save_data.world_seed)}\n"\
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
                load_all_chunks(save_data, "Getting chunk data...")
                # fill
                ans = sfm.UI_list(["No", "Yes"], f"Do you want to fill in ALL tiles in ALL generated chunks?").display()
                if ans == 1:
                    ans = sfm.UI_list(["No", "Yes"], f"Do you want to generates the rest of the chunks in a way that makes the world rectangle shaped?").display()
                    if ans == 1:
                        print("Generating chunks...", end="", flush=True)
                        save_data.world.make_rectangle()
                        print("DONE!")
                    save_data.world.fill_all_chunks("Filling chunks...")
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


# Self_Checks().run_all_tests()

# for folder in listdir(SAVES_FOLDER_PATH):
#     if isdir(join(SAVES_FOLDER_PATH, folder)):
#         save_visualizer(folder)

# save_visualizer("new sav")


# import entities as es
# import save_manager as sm
# mseed = ts.np.random.RandomState()
# wseed = ts.make_random_seed(mseed)
# sd = dm.Save_data("test", "test save", [0, 0, 0, 0, 0, 0], es.Player(), mseed, wseed, ts.recalculate_tile_type_noise_seeds(wseed))
# sd.world.gen_tile(-100, -100)
# sd.world.gen_tile(99, 99)
# sd.world.make_rectangle()
# sd.world.fill_all_chunks("Filling chunks...")
# ts.remove_save("test", False)
# sm.make_save(sd, show_progress_text="Saving...")
# save_visualizer("test")

"""
(make_rectangle + fill + save) in n parts
"""

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
