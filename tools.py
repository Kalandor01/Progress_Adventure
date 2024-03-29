from enum import Enum
import json
import os
from shutil import copyfile, rmtree
import threading
from datetime import datetime as dtime
from typing import Any
import numpy as np
import colorama as col
from zipfile import ZipFile
from copy import deepcopy
from perlin_noise import PerlinNoise

import save_file_manager as sfm

import utils as u
from constants import                                                   \
    PYTHON_MIN_VERSION,                                                 \
    PIP_NP_MIN_VERSION, PIP_COL_MIN_VERSION,                            \
    PIP_PIL_MIN_VERSION, PIP_PERLIN_MIN_VERSION,                         \
    PIP_SFM_MIN_VERSION, PIP_RS_MIN_VERSION,                            \
    ROOT_FOLDER,                                                        \
    SAVES_FOLDER, SAVES_FOLDER_PATH, OLD_SAVE_NAME, SAVE_EXT,           \
    LOGGING, LOGGING_LEVEL, LOGS_FOLDER, LOGS_FOLDER_PATH, LOG_EXT,     \
    BACKUPS_FOLDER, BACKUPS_FOLDER_PATH, OLD_BACKUP_EXT, BACKUP_EXT,    \
    SAVE_SEED, SETTINGS_SEED, SETTINGS_FILE_NAME,                       \
    LOG_MS,                                                             \
    FILE_ENCODING_VERSION
from keybinds import Action_keybinds, Action_key, keybinds_from_json, get_def_keybinds


# random
def make_random_seed(parrent_seed:np.random.RandomState):
    """Returns a new numpy.RandomState from another numpy.RandomState."""
    return np.random.RandomState(int(parrent_seed.rand() * 4294967296))


main_seed = np.random.RandomState()
world_seed = make_random_seed(main_seed)


def make_perlin_noise_seed(parrent_seed:np.random.RandomState=world_seed):
    """Returns a seed for a perlin noise."""
    return int(parrent_seed.rand() * 10000000000000000)


def recalculate_tile_type_noise_seeds(parrent_seed:np.random.RandomState=world_seed):
    """Recalculate seeds for perlin noise generators."""
    hostility_seed = make_perlin_noise_seed(parrent_seed)
    height_seed = make_perlin_noise_seed(parrent_seed)
    temperature_seed = make_perlin_noise_seed(parrent_seed)
    humidity_seed = make_perlin_noise_seed(parrent_seed)
    population_seed = make_perlin_noise_seed(parrent_seed)
    ttn_seeds = {
        "height": height_seed,
        "temperature": temperature_seed,
        "humidity": humidity_seed,
        "hostility": hostility_seed,
        "population": population_seed
    }
    return ttn_seeds


def recalculate_noise_generators(ttn_seeds:dict[str, int]):
    """Recalculate perlin noise generators for `tile_type_noise_seeds`."""
    height1 = PerlinNoise(octaves=2**35, seed=ttn_seeds["height"])
    height2 = PerlinNoise(octaves=2**36, seed=ttn_seeds["height"])
    height3 = PerlinNoise(octaves=2**37, seed=ttn_seeds["height"])
    temperature1 = PerlinNoise(octaves=2**34, seed=ttn_seeds["temperature"])
    temperature2 = PerlinNoise(octaves=2**35, seed=ttn_seeds["temperature"])
    temperature3 = PerlinNoise(octaves=2**36, seed=ttn_seeds["temperature"])
    humidity1 = PerlinNoise(octaves=2**34, seed=ttn_seeds["humidity"])
    humidity2 = PerlinNoise(octaves=2**35, seed=ttn_seeds["humidity"])
    humidity3 = PerlinNoise(octaves=2**36, seed=ttn_seeds["humidity"])
    hostility1 = PerlinNoise(octaves=2**36, seed=ttn_seeds["hostility"])
    hostility2 = PerlinNoise(octaves=2**37, seed=ttn_seeds["hostility"])
    hostility3 = PerlinNoise(octaves=2**38, seed=ttn_seeds["hostility"])
    population1 = PerlinNoise(octaves=2**36, seed=ttn_seeds["population"])
    population2 = PerlinNoise(octaves=2**37, seed=ttn_seeds["population"])
    population3 = PerlinNoise(octaves=2**38, seed=ttn_seeds["population"])
    
    tile_type_noises = {
        "height": (height1, height2, height3),
        "temperature": (temperature1, temperature2, temperature3),
        "humidity": (humidity1, humidity2, humidity3),
        "hostility": (hostility1, hostility2, hostility3),
        "population": (population1, population2, population3)
    }
    return tile_type_noises


# perlin noise variables
tile_type_noise_seeds:dict[str, int] = recalculate_tile_type_noise_seeds(world_seed)
noise_generators = recalculate_noise_generators(tile_type_noise_seeds)


class Log_type(Enum):
    DEBUG   = 0
    INFO    = 1
    WARN    = 2
    ERROR   = 3
    FATAL   = 4
    PASS    = 5
    FAIL    = 6
    OTHER   = 7


def write_as_json(data:list[dict[str, Any]]|dict[str, Any], file_path:str):
    """
    Writes to unencoded file + convert from json dict to string.
    """
    # convert from json to string
    if type(data) is dict:
        json_data = [json.dumps(data)]
    else:
        json_data:list[str] = []
        for dat in data:
            json_data.append(json.dumps(dat))
    
    with (open(file_path + ".json", "w")) as f:
        for line in json_data:
            f.write(line + "\n")


def encode_save_s(data:list[dict[str, Any]]|dict[str, Any], file_path:str, seed=SAVE_SEED, extension=SAVE_EXT):
    """
    Shorthand for `sfm.encode_save` + convert from json to string.
    """
    # convert from json to string
    if type(data) is dict:
        json_data = [json.dumps(data)]
    else:
        json_data:list[str] = []
        for dat in data:
            json_data.append(json.dumps(dat))
    
    sfm.encode_save(json_data, seed, file_path, extension, FILE_ENCODING_VERSION)


def decode_save_s(file_path:str, line_num=0, seed=SAVE_SEED, extension=SAVE_EXT, can_be_old=False) -> dict[str, Any]:
    """
    Shorthand for `sfm.decode_save` + convert from string to json.\n
    `line_num` is the line, that you want go get back (starting from 0).
    """
    try:
        decoded_lines = sfm.decode_save(seed, file_path, extension, line_num + 1)
    except ValueError:
        safe_file_path = file_path.removeprefix(ROOT_FOLDER)
        logger("Decode error", f"file name: {safe_file_path}.{SAVE_EXT}", Log_type.ERROR)
        if can_be_old:
            logger("Decode backup", "trying to decode file as a numbered save file")
            save_name = str(os.path.basename(file_path))
            old_save_removable = OLD_SAVE_NAME.replace("*", "")
            file_number = int(save_name.replace(old_save_removable, ""))
            decoded_lines = sfm.decode_save(file_number, file_path, extension, line_num + 1)
        else:
            raise
    except FileNotFoundError:
        safe_file_path = file_path.removeprefix(ROOT_FOLDER)
        logger("File not found", f"file name: {safe_file_path}.{SAVE_EXT}", Log_type.ERROR)
        raise
    return json.loads(decoded_lines[line_num])


def sfm_choice_s(choice_list:list|range, value=0, pre_text="", pre_value="", display_value=False, post_value="", multiline=False):
    """`sfm.Choice()`, but adds <> around the answer to signal that it is a choice."""
    return sfm.Choice(choice_list, value, pre_text + "<", ">" + pre_value, display_value, post_value, multiline)


def change_logging_level(value:int):
    """
    Sets the `LOGGING_LEVEL`, and if logging is enabled or not.
    """
    global LOGGING_LEVEL
    if LOGGING_LEVEL != value:
        # logging level
        old_logging_level = LOGGING_LEVEL
        LOGGING_LEVEL = value
        logger("Logging level changed", f"{old_logging_level} -> {LOGGING_LEVEL}")
        # logging
        global LOGGING
        old_logging = LOGGING
        LOGGING = (value != -1)
        if LOGGING != old_logging:
            logger(f"Logging {'enabled' if LOGGING else 'disabled'}")


def log_separator():
    """
    Puts a newline in the logs.
    """
    try:
        if LOGGING:
            recreate_logs_folder()
            with open(os.path.join(LOGS_FOLDER_PATH, f"{u.make_date(dtime.now())}.{LOG_EXT}"), "a") as f:
                f.write("\n")
    except:
        if LOGGING:
            with open(os.path.join(ROOT_FOLDER, "CRASH.log"), "a") as f:
                f.write(f"\n[{u.make_date(dtime.now())}_{u.make_time(dtime.now(), write_ms=True)}] [CRASH]\t: |Logging error|\n")


def logger(message:str, detail="", log_type=Log_type.INFO, write_out=False, new_line=False):
    """
    Progress Adventure logger.
    """
    try:
        if LOGGING and LOGGING_LEVEL <= log_type.value:
            l_type = log_type.name
            current_date = u.make_date(dtime.now())
            current_time = u.make_time(dtime.now(), write_ms=LOG_MS)
            recreate_logs_folder()
            with open(os.path.join(LOGS_FOLDER_PATH, f"{current_date}.{LOG_EXT}"), "a") as f:
                if new_line:
                    f.write("\n")
                f.write(f"[{current_time}] [{threading.current_thread().name}/{l_type}]\t: |{message}| {detail}\n")
            if write_out:
                if new_line:
                    print("\n")
                print(f'{os.path.join(LOGS_FOLDER, f"{current_date}.{LOG_EXT}")} -> [{current_time}] [{threading.current_thread().name}/{l_type}]\t: |{message}| {detail}')
    except:
        if LOGGING:
            with open(os.path.join(ROOT_FOLDER, "CRASH.log"), "a") as f:
                f.write(f"\n[{u.make_date(dtime.now())}_{u.make_time(dtime.now(), write_ms=True)}] [CRASH]\t: |Logging error|\n")


def recreate_folder(folder_name:str, parent_folder_path:str=ROOT_FOLDER, display_name:str|None=None):
    """
    Recreates the folder, if it doesn't exist.\n
    Returns if the folder needed to be recreated.
    """
    folder_path = os.path.join(parent_folder_path, folder_name)
    if display_name is None:
        display_name = folder_name.lower()
    if not os.path.isdir(folder_path):
        os.mkdir(folder_path)
        logger(f"Recreating {display_name} folder")
        return True
    else:
        return False

def recreate_saves_folder():
    """
    `recreate_folder` for the saves folder.
    """
    return recreate_folder(SAVES_FOLDER)

def recreate_backups_folder():
    """
    `recreate_folder` for the backups folder.
    """
    return recreate_folder(BACKUPS_FOLDER)

def recreate_logs_folder():
    """
    `recreate_folder` for the logs folder.
    """
    return recreate_folder(LOGS_FOLDER)


def make_zip(save_name:str, save_name_path:str, full_zip_name:str):
    """
    Makes a zip archive from a save folder.
    """
    with ZipFile(full_zip_name, 'w') as zf:
        for root, dirs, files in os.walk(save_name_path):
            for dir in dirs:
                dir_name = os.path.join(root, dir)
                ar2 = os.path.join(save_name_path, '..')
                arc_name = os.path.relpath(dir_name, ar2).removeprefix(save_name + os.sep)
                zf.write(dir_name, arc_name)
            for file in files:
                file_name = os.path.join(root, file)
                ar2 = os.path.join(save_name_path, '..')
                arc_name = os.path.relpath(file_name, ar2).removeprefix(save_name + os.sep)
                zf.write(file_name, arc_name)


def make_backup(save_name:str, is_temporary=False):
    """
    Makes a backup of a save from the saves folder into the backups folder (as a zip file).\n
    Returns the name of the backup normaly, and in a way that doesn't contain the root directories.
    """
    # recreate folders
    recreate_saves_folder()
    recreate_backups_folder()
    now = dtime.now()

    # make common variables
    save_folder_path = os.path.join(SAVES_FOLDER_PATH, save_name)
    save_file_path = f'{save_folder_path}.{SAVE_EXT}'
    if os.path.isdir(save_folder_path) or os.path.isfile(save_file_path):
        # make more variables
        backup_name_end = f'{u.make_date(now)};{u.make_time(now, "-", is_temporary, "-")};{save_name}.{OLD_BACKUP_EXT if os.path.isfile(save_file_path) else BACKUP_EXT}'
        backup_name = os.path.join(BACKUPS_FOLDER_PATH, backup_name_end)
        display_backup_name = os.path.join(BACKUPS_FOLDER, backup_name_end)
        # file copy
        if os.path.isfile(save_file_path):
            copyfile(save_file_path, backup_name)
        # make zip
        else:
            make_zip(save_name, save_folder_path, backup_name)
        logger(f"Made {('temporary ' if is_temporary else '')}backup", display_backup_name, (Log_type.DEBUG if is_temporary else Log_type.INFO))
        return [backup_name, display_backup_name]
    else:
        display_save_path = os.path.join(SAVES_FOLDER, save_name)
        logger(f"{'Temporary b' if is_temporary else 'B'}ackup failed", f"save file/folder not found: {display_save_path}(.{SAVE_EXT})", Log_type.WARN)
        return False


class Settings_keys(Enum):
    AUTO_SAVE = "auto_save"
    LOGGING_LEVEL = "logging_level"
    KEYBINDS = "keybinds"
    ASK_PACKAGE_CHECK_FAIL = "ask_package_check_fail"
    ASK_DELETE_SAVE = "ask_delete_save"
    ASK_REGENERATE_SAVE = "ask_regenerate_save"
    DEF_BACKUP_ACTION = "def_backup_action"


def settings_manager(line_name:Settings_keys|None=None, write_value:Any=None):
    """
    STRUCTURE:\n
    - auto_save: bool
    - logging_level: int
    - keybinds: dict[str, list[list[str]]]
    \t- esc
    \t- up
    \t- down
    \t- left
    \t- right
    \t- enter
    - ask_package_check_fail: bool
    - ask_delete_save: bool
    - ask_regenerate_save: bool
    - def_backup_action: int
    """

    # default values
    def_settings:dict[str, Any] = {
        Settings_keys.AUTO_SAVE.value: True,
        Settings_keys.LOGGING_LEVEL.value: 0,
        Settings_keys.KEYBINDS.value: "[KEYBINDS OBJECT PLACEHOLDER]",
        Settings_keys.ASK_PACKAGE_CHECK_FAIL.value: True,
        Settings_keys.ASK_DELETE_SAVE.value: True,
        Settings_keys.ASK_REGENERATE_SAVE.value: True,
        Settings_keys.DEF_BACKUP_ACTION.value: -1
    }

    def recreate_settings():
        """Recreates the settings file from the default values, and returns the result."""
        new_settings = deepcopy(def_settings)
        new_settings[Settings_keys.KEYBINDS.value] = get_def_keybinds().to_json()
        encode_save_s(new_settings, os.path.join(ROOT_FOLDER, SETTINGS_FILE_NAME), SETTINGS_SEED)
        # log
        logger("Recreated settings")
        return new_settings


    try:
        settings = decode_save_s(os.path.join(ROOT_FOLDER, SETTINGS_FILE_NAME), 0, SETTINGS_SEED)
    except (ValueError, TypeError):
        logger("Decode error", "settings", Log_type.ERROR)
        u.press_key("The settings file is corrupted, and will now be recreated!")
        settings = recreate_settings()
    except FileNotFoundError:
        settings = recreate_settings()
    if line_name is not None:
        # return
        if write_value is None:
            try:
                if line_name == Settings_keys.KEYBINDS:
                    settings[Settings_keys.KEYBINDS.value] = keybinds_from_json(settings[Settings_keys.KEYBINDS.value])
                return settings[line_name.value]
            except KeyError:
                if line_name.name in Settings_keys._member_names_:
                    logger("Missing key in settings", line_name.name, Log_type.WARN)
                    if line_name == Settings_keys.KEYBINDS:
                        def_settings[Settings_keys.KEYBINDS.value] = get_def_keybinds()
                    settings_manager(line_name, def_settings[line_name.value])
                    return deepcopy(def_settings[line_name.value])
                else:
                    raise
        # write
        else:
            if line_name.value in settings.keys():
                if line_name == Settings_keys.KEYBINDS:
                    if isinstance(write_value, Action_keybinds):
                        write_value = write_value.to_json()
                    else:
                        raise TypeError(write_value)
                if settings[line_name.value] != write_value:
                    print(settings[line_name.value])
                    print(write_value)
                    logger("Changed settings", f"{line_name.name}: {settings[line_name.value]} -> {write_value}", Log_type.DEBUG)
                    settings[line_name.value] = write_value
                    encode_save_s(settings, os.path.join(ROOT_FOLDER, SETTINGS_FILE_NAME), SETTINGS_SEED)
            else:
                if line_name.name in Settings_keys._member_names_:
                    logger("Recreating key in settings", line_name.name, Log_type.WARN)
                    if line_name == Settings_keys.KEYBINDS:
                        def_settings[Settings_keys.KEYBINDS.value] = get_def_keybinds().to_json()
                    settings[line_name.value] = def_settings[line_name.value]
                    encode_save_s(settings, os.path.join(ROOT_FOLDER, SETTINGS_FILE_NAME), SETTINGS_SEED)
                else:
                    raise KeyError(line_name)
    else:
        return settings


def random_state_to_json(random_state:np.random.RandomState|tuple):
    """
    Converts a numpy RandomState(.getstate()) into a json format.
    """
    if isinstance(random_state, np.random.RandomState):
        state:tuple = tuple(random_state.get_state())
    else:
        state:tuple = random_state
    state_nums = []
    for num in state[1]:
        state_nums.append(int(num))
    return {"type": state[0], "state": state_nums, "pos": state[2], "has_gauss": state[3], "cached_gaussian": state[4]}


def json_to_random_state(random_state:dict[str, Any]):
    """
    Converts a json formated numpy RandomState.getstate() into a numpy RandomState.getstate().
    """
    states = [int(num) for num in random_state["state"]]
    return (str(random_state["type"]), np.array(states, dtype=np.uint32), int(random_state["pos"]), int(random_state["has_gauss"]), float(random_state["cached_gaussian"]))


def is_up_to_date(min_version:str, curr_version:str):
    """
    Returns if the current version string is equal or higher than the minimum version.
    """
    version = str(curr_version).split(".")
    min_v = str(min_version).split(".")

    for x in range(len(version)):
        # min v. shorter
        if len(min_v) < (x + 1):
            return True
        # print(f"{version[x]} >=? {min_v[x]}")
        # v. > min v. ?
        if int(version[x]) > int(min_v[x]):
            return True
        # v. < min v. ?
        elif int(version[x]) < int(min_v[x]):
            return False
    # v. shorter
    return True


def _package_response(bad_packages:list, py_good:bool):
    # python
    if py_good:
        logger("Python up to date")
    else:
        from platform import python_version
        logger("Python not up to date", f"{python_version()} -> {PYTHON_MIN_VERSION}", Log_type.WARN)
        print(f"Python not up to date: {python_version()} -> {PYTHON_MIN_VERSION}")
    # packages
    if len(bad_packages) == 0:
        logger("All packages up to date")
    else:
        bad_packages_str = []
        for package in bad_packages:
            bad_packages_str.append(f"{package[2]}({package[1]}) -> {package[0]}")
        logger("Some packages are not up to date", ", ".join([p for p in bad_packages_str]), Log_type.WARN)
        print(f"{'Some packages are' if len(bad_packages) > 1 else 'A package is'} not up to date:\n\t" + "\n\t".join([p for p in bad_packages_str]))
    # return
    if len(bad_packages) == 0 and py_good:
        return True
    # BAD BUT WORKS???!
    elif not bool(settings_manager(Settings_keys.ASK_PACKAGE_CHECK_FAIL)):
        return True
    else:
        ans = input("Do you want to continue?(Y/N): ")
        if ans.upper() == "Y":
            logger("Continuing anyways")
            return True
        else:
            return False

def check_package_versions():
    """
    Checks if all tested packages and python are up do date.\n
    Checks:
    - python
    - numpy
    - colorama
    - Pillow
    - perlin-noise
    - Save File Manager
    - random sentance
    """
    from importlib.metadata import version
    from platform import python_version
    import random_sentance as rs
    import PIL
    import perlin_noise as perlin

    logger("Checking python version")
    py_good = True
    if not is_up_to_date(PYTHON_MIN_VERSION, python_version()):
        py_good = False
    logger("Checking package versions")
    packages = [[PIP_NP_MIN_VERSION, np.__version__, "numpy"],
                [PIP_COL_MIN_VERSION, col.__version__, "colorama"],
                [PIP_PIL_MIN_VERSION, PIL.__version__, "Pillow"],
                [PIP_PERLIN_MIN_VERSION, version("perlin-noise"), "perlin-noise"],
                [PIP_SFM_MIN_VERSION, sfm.__version__, "Save File Manager"],
                [PIP_RS_MIN_VERSION, rs.__version__, "Random Sentance"]]

    bad_packages = []
    for package in packages:
        if not is_up_to_date(package[0], package[1]):
            bad_packages.append(package)
    return _package_response(bad_packages, py_good)


def _check_save_name(save_name:str):
    """
    Checks if the file name exists in the saves directory.
    """
    if not recreate_saves_folder():
        is_folder = os.path.isdir(os.path.join(SAVES_FOLDER_PATH, save_name))
        is_file = os.path.isfile(os.path.join(SAVES_FOLDER_PATH, f"{save_name}.{SAVE_EXT}"))
        return is_folder or is_file
    else:
        return False

def correct_save_name(raw_save_name:str):
    save_name = u.remove_bad_characters(raw_save_name)
    if save_name == "":
        save_name = "new_save"
    if _check_save_name(save_name):
        extra_num = 1
        while _check_save_name(save_name + "_" + str(extra_num)):
            extra_num += 1
        save_name += "_" + str(extra_num)
    return save_name


def remove_save(save_name:str, is_file:bool|None=None):
    removed = False
    if (is_file is None or is_file) and os.path.isfile(f'{os.path.join(SAVES_FOLDER_PATH, save_name)}.{SAVE_EXT}'):
        os.remove(f'{os.path.join(SAVES_FOLDER_PATH, save_name)}.{SAVE_EXT}')
        removed = True
    elif(is_file is None or not is_file) and os.path.isdir(os.path.join(SAVES_FOLDER_PATH, save_name)):
        rmtree(os.path.join(SAVES_FOLDER_PATH, save_name))
        removed = True
    if removed:
        logger("Deleted save", f'save name: {save_name}')
