import copy
import json
import os
import threading
from datetime import datetime as dtime
from msvcrt import getch
import numpy as np

import random_sentance as rs
import save_file_manager as sfm

# random
r = np.random.RandomState()

# package versions
PIP_NP_MIN_VERSION = "1.22.1"

PIP_SFM_MIN_VERSION = "1.10.2"
PIP_RS_MIN_VERSION = "1.5.1"
# language
ENCODING = "windows-1250"
# thread names
MAIN_THREAD_NAME = "Main"
AUTO_SAVE_THREAD_NAME = "Auto saver"
MANUAL_SAVE_THREAD_NAME = "Quit manager"
# paths/folders/file names
LOGS_FOLDER = "logs/"
LOGS_EXT = "log"
SAVE_FOLDER = os.path.dirname(os.path.abspath(__file__)) + "/saves"
SAVE_NAME = "save*"
SAVE_EXT = "sav"
SAVE_FILE_PATH = os.path.join(SAVE_FOLDER, SAVE_NAME)
# other
AUTO_SAVE_DELAY = 3
SETTINGS_ENCODE_SEED = 1
FILE_ENCODING_VERSION = 2
DOUBLE_KEYS = [b"\xe0", b"\x00"]
LOG_MS = False


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


def make_time(time_lis:list|dtime, sep=":", write_ms=False):
    """
    Turns a datetime object's time part or a list into a formated string.
    """
    if type(time_lis) == dtime:
        return f"{pad_zero(time_lis.hour)}{sep}{pad_zero(time_lis.minute)}{sep}{pad_zero(time_lis.second)}{f'.{time_lis.microsecond}' if write_ms else ''}"
    else:
        return f"{pad_zero(time_lis[0])}{sep}{pad_zero(time_lis[1])}{sep}{pad_zero(time_lis[2])}{f'.{time_lis[3]}' if write_ms else ''}"


def log_info(message:str, detail="", message_type="INFO", write_out=False, new_line=False):
    """
    Progress Adventure logger.
    """
    current_date = make_date(dtime.now())
    current_time = make_time(dtime.now(), write_ms=LOG_MS)
    try:
        f = open(f"{LOGS_FOLDER}{current_date}.{LOGS_EXT}", "a")
    except FileNotFoundError:
        os.mkdir("logs")
        # log
        log_info("Recreating logs folder")
        f = open(f"{LOGS_FOLDER}{current_date}.{LOGS_EXT}", "a")
    if new_line:
        f.write("\n")
    f.write(f"[{current_time}] [{threading.current_thread().name}/{message_type}]\t: |{message}| {detail}\n")
    f.close()
    if write_out:
        if new_line:
            print("\n")
        print(f'{LOGS_FOLDER}{current_date}.{LOGS_EXT} -> [{current_time}] [{threading.current_thread().name}/{message_type}]\t: |{message}| {detail}')


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


# ULTIMATE MIND DESTRUCTION!!!
def file_data_merger_special(def_data:list|dict, file_data:list|dict, index:int|str, list_type:type):
    code = def_data["file_merger_code"]
    value = def_data["file_merger_value"]
    print("good", def_data, file_data)
    if code == -1:
        if len(file_data) == 0:
            merged_data = value
        else:
            merged_data = file_data[index]
    elif code == 1:
        merged_data = file_data
    print(merged_data)
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
                        merged_data.append(file_data_merger_special(def_data_c[x], file_data, x, list))
                    else:
                        merged_data.append(file_data_merger(def_data_c[x], file_data[x]))
                else:
                    merged_data.append(file_data[x])
            except IndexError:
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
                merged_data[key] = def_data_c[key]
    return merged_data

def_d = {"auto_save": {"file_merger_code": 1, "file_merger_value": [52]}, "keybinds": {"esc": [b"\x1b"], "up": [b"H", {"file_merger_code": -1, "file_merger_value": 1}], "down": [b"P", 1], "left": [b"K", 1], "right": [b"M", 1], "enter": [b"\r"]}}
file_d = {"auto_save": [1, 2, 3, 4, 5], "lol": "trash", "keybinds": {"esc": [b"\x1b", 1, 2, 3], "up": [b"H"], "right": [b"M", 1], "enter": [b"\r"]}}

merged_d = file_data_merger(def_d, file_d)
print("\n" + str(def_d))
print(file_d)
print(merged_d)



def encode_keybinds(settings:dict[list[bytes|int]]):
    for x in settings["keybinds"]:
        settings['keybinds'][x][0] = settings['keybinds'][x][0].decode(ENCODING)
    return settings

def decode_keybinds(settings:dict):
    for x in settings["keybinds"]:
        settings['keybinds'][x][0] = bytes(settings['keybinds'][x][0], ENCODING)
    return settings

def settings_manager(line_name:str, write_value=None):
    """
    STRUCTURE:\n
    - auto_save
    - keybinds
    \t- esc
    \t- up
    \t- down
    \t- left
    \t- right
    \t- enter
    """

    def recreate_settings():
        settings = {"auto_save": True, "keybinds": {"esc": [b"\x1b"], "up": [b"H", 1], "down": [b"P", 1], "left": [b"K", 1], "right": [b"M", 1], "enter": [b"\r"]}}
        sfm.encode_save(json.dumps(encode_keybinds(settings)), SETTINGS_ENCODE_SEED, "settings", SAVE_EXT, ENCODING, FILE_ENCODING_VERSION)
        # log
        log_info("Recreated settings")
        return settings

    # default values
    try:
        settings = decode_keybinds(json.loads(sfm.decode_save(SETTINGS_ENCODE_SEED, "settings", SAVE_EXT, ENCODING)[0]))
    except ValueError:
        log_info("Decode error", "Settings", "ERROR")
        press_key(f"The settings file is corrupted, and will now be recreated!")
        settings = recreate_settings()
    except FileNotFoundError:
        settings = recreate_settings()
    if write_value == None:
        if line_name == None:
            return settings
        else:
            return settings[line_name]
    else:
        settings[line_name] = write_value
        sfm.encode_save(json.dumps(encode_keybinds(settings)), SETTINGS_ENCODE_SEED, "settings", SAVE_EXT, ENCODING, FILE_ENCODING_VERSION)


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
        return {"seed": {"type": state[0], "state": state_nums, "pos": state[2], "has_gauss": state[3], "cached_gaussian": state[4]}}


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

def package_response(bad_packages:list):
    if len(bad_packages) == 0:
        log_info("All packages up to date")
        return True
    else:
        log_info("Some packages are not up to date", bad_packages, "WARN")
        if input(str(", ".join(bad_packages)) + " packages out of date. Do you want to continue?(Y/N): ").upper() == "Y":
            log_info("Continuing anyways")
            return True
        else:
            return False

def check_package_versions():
    """
    Checks if all tested packages are up do date.
    Checks:
    - Save File Manager
    """

    log_info("Checking package versions", new_line=True)
    packages = [[PIP_NP_MIN_VERSION, np], [PIP_SFM_MIN_VERSION, sfm], [PIP_RS_MIN_VERSION, rs]]
    bad_packages = []
    for package in packages:
        if not check_p_version(package[0], package[1].__version__):
            bad_packages.append(package[1].__name__)
    return package_response(bad_packages)

