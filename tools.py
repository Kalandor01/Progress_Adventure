import os
import threading
from datetime import datetime as dtime
import numpy as np

import save_file_manager as sfm

r = np.random.RandomState()

def metadata_manager(line_num:int, write_value=None):
    """
    STRUCTURE:\n
    
    """
    # default values
    
    try:
        metadata = sfm.decode_save(0, "metadata")
    except FileNotFoundError:
        metadata = []
        sfm.encode_save(metadata, 0, "metadata")
        # log
        log_info("Recreated metadata")
    # formating
    metadata[0] = int(metadata[0])
    if write_value == None:
        return metadata[line_num]
    else:
        metadata[line_num] = write_value
        sfm.encode_save(metadata, 0, "metadata")


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
        print("FILE NOT FOUND!")
    else:
        f = open(f'{save_name.replace("*", str(save_num))}.decoded.txt', "w")
        for line in save_data:
            f.write(line + "\n")
        f.close()


def log_info(message:str, detail="", message_type="INFO", write_out=False):
    zero = lambda num: ("0" if num < 10 else "") + str(num)

    current_date = make_date(dtime.now())
    current_time = make_time(dtime.now())
    try:
        f = open(f"logs/{current_date}.txt", "a")
    except FileNotFoundError:
        os.mkdir("logs")
        # log
        log_info("Recreating logs folder")
        f = open(f"logs/{current_date}.txt", "a")
    f.write(f"[{current_time}] [{threading.current_thread().name}/{message_type}]\t: |{message}| {detail}\n")
    f.close()
    if write_out:
        print(f'logs/{current_date}.txt -> [{current_time}] [{threading.current_thread().name}/{message_type}]\t: |{message}| {detail}')


# thread_1 = threading.Thread(target="function", name="Thread name", args=["argument list"])
# thread_1.start()
# merge main and started thread 1?
# thread_1.join()