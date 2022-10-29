from enum import Enum
import json
import os
import shutil
import threading
from datetime import datetime as dtime
from msvcrt import getch
from typing import Any
import numpy as np

import save_file_manager as sfm

import utils as u


# random
r = np.random.RandomState()

# package versions
PYTHON_MIN_VERSION = "3.11.0"
PIP_NP_MIN_VERSION = "1.23.4"

PIP_SFM_MIN_VERSION = "1.12.2.2"
PIP_RS_MIN_VERSION = "1.5.1"
# language
ENCODING = "windows-1250"
# thread names
MAIN_THREAD_NAME = "Main"
AUTO_SAVE_THREAD_NAME = "Auto saver"
MANUAL_SAVE_THREAD_NAME = "Quit manager"
TEST_THREAD_NAME = "Test"
# paths/folders/file names
ROOT_FOLDER = os.path.dirname(os.path.abspath(__file__))
    #saves folder
SAVES_FOLDER = "saves"
SAVES_FOLDER_PATH = os.path.join(ROOT_FOLDER, SAVES_FOLDER)
SAVE_EXT = "sav"
    #logs folder
LOGGING = True
LOGS_FOLDER = "logs"
LOGS_FOLDER_PATH = os.path.join(ROOT_FOLDER, LOGS_FOLDER)
LOG_EXT = "log"
    #backups folder
BACKUPS_FOLDER = "backups"
BACKUPS_FOLDER_PATH = os.path.join(ROOT_FOLDER, BACKUPS_FOLDER)
OLD_BACKUP_EXT = SAVE_EXT + ".bak"
BACKUP_EXT = "zip"
    # save folder structure
SAVE_FILE_NAME_DATA = "data"
SAVE_FOLDER_NAME_CHUNKS = "chunks"
# seeds
SAVE_SEED = 87531
SETTINGS_SEED = 1
# other
AUTO_SAVE_DELAY = 3
FILE_ENCODING_VERSION = 2
DOUBLE_KEYS = [b"\xe0", b"\x00"]
LOG_MS = False
SAVE_VERSION = 1.3
STANDARD_CURSOR_ICONS = sfm.Cursor_icon(selected_icon=">", selected_icon_right="",
                                        not_selected_icon=" ", not_selected_icon_right="")
DELETE_CURSOR_ICONS = sfm.Cursor_icon(selected_icon=" X", selected_icon_right="",
                                        not_selected_icon="  ", not_selected_icon_right="")


class Log_type(Enum):
    INFO    = 0
    WARN    = 1
    ERROR   = 2
    CRASH   = 3
    OTHER   = 4


def encode_save_s(data:list[dict]|dict, file_path:str, seed=SAVE_SEED, extension=SAVE_EXT):
    """
    Shorthand for `sfm.encode_save` + convert from json to string.
    """
    # convert from json to string
    if type(data) is dict:
        json_data = json.dumps(data)
    else:
        json_data = []
        for dat in data:
            json_data.append(json.dumps(dat))
        
    sfm.encode_save(json_data, seed, file_path, extension, ENCODING, FILE_ENCODING_VERSION)


def decode_save_s(file_path, line_num=0, seed=SAVE_SEED, extension=SAVE_EXT) -> dict:
    """
    Shorthand for `sfm.decode_save` + convert from string to json.\n
    `line_num` is the line, that you want go get back (starting from 0).
    """
    return json.loads(sfm.decode_save(seed, file_path, extension, ENCODING, line_num + 1)[line_num])


def change_logging(value:bool):
    global LOGGING
    if LOGGING != value:
        if value:
            LOGGING = value
            log_info("Logging enabled")
        else:
            log_info("Logging disabled")
            LOGGING = value


def begin_log():
    if LOGGING:
        current_date = u.make_date(dtime.now())
        recreate_logs_folder()
        with open(os.path.join(LOGS_FOLDER_PATH, f"{current_date}.{LOG_EXT}"), "a") as f:
            f.write("\n")


def log_info(message:str, detail="", log_type=Log_type.INFO, write_out=False, new_line=False):
    """
    Progress Adventure logger.
    """
    try:
        if LOGGING:
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


def recreate_folder(folder_name:str, parent_folder_path:str=ROOT_FOLDER, display_name:str=None):
    """
    Recreates the folder, if it doesn't exist.\n
    Returns if the folder needed to be recreated.
    """
    folder_path = os.path.join(parent_folder_path, folder_name)
    if display_name == None:
        display_name = folder_name.lower()
    if not os.path.isdir(folder_path):
        os.mkdir(folder_path)
        log_info(f"Recreating {display_name} folder")
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
    save_file = f'{os.path.join(SAVES_FOLDER_PATH, save_name)}.{SAVE_EXT}'
    save_folder = os.path.join(SAVES_FOLDER_PATH, save_name)
    display_save_path = f'{os.path.join(SAVES_FOLDER, save_name)}'
    if os.path.isdir(save_folder) or os.path.isfile(save_file):
        # make more variables
        if os.path.isfile(save_file):
            backup_name_end = f'{u.make_date(now)};{u.make_time(now, "-", is_temporary, "-")};{save_name}.{OLD_BACKUP_EXT}'
        else:
            backup_name_end = f'{u.make_date(now)};{u.make_time(now, "-", is_temporary, "-")};{save_name}.{BACKUP_EXT}'

        backup_name = os.path.join(BACKUPS_FOLDER_PATH, backup_name_end)
        display_backup_name = os.path.join(BACKUPS_FOLDER, backup_name_end)
        # file copy
        if os.path.isfile(save_file):
            shutil.copyfile(save_file, backup_name)
        # make zip
        else:
            # REWORK SO IT'S SIMPLER!!!            
            base = os.path.basename(backup_name)
            name = base.split('.')[0]
            archive_from = os.path.dirname(save_folder)
            archive_to = os.path.basename(save_folder.strip(os.sep))
            shutil.make_archive(name, BACKUP_EXT, archive_from, archive_to)
            shutil.move('%s.%s'%(name,BACKUP_EXT), backup_name)
        log_info(f"Made {('temporary ' if is_temporary else ' ')}backup", display_backup_name)
        return [backup_name, display_backup_name]
    else:
        log_info("Backup failed", f"save file/folder not found: {display_save_path}(.{SAVE_EXT})", Log_type.WARN)
        return False


# FILE_DATA_MERGER ABANDONED!!!
    """
    # -1: add only if there is nothing in the list? (NO!)
    # 1: don't remove if there is extra stuff in list (success!?)

    # ULTIMATE MIND DESTRUCTION!!!
    def file_data_merger_special(def_data:list|dict, file_data:list|dict, index:int|str, list_type:type):
        code = def_data["file_merger_code"]
        value = def_data["file_merger_value"]
        print("good:", def_data, file_data)
        if code == -1:
            if len(file_data) == 0:
                merged_data = value
            else:
                if len(file_data) < index:
                    merged_data = file_data[index]
                else:
                    merged_data = {"file_merger_nothing_to_add": None}
        elif code == 1:
            merged_data = file_data[index]
        print("merged:", merged_data)
        return merged_data

    def is_good(data:list|dict, write=False):
        good = (type(data) is dict and "file_merger_code" in data.keys() and "file_merger_value" in data.keys() and data["file_merger_code"] != 0)
        if write:
            print(f"{data}:", good)
        return good

    def file_data_merger(def_data:list|dict, file_data:list|dict):
        def_data_c = copy.deepcopy(def_data)
        if type(def_data_c) is list:
            merged_data = []
            for x in range(len(def_data_c)):
                print("\nlist", type(def_data_c[x]))
                good = is_good(def_data_c[x], True)
                try:
                    if type(def_data_c[x]) is list or type(def_data_c[x]) is dict:
                        if good:
                            sp_merge = file_data_merger_special(def_data_c[x], file_data, x, list)
                            if sp_merge != {"file_merger_nothing_to_add": None}:
                                merged_data.append()
                        else:
                            merged_data.append(file_data_merger(def_data_c[x], file_data[x]))
                    else:
                        merged_data.append(file_data[x])
                except IndexError:
                    print("error")
                    merged_data.append(def_data_c[x])
        else:
            merged_data = {}
            for key in def_data_c:
                print("\ndict", type(def_data_c[key]))
                good = is_good(def_data_c[key], True)
                try:
                    if type(def_data_c[key]) is list or type(def_data_c[key]) is dict:
                        if good:
                            merged_data[key] = file_data_merger_special(def_data_c[key], file_data, key, dict)
                        else:
                            merged_data[key] = file_data_merger(def_data_c[key], file_data[key])
                    else:
                        merged_data[key] = file_data[key]
                except KeyError:
                    print("error")
                    merged_data[key] = def_data_c[key]
        return merged_data

    def_d = {"auto_save": {"file_merger_code": 1, "file_merger_value": [52]}, "keybinds": {"esc": [b"\x1b"], "up": [b"H", {"file_merger_code": -1, "file_merger_value": 1}], "down": [b"P", 1], "left": [b"K", 1], "right": [b"M", 1], "enter": [b"\r"]}}
    file_d = {"auto_save": [1, 2, 3, 4, 5], "lol": "trash", "keybinds": {"esc": [b"\x1b", 1, 2, 3], "up": [b"H", 1], "right": [b"M", 1], "enter": [b"\r"]}}

    merged_d = file_data_merger(def_d, file_d)
    print("\n" + str(def_d))
    print("\n" + str(file_d))
    print("\n" + str(merged_d))
    """


def encode_keybinds(settings:dict[list[bytes|int]]):
    for x in settings["keybinds"]:
        settings['keybinds'][x][0] = settings['keybinds'][x][0].decode(ENCODING)
    return settings


def decode_keybinds(settings:dict):
    for x in settings["keybinds"]:
        settings['keybinds'][x][0] = bytes(settings['keybinds'][x][0], ENCODING)
    return settings


def settings_manager(line_name:str, write_value=None) -> Any | None:
    """
    STRUCTURE:\n
    - auto_save
    - logging
    - keybinds
    \t- esc
    \t- up
    \t- down
    \t- left
    \t- right
    \t- enter
    """

    # default values
    settings_lines = ["auto_save", "logging", "keybinds"]
    def_settings = {"auto_save": True, "logging": True, "keybinds": {"esc": [b"\x1b"], "up": [b"H", 1], "down": [b"P", 1], "left": [b"K", 1], "right": [b"M", 1], "enter": [b"\r"]}}

    def recreate_settings():
        encode_save_s(encode_keybinds(def_settings), os.path.join(ROOT_FOLDER, "settings"), SETTINGS_SEED)
        # log
        log_info("Recreated settings")
        return def_settings


    try:
        settings = decode_keybinds(decode_save_s(os.path.join(ROOT_FOLDER, "settings"), 0, SETTINGS_SEED))
    except ValueError:
        from data_manager import press_key
        
        log_info("Decode error", "settings", Log_type.ERROR)
        press_key("The settings file is corrupted, and will now be recreated!")
        settings = recreate_settings()
    except FileNotFoundError:
        settings = recreate_settings()
    # return
    if write_value == None:
        if line_name == None:
            return settings
        else:
            try:
                return settings[line_name]
            except KeyError:
                if line_name in settings_lines:
                    log_info("Missing key in settings", line_name, Log_type.WARN)
                    settings_manager(line_name, def_settings[line_name])
                    return def_settings[line_name]
                else:
                    raise
    # write
    else:
        if line_name in settings.keys():
            if settings[line_name] != write_value:
                log_info("Changed settings", f"{line_name}: {settings[line_name]} -> {write_value}")
                settings[line_name] = write_value
                encode_save_s(encode_keybinds(settings), os.path.join(ROOT_FOLDER, "settings"), SETTINGS_SEED)
        else:
            if line_name in settings_lines:
                log_info("Recreating key in settings", line_name, Log_type.WARN)
                settings[line_name] = def_settings[line_name]
                encode_save_s(encode_keybinds(settings), os.path.join(ROOT_FOLDER, "settings"), SETTINGS_SEED)
            else:
                raise KeyError(line_name)


def random_state_converter(random_state:np.random.RandomState | dict | tuple):
    """
    Can convert a numpy RandomState.getstate() into a json format and back.
    """
    if type(random_state) is dict:
        states = [int(num) for num in random_state["state"]]
        return (str(random_state["type"]), np.array(states, dtype=np.uint32), int(random_state["pos"]), int(random_state["has_gauss"]), float(random_state["cached_gaussian"]))
    else:
        if type(random_state) is tuple:
            state = random_state
        else:
            state = random_state.get_state()
        state_nums = []
        for num in state[1]:
            state_nums.append(int(num))
        return {"type": state[0], "state": state_nums, "pos": state[2], "has_gauss": state[3], "cached_gaussian": state[4]}


def is_up_to_date(min_version:str, curr_version:str):
    """
    Returns if the current version string is equal or higher than the minimum version.
    """
    version = curr_version.split(".")
    min_v = min_version.split(".")

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
        log_info("Python up to date")
    else:
        from platform import python_version
        log_info("Python not up to date", f"{python_version()} -> {PYTHON_MIN_VERSION}", Log_type.WARN)
        print(f"Python not up to date: {python_version()} -> {PYTHON_MIN_VERSION}")
    # packages
    if len(bad_packages) == 0:
        log_info("All packages up to date")
    else:
        bad_packages_str = []
        for package in bad_packages:
            bad_packages_str.append(f"{package[2]}({package[1]}) -> {package[0]}")
        log_info("Some packages are not up to date", ", ".join([p for p in bad_packages_str]), Log_type.WARN)
        print(f"{'Some packages are' if len(bad_packages) > 1 else 'A package is'} not up to date:\n\t" + "\n\t".join([p for p in bad_packages_str]))
    # return
    if len(bad_packages) == 0 and py_good:
        return True
    else:
        if input("Do you want to continue?(Y/N): ").upper() == "Y":
            log_info("Continuing anyways")
            return True
        else:
            return False

def check_package_versions():
    """
    Checks if all tested packages and python are up do date.\n
    Checks:
    - python
    - numpy
    - Save File Manager
    - random sentance
    """
    from platform import python_version
    import random_sentance as rs

    log_info("Checking python version")
    py_good = True
    if not is_up_to_date(PYTHON_MIN_VERSION, python_version()):
        py_good = False
    log_info("Checking package versions")
    packages = [[PIP_NP_MIN_VERSION, np.__version__, "numpy"],
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
        return os.path.isdir(os.path.join(SAVES_FOLDER_PATH, save_name))
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