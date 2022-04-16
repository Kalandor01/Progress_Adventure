import os
import threading
from datetime import datetime as dtime
import numpy as np

import save_file_manager as sfm

r = np.random.RandomState()

def metadata_manager(line_num:int, write_value=None):
    """
    STRUCTURE:\n
    0 = max_saves
    """
    # default values
    max_saves = 5
    try:
        metadata = sfm.decode_save(0, "metadata")
    except FileNotFoundError:
        metadata = [max_saves]
        sfm.encode_save(metadata, 0, "metadata")
        # log
        log_info("|Recreated metadata|")
    # formating
    metadata[0] = int(metadata[0])
    if write_value == None:
        return metadata[line_num]
    else:
        metadata[line_num] = write_value
        sfm.encode_save(metadata, 0, "metadata")


def random_state_converter(random_state:np.random.RandomState | tuple | str):
    """
    Can convert a numpy RandomState.getstate() into an easily storable string and back.
    """
    if type(random_state) == str:
        lines = random_state.split(";")
        states = [int(num) for num in lines[1].split("|")]
        return (str(lines[0]), np.array(states, dtype=np.uint32), int(lines[2]), int(lines[3]), float(lines[4]))
    else:
        if type(random_state) == tuple:
            state = random_state
        else:
            state = random_state.get_state()
        state_txt = state[0] + ";"
        for num in state[1]:
            state_txt += str(num) + "|"
        return f"{state_txt[:-1]};{str(state[2])};{str(state[3])};{str(state[4])}"


def decode_save_file(save_num=1, save_name="save*", save_ext="sav"):
    save_data = sfm.decode_save(save_num, save_name, save_ext)
    f = open(f'{save_name.replace("*", str(save_num))}.decoded.txt', "w")
    for line in save_data:
        f.write(line + "\n")
    f.close()


def log_info(message:str, message_type="INFO", write_out=False):
    zero = lambda num: ("0" if num < 10 else "") + str(num)

    current_date = f"{zero(dtime.now().year)}-{zero(dtime.now().month)}-{zero(dtime.now().day)}"
    current_time = f"{zero(dtime.now().hour)}:{zero(dtime.now().minute)}:{zero(dtime.now().second)}"
    try:
        f = open(f"logs/{current_date}.txt", "a")
    except FileNotFoundError:
        os.mkdir("logs")
        f = open(f"logs/{current_date}.txt", "a")
    f.write(f"[{current_time}] [{threading.current_thread().name}/{message_type}]\t: {message}\n")
    f.close()
    if write_out:
        print(f'logs/{current_date}.txt -> [{current_time}] [{threading.current_thread().name}/{message_type}]\t: {message}')


# thread_1 = threading.Thread(target="function", name="Thread name", args=["argument list"])
# thread_1.start()
# merge main and started thread 1?
# thread_1.join()