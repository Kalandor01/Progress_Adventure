import json
import os
from datetime import datetime as dtime
from typing import Any, Literal

import utils as u
import tools as ts
from data_manager import Save_data
import entities as es
import inventory as iy
from chunk_manager import World

from utils import Color
from tools import r, sfm, Log_type
from constants import                               \
    SAVES_FOLDER_PATH, OLD_SAVE_NAME, SAVE_EXT,     \
    SAVE_FILE_NAME_DATA, SAVE_FOLDER_NAME_CHUNKS,   \
    SAVE_SEED,                                      \
    SAVE_VERSION


def _save_display_json(data:Save_data):
    """Converts the display data to json format."""
    display_data:dict[str, Any] = {}
    display_data["save_version"] = SAVE_VERSION
    display_data["display_name"] = data.display_save_name
    now = dtime.now()
    last_access = [now.year, now.month, now.day, now.hour, now.minute, now.second]
    display_data["last_access"] = last_access
    display_data["player_name"] = data.player.name
    return display_data


def _save_player_json(player_data:es.Player):
    """Converts the player data to json format."""
    player_json = {
                    "name": player_data.name,
                    "hp": player_data.hp,
                    "attack": player_data.attack,
                    "defence": player_data.defence,
                    "speed": player_data.speed,
                    "x_pos": player_data.pos[0],
                    "y_pos": player_data.pos[1],
                    "rotation": player_data.rotation.value
                    }
    player_json["inventory"] = player_data.inventory.to_json()
    return player_json


def _load_inventory_json(inventory_json:list):
    """Converts the inventory json to object format."""
    items = []
    for item in inventory_json:
        item_type = iy.item_finder(item[0])
        if item_type is not None:
            items.append(iy.Item(item_type, item[1]))
    return items


def _load_player_json(player_json:dict[str, Any]):
    """Converts the player json to object format."""
    player = es.Player(player_json["name"])
    player.hp = int(player_json["hp"])
    player.attack = int(player_json["attack"])
    player.defence = int(player_json["defence"])
    player.speed = int(player_json["speed"])
    player.inventory.items = list(_load_inventory_json(player_json["inventory"]))
    player.pos = (int(player_json["x_pos"]), int(player_json["y_pos"]))
    player.rotation = es.Rotation(es.Rotation._value2member_map_[int(player_json["rotation"])])
    return player


def _save_data_json(data:Save_data):
    """Converts the miscellaneous data to json format."""
    save_data_json:dict[str, Any] = {}
    # save_version
    save_data_json["save_version"] = SAVE_VERSION
    # display_name
    save_data_json["display_name"] = data.display_save_name
    # last_access
    now = dtime.now()
    last_access = [now.year, now.month, now.day, now.hour, now.minute, now.second]
    save_data_json["last_access"] = last_access
    # player
    save_data_json["player"] = _save_player_json(data.player)
    # randomstate
    save_data_json["seed"] = ts.random_state_to_json(r)
    return save_data_json


def _load_world_json(x:int, y:int, save_folder:str):
    """Converts the world json to object format."""
    world = World()
    world.load_chunk_from_folder(x, y, save_folder)
    return world


def make_save(data:Save_data, actual_data:Save_data|None=None, clear_chunks=True):
    """
    Creates a save file from the save data.\n
    Makes a temporary backup.
    """
    # make backup
    backup_status = ts.make_backup(data.save_name, True)
    # FOLDER
    ts.recreate_folder(data.save_name, SAVES_FOLDER_PATH, "save file")
    save_folder = os.path.join(SAVES_FOLDER_PATH, data.save_name)
    # DATA FILE
    # display data
    display_data = _save_display_json(data)
    save_data = _save_data_json(data)
    # create new save
    ts.encode_save_s([display_data, save_data], os.path.join(save_folder, SAVE_FILE_NAME_DATA))
    # CHUNKS/WORLD
    ts.recreate_folder(SAVE_FOLDER_NAME_CHUNKS, save_folder)
    # WORKING WITH ACTUAL DATA
    if actual_data is None:
        actual_data = data
    ts.logger("Saving chunks")
    actual_data.world.save_all_chunks_to_files(save_folder, clear_chunks)
    # remove backup
    if backup_status != False:
        os.remove(backup_status[0])
        ts.logger("Removed temporary backup", backup_status[1], Log_type.DEBUG)


def create_save_data():
    """Creates the data for a new save file."""
    ts.logger("Preparing game data")
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
    save_data = Save_data(save_name, display_save_name, last_access, player, r.get_state())
    save_data.world.gen_tile(save_data.player.pos[0], save_data.player.pos[1])
    return save_data


def correct_save_data(data:dict[str, Any], save_version:str, extra_data:dict[str, Any]):
    """Modifys the save data, to make it up to date, with the newest save file data structure."""
    ts.logger("Correcting save data")
    # 0.0 -> 1.0
    if save_version == "0.0":
        # added save varsions
        save_version = "1.0"
        ts.logger("Corrected save data", "0.0 -> 1.0", Log_type.DEBUG)
    # 1.0 -> 1.1
    if save_version == "1.0":
        # added player inventory
        data["player"]["inventory"] = []
        save_version = "1.1"
        ts.logger("Corrected save data", "1.0 -> 1.1", Log_type.DEBUG)
    # 1.1 -> 1.2
    if save_version == "1.1":
        # added display save name
        data["display_name"] = extra_data["save_name"]
        save_version = "1.2"
        ts.logger("Corrected save data", "1.1 -> 1.2", Log_type.DEBUG)
    # 1.2 -> 1.3
    if save_version == "1.2":
        # switched from file to folder
        save_version = "1.3"
        ts.logger("Corrected save data", "1.2 -> 1.3", Log_type.DEBUG)
    # 1.3 -> 1.4
    if save_version == "1.3":
        # added chunks + player position/rotation
        data["player"]["x_pos"] = 0
        data["player"]["y_pos"] = 0
        data["player"]["rotation"] = "UP"
        save_version = "1.4"
        ts.logger("Corrected save data", "1.3 -> 1.4", Log_type.DEBUG)
    # 1.4 -> 1.4.1
    if save_version == "1.4":
        # renamed facings up, down... to 0, 1..
        p_rot:str = data["player"]["rotation"]
        if p_rot == "DOWN":
            data["player"]["rotation"] = 1
        elif p_rot == "LEFT":
            data["player"]["rotation"] = 2
        elif p_rot == "RIGHT":
            data["player"]["rotation"] = 3
        else:
            data["player"]["rotation"] = 0
        save_version = "1.4.1"
        ts.logger("Corrected save data", "1.4 -> 1.4.1", Log_type.DEBUG)
    return data


def load_save(save_name:str, keybind_mapping:tuple[list[list[list[bytes]]], list[bytes]], is_file=False):
    """Loads a save file into a `Save_data` object."""
    full_save_name = os.path.join(SAVES_FOLDER_PATH, save_name)
    # get if save is a file
    if is_file and os.path.isfile(f'{full_save_name}.{SAVE_EXT}'):
        data = ts.decode_save_s(full_save_name, 1, can_be_old=True)
        save_name = ts.correct_save_name(save_name)
        old_full_save_name = full_save_name
        full_save_name = os.path.join(SAVES_FOLDER_PATH, save_name)
        os.rename(f"{old_full_save_name}.{SAVE_EXT}", f"{full_save_name}.{SAVE_EXT}")
    else:
        data = ts.decode_save_s(os.path.join(full_save_name, SAVE_FILE_NAME_DATA, ), 1)
        is_file = False
    # read data
    
    # save version
    try: save_version = str(data["save_version"])
    except KeyError: save_version = "0.0"
    if save_version != SAVE_VERSION:
        is_older = ts.is_up_to_date(save_version, SAVE_VERSION)
        ts.logger("Trying to load save with an incorrect version", f"{save_version} -> {SAVE_VERSION}", Log_type.WARN)
        ans = sfm.UI_list(["Yes", "No"], f"\"{save_name}\" is {('an older version' if is_older else 'a newer version')} than what it should be! Do you want to back up the save file before loading it?").display(keybind_mapping)
        if ans == 0:
            ts.make_backup(save_name)
        # delete save file
        if is_file:
            os.remove(f'{full_save_name}.{SAVE_EXT}')
            ts.logger("Removed save file", "single save files have been deprecated", Log_type.WARN)
        # correct
        data = correct_save_data(data, save_version, {"save_name": save_name})
    # display_name
    display_name = str(data["display_name"])
    # last access
    last_access:list[int] = data["last_access"]
    # player
    player_data:dict[str, Any] = data["player"]
    player = _load_player_json(player_data)
    # world
    ts.logger("Loading world")
    world = _load_world_json(player.pos[0], player.pos[1], full_save_name)
    ts.logger("Loaded save", f'save name: {save_name}, player name: "{player.name}", last saved: {u.make_date(last_access)} {u.make_time(last_access[3:])}')
    
    # PREPARING
    ts.logger("Preparing game data")
    # load random state
    r.set_state(ts.json_to_random_state(data["seed"]))
    # load to class
    save_data = Save_data(save_name, display_name, last_access, player, r.get_state(), world)
    if is_file:
        make_save(save_data, clear_chunks=False)
    return save_data


def _process_save_display_data(data:tuple[str, dict[str, Any] | Literal[-1]]):
    """Turns the json display data from a json into more uniform data."""
    try:
        if data[1] != -1:
            data_processed = ""
            try:
                dispaly_name = data[1]['display_name']
            except KeyError:
                dispaly_name = data[0]
            data_processed += f"{dispaly_name}: {data[1]['player_name']}\n"
            last_access = data[1]["last_access"]
            data_processed += f"Last opened: {u.make_date(last_access, '.')} {u.make_time(last_access[3:])}"
            # check version
            try: save_version = str(data[1]["save_version"])
            except KeyError: save_version = "0.0"
            data_processed += u.stylized_text(f" v.{save_version}", (Color.GREEN if save_version == SAVE_VERSION else Color.RED))
            return (data[0], data_processed, not ts.is_up_to_date("1.3", save_version))
        else:
            raise IndexError
    except (TypeError, IndexError):
        ts.logger("Parse error", f"Save name: {data[0]}", Log_type.ERROR)
        ts.press_key(f"\"{data[0]}\" could not be parsed!")
        return None

def _get_save_folders() -> list[str]:
    """Gets all folders from the save folder."""
    folders = []
    items = os.listdir(SAVES_FOLDER_PATH)
    for item in items:
        if os.path.isdir(os.path.join(SAVES_FOLDER_PATH, item)):
            folders.append(item)
    folders.sort()
    return folders

def _get_valid_folders(folders:list[str]):
    """Gets the display data from all readable save files in the save folder."""
    datas:list[tuple[str, dict[str, Any]]] = []
    for folder in folders:
        data = ts.decode_save_s(os.path.join(SAVES_FOLDER_PATH, folder, SAVE_FILE_NAME_DATA), 0)
        datas.append((folder, data))
    return datas

def get_saves_data():
    """Gets all save files from the save folder, and proceses them for diplay."""
    ts.recreate_saves_folder()
    # read saves
    datas:list[tuple[str, dict[str, Any]|Literal[-1]]] = []
    # read from numbered file (very old)!
    datas_very_old = sfm.file_reader(-1, OLD_SAVE_NAME, SAVE_EXT, SAVES_FOLDER_PATH, True, 1)
    for data in datas_very_old:
        # fix data
        fix_name = OLD_SAVE_NAME.replace("*", str(data[0]))
        fix_data:dict[str, Any]|Literal[-1] = -1
        if data[1] != -1:
            fix_data:dict[str, Any]|Literal[-1] = json.loads(data[1][0])
        datas.append((fix_name, fix_data))
    # read from file (old)
    datas_old = sfm.file_reader_blank(SAVE_SEED, SAVES_FOLDER_PATH, 1)
    for data in datas_old:
        # fix data
        fix_data:dict[str, Any]|Literal[-1] = -1
        if data[1] != -1:
            fix_data:dict[str, Any]|Literal[-1] = json.loads(data[1][0])
        found = False
        index = -1
        for x in range(len(datas)):
            if datas[x][0] == data[0]:
                found = True
                if datas[x][1] == -1:
                    index = x
                break
        if not found:
            datas.append((data[0], fix_data))
        elif index != -1:
            datas[index] = (data[0], fix_data)
                
    # read from folder
    folders = _get_save_folders()
    datas.extend(_get_valid_folders(folders))
    # process file data
    datas_processed:list[tuple[str, str, bool]] = []
    for data in datas:
        if data[1] == -1:
            ts.logger("Decode error", f"save name: {data[0]}(.{SAVE_EXT})", Log_type.ERROR)
            ts.press_key(f"\"{data[0]}\" is corrupted!")
        else:
            processed_data = _process_save_display_data(data)
            if processed_data is not None:
                datas_processed.append(processed_data)
    return datas_processed