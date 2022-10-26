import json
import os
from datetime import datetime as dtime

import utils as u
import tools as ts
import data_manager as dm
import entities as es
import inventory as iy
import chunk_manager as ch

from utils import Color, Style
from tools import r, sfm
from tools import Log_type
from tools import SAVES_FOLDER_PATH, SAVE_SEED, SAVE_EXT
from tools import SAVE_VERSION
from tools import SAVE_FILE_NAME_DATA
from tools import SAVE_FOLDER_NAME_CHUNKS


def _create_display_json(data:dm.Save_data):
    display_data = {}
    display_data["save_version"] = SAVE_VERSION
    display_data["display_name"] = data.display_save_name
    now = dtime.now()
    last_access = [now.year, now.month, now.day, now.hour, now.minute, now.second]
    display_data["last_access"] = last_access
    display_data["player_name"] = data.player.name
    return display_data


def _create_player_json(player_data:es.Player):
    player_json = {"name": player_data.name, "hp": player_data.hp, "attack": player_data.attack, "defence": player_data.defence, "speed": player_data.speed}
    player_json["inventory"] = list(iy.inventory_converter(player_data.inventory.items))
    return player_json


def _create_data_json(data:dm.Save_data):
    save_data_json = {}
    # save_version
    save_data_json["save_version"] = SAVE_VERSION
    # display_name
    save_data_json["display_name"] = data.display_save_name
    # last_access
    now = dtime.now()
    last_access = [now.year, now.month, now.day, now.hour, now.minute, now.second]
    save_data_json["last_access"] = last_access
    # player
    save_data_json["player"] = _create_player_json(data.player)
    # randomstate
    save_data_json["seed"] = ts.random_state_converter(r)
    return save_data_json


def _create_chunk_json(chunk:ch.Chunk, save_folder:str):
    chunk_data = chunk.to_json()
    chunk_file_name = f"{chunk.base_x}_{chunk.base_y}"
    ts.encode_save_s(chunk_data, os.path.join(save_folder, SAVE_FOLDER_NAME_CHUNKS, chunk_file_name))


def _create_chunks_json(chunks:list[ch.Chunk], save_folder:str):
    for chunk in chunks:
        _create_chunk_json(chunk, save_folder)


def make_save(data:dm.Save_data):
    # make backup
    backup_status = ts.make_backup(data.save_name, True)
    # FOLDER
    ts.recreate_folder(data.save_name, SAVES_FOLDER_PATH, "save file")
    save_folder = os.path.join(SAVES_FOLDER_PATH, data.save_name)
    # DATA FILE
    # display data
    display_data = _create_display_json(data)
    save_data = _create_data_json(data)
    # create new save
    ts.encode_save_s([display_data, save_data], os.path.join(save_folder, SAVE_FILE_NAME_DATA))
    # CHUNKS FOLDER
    ts.recreate_folder(SAVE_FOLDER_NAME_CHUNKS, save_folder)
    ts.log_info("Saving chunks")
    _create_chunks_json(data.chunks, save_folder)
    # remove backup
    if backup_status != False:
        os.remove(backup_status[0])
        ts.log_info("Removed temporary backup", backup_status[1])


def create_save_data():
    ts.log_info("Preparing game data")
    # make save name
    display_save_name = input("Name your save: ")
    if display_save_name == "":
        display_save_name = "new save"
    save_name = ts.correct_save_name(display_save_name)
    # make player
    player = es.Player(input("What is your name?: "))
    # last_access
    now = dtime.now()
    last_access = [now.year, now.month, now.day, now.hour, now.minute, now.second]
    # load to class
    return dm.Save_data(save_name, display_save_name, last_access, player, r.get_state())


def correct_save_data(data:dict, save_version:int, extra_data:dict):
    ts.log_info("Correcting save data")
    # 0.0 -> 1.0
    if save_version == 0.0:
        save_version = 1.0
        ts.log_info("Corrected save data", "0.0 -> 1.0")
    # 1.0 -> 1.1
    if save_version == 1.0:
        data["player"]["inventory"] = []
        save_version = 1.1
        ts.log_info("Corrected save data", "1.0 -> 1.1")
    # 1.1 -> 1.2
    if save_version == 1.1:
        data["display_name"] = extra_data["save_name"]
        save_version = 1.2
        ts.log_info("Corrected save data", "1.1 -> 1.2")
    # 1.2 -> 1.3
    if save_version == 1.2:
        # switched from file to folder
        save_version = 1.3
        ts.log_info("Corrected save data", "1.2 -> 1.3")
    return data


def load_save(save_name:str, keybind_mapping:list):
    """
    Loads a save file.
    """
    full_save_name = os.path.join(SAVES_FOLDER_PATH, save_name)
    # get if save if a file
    if os.path.isfile(f'{full_save_name}.{SAVE_EXT}'):
        data = ts.decode_save_s(full_save_name, 1)
        os.remove(f'{full_save_name}.{SAVE_EXT}')
        ts.log_info("Removed save file", "single save files have been deprecated", Log_type.WARN)
    else:
        data = ts.decode_save_s(os.path.join(full_save_name, SAVE_FILE_NAME_DATA, ), 1)
    # read data
    
    # save version
    try: save_version = data["save_version"]
    except KeyError: save_version = 0.0
    if save_version != SAVE_VERSION:
        is_older = ts.is_up_to_date(str(save_version), str(SAVE_VERSION))
        ts.log_info("Trying to load save with an incorrect version", f"{SAVE_VERSION} -> {save_version}", Log_type.WARN)
        ans = sfm.UI_list(["Yes", "No"], f"\"{save_name}\" is {('an older version' if is_older else 'a newer version')} than what it should be! Do you want to back up the save file before loading it?").display(keybind_mapping)
        if ans == 0:
            ts.make_backup(save_name)
        data = correct_save_data(data, save_version, {"save_name": save_name})
    # display_name
    display_name = data["display_name"]
    # last access
    last_access = data["last_access"]
    # player
    player_data = data["player"]
    player = es.Player(player_data["name"])
    player.hp = int(player_data["hp"])
    player.attack = int(player_data["attack"])
    player.defence = int(player_data["defence"])
    player.speed = float(player_data["speed"])
    player.inventory.items = list(iy.inventory_converter(player_data["inventory"]))
    # log
    ts.log_info("Loaded save", f'save name: {save_name}, player name: "{player.name}", last saved: {u.make_date(last_access)} {u.make_time(last_access[3:])}')
    
    # PREPARING
    ts.log_info("Preparing game data")
    # load random state
    r.set_state(ts.random_state_converter(data["seed"]))
    # load to class
    return dm.Save_data(save_name, display_name, last_access, player, r.get_state())


def _process_save_display_data(data):
    try:
        data_processed = ""
        try:
            dispaly_name = data[1]['display_name']
        except KeyError:
            dispaly_name = data[0]
        data_processed += f"{dispaly_name}: {data[1]['player_name']}\n"
        last_access = data[1]["last_access"]
        data_processed += f"Last opened: {u.make_date(last_access, '.')} {u.make_time(last_access[3:])}"
        # check version
        try: save_version = data[1]["save_version"]
        except KeyError: save_version = 0.0
        data_processed += u.stylized_text(f" v.{save_version}", (Color.GREEN if save_version == SAVE_VERSION else Color.RED))
        return [data[0], data_processed]
    except (TypeError, IndexError):
        ts.log_info("Parse error", f"Save name: {data[0]}", Log_type.ERROR)
        dm.press_key(f"\"{data[0]}\" could not be parsed!")
        return None

def _get_save_folders() -> list[str]:
    folders = []
    items = os.listdir(SAVES_FOLDER_PATH)
    for item in items:
        if os.path.isdir(os.path.join(SAVES_FOLDER_PATH, item)):
            folders.append(item)
    folders.sort()
    return folders

def _get_valid_folders(folders:list[str]):
    datas = []
    for folder in folders:
        data = ts.decode_save_s(os.path.join(SAVES_FOLDER_PATH, folder, SAVE_FILE_NAME_DATA), 0)
        datas.append([folder, data])
    return datas

def get_saves_data():
    ts.recreate_saves_folder()
    # read saves
    datas = []
    # read from file (old)
    datas.extend(sfm.file_reader_blank(SAVE_SEED, SAVES_FOLDER_PATH, 1))
    for data in datas:
        data[1] = json.loads(data[1][0])
    # read from folder
    folders = _get_save_folders()
    datas.extend(_get_valid_folders(folders))
    # process file data
    datas_processed = []
    for data in datas:
        if data[1] == -1:
            ts.log_info("Decode error", f"Save name: {data[0]}", Log_type.ERROR)
            dm.press_key(f"\"{data[0]}\" is corrupted!")
        else:
            processed_data = _process_save_display_data(data)
            if processed_data != None:
                datas_processed.append(processed_data)
    return datas_processed