from enum import Enum
import json
import os
import shutil
import threading
from datetime import datetime as dtime
from msvcrt import getch
from typing import Any
import numpy as np
import colorama

import save_file_manager as sfm

# random
r = np.random.RandomState()

# package versions
PYTHON_MIN_VERSION = "3.10.5"
PIP_NP_MIN_VERSION = "1.22.1"
PIP_COLOR_MIN_VERSION = "0.4.5"

PIP_SFM_MIN_VERSION = "1.10.6"
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
    #save
SAVES_FOLDER = "saves"
SAVES_FOLDER_PATH = os.path.join(ROOT_FOLDER, SAVES_FOLDER)
SAVE_NAME = "save*"
SAVE_EXT = "sav"
SAVE_FILE_PATH = os.path.join(SAVES_FOLDER_PATH, SAVE_NAME)
    #logs
LOGGING = True
LOGS_FOLDER = "logs"
LOGS_FOLDER_PATH = os.path.join(ROOT_FOLDER, LOGS_FOLDER)
LOG_EXT = "log"
    #backups
BACKUPS_FOLDER = "backups"
BACKUPS_FOLDER_PATH = os.path.join(ROOT_FOLDER, BACKUPS_FOLDER)
BACKUP_EXT = SAVE_EXT + ".bak"
# colorama color
C_F_RED = colorama.Fore.RED
C_F_GREEN = colorama.Fore.GREEN
# other
AUTO_SAVE_DELAY = 3
SETTINGS_ENCODE_SEED = 1
FILE_ENCODING_VERSION = 2
DOUBLE_KEYS = [b"\xe0", b"\x00"]
LOG_MS = False
SAVE_VERSION = 1.1


def pad_zero(num:int|str):
    """
    Converts numbers that are smaller than 10 to have a trailing 0.
    """
    return ('0' if int(num) < 10 else '') + str(num)


def make_date(date_lis:list|dtime, sep="-"):
    """
    Turns a datetime object's date part or a list into a formated string.
    """
    if type(date_lis) == dtime:
        return f"{pad_zero(date_lis.year)}{sep}{pad_zero(date_lis.month)}{sep}{pad_zero(date_lis.day)}"
    else:
        return f"{pad_zero(date_lis[0])}{sep}{pad_zero(date_lis[1])}{sep}{pad_zero(date_lis[2])}"


def make_time(time_lis:list|dtime, sep=":", write_ms=False, ms_sep:str="."):
    """
    Turns a datetime object's time part or a list into a formated string.
    """
    if type(time_lis) == dtime:
        return f"{pad_zero(time_lis.hour)}{sep}{pad_zero(time_lis.minute)}{sep}{pad_zero(time_lis.second)}{f'{ms_sep}{time_lis.microsecond}' if write_ms else ''}"
    else:
        return f"{pad_zero(time_lis[0])}{sep}{pad_zero(time_lis[1])}{sep}{pad_zero(time_lis[2])}{f'{ms_sep}{time_lis[3]}' if write_ms else ''}"


def change_logging(value:bool):
    global LOGGING
    print(LOGGING, value)
    if LOGGING != value:
        if value:
            LOGGING = value
            log_info("Logging enabled")
        else:
            log_info("Logging disabled")
            LOGGING = value

def begin_log():
    if LOGGING:
        current_date = make_date(dtime.now())
        recreate_logs_folder()
        f = open(os.path.join(LOGS_FOLDER_PATH, f"{current_date}.{LOG_EXT}"), "a")
        f.write("\n")

def log_info(message:str, detail="", message_type=0, write_out=False, new_line=False):
    """
    Progress Adventure logger.\n
    Message types:
    - 0: INFO
    - 1: WARN
    - 2: ERROR
    - 3: CRASH
    - -1: OTHER
    """
    try:
        if LOGGING:
            match message_type:
                case 0:
                    m_type = "INFO"
                case 1:
                    m_type = "WARN"
                case 2:
                    m_type = "ERROR"
                case 3:
                    m_type = "CRASH"
                case _:
                    m_type = "OTHER"
            current_date = make_date(dtime.now())
            current_time = make_time(dtime.now(), write_ms=LOG_MS)
            recreate_logs_folder()
            f = open(os.path.join(LOGS_FOLDER_PATH, f"{current_date}.{LOG_EXT}"), "a")
            if new_line:
                f.write("\n")
            f.write(f"[{current_time}] [{threading.current_thread().name}/{m_type}]\t: |{message}| {detail}\n")
            f.close()
            if write_out:
                if new_line:
                    print("\n")
                print(f'{os.path.join(LOGS_FOLDER, f"{current_date}.{LOG_EXT}")} -> [{current_time}] [{threading.current_thread().name}/{m_type}]\t: |{message}| {detail}')
    except:
        if LOGGING:
            f = open(os.path.join(ROOT_FOLDER, "CRASH.log"), "a")
            f.write(f"\n[{make_date(dtime.now())}_{make_time(dtime.now(), write_ms=True)}] [CRASH]\t: |Logging error|\n")
            f.close()


def recreate_folder(folder_name:str, folder_path:str=None, display_name:str=None):
    if folder_path == None:
        folder_path = os.path.join(ROOT_FOLDER, folder_name)
    if display_name == None:
        display_name = folder_name.lower()
    if not os.path.isdir(folder_path):
        os.mkdir(folder_name)
        log_info(f"Recreating {display_name} folder")

def recreate_saves_folder():
    recreate_folder(SAVES_FOLDER)


def recreate_backups_folder():
    recreate_folder(BACKUPS_FOLDER)


def recreate_logs_folder():
    recreate_folder(LOGS_FOLDER)


def make_backup(save_num:int, is_temporary=False):
    recreate_saves_folder()
    recreate_backups_folder()
    now = dtime.now()
    backup_name_end = f'{make_date(now)};{make_time(now, "-", is_temporary, "-")};{SAVE_NAME.replace("*", str(save_num))}.{BACKUP_EXT}'
    save_name = f'{SAVE_FILE_PATH.replace("*", str(save_num))}.{SAVE_EXT}'
    display_save_name = f'{os.path.join(SAVES_FOLDER, SAVE_NAME).replace("*", str(save_num))}.{SAVE_EXT}'
    backup_name = os.path.join(BACKUPS_FOLDER_PATH, backup_name_end)
    display_backup_name = os.path.join(BACKUPS_FOLDER, backup_name_end)

    if os.path.isfile(save_name):
        shutil.copyfile(save_name, backup_name)
        log_info(f"Made {('temporary ' if is_temporary else ' ')}backup", display_backup_name)
        return [backup_name, display_backup_name]
    else:
        log_info("Backup failed", f"save file not found: {display_save_name}", 1)
        return False
    


def press_key(text=""):
    """
    Writes out text, and then stalls until the user presses any key.
    """

    print(text, end="", flush=True)
    if DOUBLE_KEYS.count(getch()):
        getch()
    print()


def is_key(key:object) -> bool:
    """
    Waits for a specific key.\n
    key should be a Key object.
    """

    key_in = getch()
    arrow = False
    if key_in in DOUBLE_KEYS:
        arrow = True
        key_in = getch()
    return ((len(key.value) == 1 and not arrow) or (len(key.value) > 1 and arrow)) and key_in == key.value[0]


def text_c(text:str, color):
    """
    Colors text fore/background.
    """
    return color + text + colorama.Back.RESET + colorama.Fore.RESET


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
        good = (type(data) == dict and "file_merger_code" in data.keys() and "file_merger_value" in data.keys() and data["file_merger_code"] != 0)
        if write:
            print(f"{data}:", good)
        return good

    def file_data_merger(def_data:list|dict, file_data:list|dict):
        def_data_c = copy.deepcopy(def_data)
        if type(def_data_c) == list:
            merged_data = []
            for x in range(len(def_data_c)):
                print("\nlist", type(def_data_c[x]))
                good = is_good(def_data_c[x], True)
                try:
                    if type(def_data_c[x]) == list or type(def_data_c[x]) == dict:
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
                    if type(def_data_c[key]) == list or type(def_data_c[key]) == dict:
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
        sfm.encode_save(json.dumps(encode_keybinds(def_settings)), SETTINGS_ENCODE_SEED, "settings", SAVE_EXT, ENCODING, FILE_ENCODING_VERSION)
        # log
        log_info("Recreated settings")
        return def_settings


    try:
        settings = decode_keybinds(json.loads(sfm.decode_save(SETTINGS_ENCODE_SEED, "settings", SAVE_EXT, ENCODING)[0]))
    except ValueError:
        log_info("Decode error", "settings", 2)
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
                    log_info("Missing key in settings", line_name, 1)
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
                sfm.encode_save(json.dumps(encode_keybinds(settings)), SETTINGS_ENCODE_SEED, "settings", SAVE_EXT, ENCODING, FILE_ENCODING_VERSION)
        else:
            if line_name in settings_lines:
                log_info("Recreating key in settings", line_name, 1)
                settings[line_name] = def_settings[line_name]
                sfm.encode_save(json.dumps(encode_keybinds(settings)), SETTINGS_ENCODE_SEED, "settings", SAVE_EXT, ENCODING, FILE_ENCODING_VERSION)
            else:
                raise KeyError(line_name)


def random_state_converter(random_state:np.random.RandomState | dict | tuple):
    """
    Can convert a numpy RandomState.getstate() into a json format and back.
    """
    if type(random_state) == dict:
        states = [int(num) for num in random_state["state"]]
        return (str(random_state["type"]), np.array(states, dtype=np.uint32), int(random_state["pos"]), int(random_state["has_gauss"]), float(random_state["cached_gaussian"]))
    else:
        if type(random_state) == tuple:
            state = random_state
        else:
            state = random_state.get_state()
        state_nums = []
        for num in state[1]:
            state_nums.append(int(num))
        return {"type": state[0], "state": state_nums, "pos": state[2], "has_gauss": state[3], "cached_gaussian": state[4]}

def item_finder(name:str) -> Enum|None:
    """
    Gives back the item enum, from the item name.\n
    Returns ``None`` if it doesn't exist.
    """
    from classes import Item_categories

    for enum in Item_categories._value2member_map_:
        try: return enum._member_map_[name]
        except KeyError: pass

def inventory_converter(inventory:list):
    """
    Can convert between the json and object versions of the inventory items list.
    """
    from classes import Item

    items = []
    for item in inventory:
        if type(item) == list:
            items.append(Item(item_finder(item[0]), item[1]))
        else:
            item:Item
            items.append([item.name.name, item.amount])
    return items


def check_p_version(min_version:str, curr_version:str):
    version = curr_version.split(".")
    min_v = min_version.split(".")

    for x in range(len(version)):
        if len(min_v) < (x + 1):
            return True
        # print(f"{version[x]} >=? {min_v[x]}")
        if (x == len(version) - 1 and len(version) < len(min_v)) or (int(version[x]) < int(min_v[x])):
            return False
    return True

def package_response(bad_packages:list, py_good:bool):
    # python
    if py_good:
        log_info("Python up to date")
    else:
        from platform import python_version
        log_info("Python not up to date", f"{python_version()} -> {PYTHON_MIN_VERSION}", 1)
        print(f"Python not up to date: {python_version()} -> {PYTHON_MIN_VERSION}")
    # packages
    if len(bad_packages) == 0:
        log_info("All packages up to date")
    else:
        bad_packages_str = []
        for package in bad_packages:
            bad_packages_str.append(f"{package[2]}({package[1]}) -> {package[0]}")
        log_info("Some packages are not up to date", ", ".join([p for p in bad_packages_str]), 1)
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
    - colorama
    - Save File Manager
    - random sentance
    """
    from platform import python_version
    import random_sentance as rs

    log_info("Checking python version")
    py_good = True
    if not check_p_version(PYTHON_MIN_VERSION, python_version()):
        py_good = False
    log_info("Checking package versions")
    packages = [[PIP_NP_MIN_VERSION, np.__version__, "numpy"],
                [PIP_COLOR_MIN_VERSION, colorama.__version__, "colorama"],
                [PIP_SFM_MIN_VERSION, sfm.__version__, "Save File Manager"],
                [PIP_RS_MIN_VERSION, rs.__version__, "Random Sentance"]]

    bad_packages = []
    for package in packages:
        if not check_p_version(package[0], package[1]):
            bad_packages.append(package)
    return package_response(bad_packages, py_good)

