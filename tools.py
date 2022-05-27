import json
import os
import threading
from datetime import datetime as dtime
from msvcrt import getch
import numpy as np

import save_file_manager as sfm

r = np.random.RandomState()

ENCODING = "windows-1250"
MAIN_THREAD_NAME = "Main"
LOGS_FOLDER = "logs/"
LOGS_EXT = "log"



def pad_zero(num:int|str):
    return ('0' if int(num) < 10 else '') + str(num)


def make_date(date_lis:list|dtime, sep="-"):
    if type(date_lis) == dtime:
        return f"{pad_zero(date_lis.year)}{sep}{pad_zero(date_lis.month)}{sep}{pad_zero(date_lis.day)}"
    else:
        return f"{pad_zero(date_lis[0])}{sep}{pad_zero(date_lis[1])}{sep}{pad_zero(date_lis[2])}"


def make_time(time_lis:list|dtime, sep=":"):
    if type(time_lis) == dtime:
        return f"{pad_zero(time_lis.hour)}{sep}{pad_zero(time_lis.minute)}{sep}{pad_zero(time_lis.second)}"
    else:
        return f"{pad_zero(time_lis[0])}{sep}{pad_zero(time_lis[1])}{sep}{pad_zero(time_lis[2])}"


def log_info(message:str, detail="", message_type="INFO", write_out=False, new_line=False):
    current_date = make_date(dtime.now())
    current_time = make_time(dtime.now())
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



def encode_keybinds(settings:dict[list[bytes|int]]):
    for x in settings["keybinds"]:
        settings['keybinds'][x][0] = settings['keybinds'][x][0].decode(ENCODING)
    return settings


def decode_keybinds(settings:dict):
    for x in settings["keybinds"]:
        settings['keybinds'][x][0] = bytes(settings['keybinds'][x][0], ENCODING)
    return settings


def is_key(key_array:list):
    # key array, exept [[key], [double checker]]
    key = getch()
    arrow = False
    if key in key_array[1]:
        arrow = True
        key = getch()
    return ((len(key_array[0]) == 1 and not arrow) or (len(key_array[0]) > 1 and arrow)) and key == key_array[0][0]


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
    # default values
    try:
        settings = decode_keybinds(json.loads(sfm.decode_save(0, "settings")[0]))
    except FileNotFoundError:
        settings = {"auto_save": True, "keybinds": {"esc": [b"\x1b"], "up": [b"H", 1], "down": [b"P", 1], "left": [b"K", 1], "right": [b"M", 1], "enter": [b"\r"]}}
        sfm.encode_save(json.dumps(encode_keybinds(settings)), 0, "settings")
        # log
        log_info("Recreated settings")
    if write_value == None:
        if line_name == None:
            return settings
        else:
            return settings[line_name]
    else:
        settings[line_name] = write_value
        sfm.encode_save(json.dumps(encode_keybinds(settings)), 0, "settings")


def random_state_converter(random_state:np.random.RandomState | dict | tuple):
    """
    Can convert a numpy RandomState.getstate() into an easily storable string and back.
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


def decode_save_file(save_num=1, save_name="save*", save_ext="sav"):
    try:
        save_data = sfm.decode_save(save_num, save_name, save_ext)
    except FileNotFoundError:
        print("decode_save_file: FILE NOT FOUND!")
    else:
        f = open(f'{save_name.replace("*", str(save_num))}.decoded.txt', "w")
        for line in save_data:
            f.write(line + "\n")
        f.close()


# thread_1 = threading.Thread(target="function", name="Thread name", args=["argument list"])
# thread_1.start()
# merge main and started thread 1?
# thread_1.join()
