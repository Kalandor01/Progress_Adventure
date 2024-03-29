import json
import os
from typing import Any, Literal

import utils as u
import tools as ts
from data_manager import Save_data, Settings
from chunk_manager import World
import entities as es
import inventory as iy

from utils import Color
from tools import sfm, Log_type
from constants import                             \
    SAVES_FOLDER_PATH, OLD_SAVE_NAME, SAVE_EXT,   \
    SAVE_FILE_NAME_DATA, SAVE_FOLDER_NAME_CHUNKS, \
    SAVE_SEED, SAVE_VERSION


def _load_inventory_json(inventory_json:list[dict[str, Any]]):
    """Converts the inventory json to object format."""
    items:list[iy.Item] = []
    for item in inventory_json:
        item_type = iy.item_finder(item["type"])
        if item_type is not None:
            items.append(iy.Item(item_type, item["amount"]))
    inventory = iy.Inventory(items)
    return inventory


def _load_player_json(player_json:dict[str, Any]):
    """Converts the player json to object format."""
    name = player_json["name"]
    base_hp = int(player_json["base_hp"])
    base_attack = int(player_json["base_attack"])
    base_defence = int(player_json["base_defence"])
    base_speed = int(player_json["base_speed"])
    inventory = _load_inventory_json(player_json["inventory"])
    position = (int(player_json["x_pos"]), int(player_json["y_pos"]))
    rotation = es.Rotation(es.Rotation._value2member_map_[int(player_json["rotation"])])

    player = es.Player(name, base_hp, base_attack, base_defence, base_speed, inventory, position, rotation)
    player._apply_attributes()
    player.update_full_name()
    return player


def _save_data_file():
    """
    Creates the data file part of a save file from the save data.
    """
    # FOLDER
    ts.recreate_folder(Save_data.save_name, SAVES_FOLDER_PATH, "save file")
    save_folder_path = os.path.join(SAVES_FOLDER_PATH, Save_data.save_name)
    # DATA FILE
    display_data_json = Save_data.display_data_to_json()
    save_data_json = Save_data.main_data_to_json()
    # create new save
    ts.encode_save_s([display_data_json, save_data_json], os.path.join(save_folder_path, SAVE_FILE_NAME_DATA))


def make_save(clear_chunks=True, show_progress_text: str | None = None):
    """
    Creates a save file from the save data.\n
    Makes a temporary backup.\n
    If `show_progress_text` is not None, it writes out a progress percentage while saving.
    """
    # make backup
    backup_status = ts.make_backup(Save_data.save_name, True)
    # FOLDER
    ts.recreate_folder(Save_data.save_name, SAVES_FOLDER_PATH, "save file")
    save_folder_path = os.path.join(SAVES_FOLDER_PATH, Save_data.save_name)
    # DATA FILE
    _save_data_file()
    # CHUNKS/WORLD
    ts.recreate_folder(SAVE_FOLDER_NAME_CHUNKS, save_folder_path)
    ts.logger("Saving chunks")
    World.save_all_chunks_to_files(save_folder_path, clear_chunks, show_progress_text)
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
    # load to class
    Save_data(save_name, display_save_name, player=player)
    World()
    World.gen_tile(Save_data.player.pos[0], Save_data.player.pos[1])


def correct_save_data(json_data:dict[str, Any], save_version:str, extra_data:dict[str, Any]):
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
        json_data["player"]["inventory"] = []
        save_version = "1.1"
        ts.logger("Corrected save data", "1.0 -> 1.1", Log_type.DEBUG)
    # 1.1 -> 1.2
    if save_version == "1.1":
        # added display save name
        json_data["display_name"] = extra_data["save_name"]
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
        json_data["player"]["x_pos"] = 0
        json_data["player"]["y_pos"] = 0
        json_data["player"]["rotation"] = "UP"
        save_version = "1.4"
        ts.logger("Corrected save data", "1.3 -> 1.4", Log_type.DEBUG)
    # 1.4 -> 1.4.1
    if save_version == "1.4":
        # renamed facings up, down... to 0, 1..
        p_rot:str = json_data["player"]["rotation"]
        if p_rot == "DOWN":
            json_data["player"]["rotation"] = 1
        elif p_rot == "LEFT":
            json_data["player"]["rotation"] = 2
        elif p_rot == "RIGHT":
            json_data["player"]["rotation"] = 3
        else:
            json_data["player"]["rotation"] = 0
        save_version = "1.4.1"
        ts.logger("Corrected save data", "1.4 -> 1.4.1", Log_type.DEBUG)
    # 1.4.1 -> 1.5
    if save_version == "1.4.1":
        # multiple seeds
        ts.main_seed.set_state(ts.json_to_random_state(json_data["seed"]))
        ts.world_seed = ts.make_random_seed(ts.main_seed)
        ttn_seeds = {
            "danger": ts.make_perlin_noise_seed(ts.world_seed),
            "height": ts.make_perlin_noise_seed(ts.world_seed),
            "temperature": ts.make_perlin_noise_seed(ts.world_seed),
            "humidity": ts.make_perlin_noise_seed(ts.world_seed)
        }
        m_seed = ts.random_state_to_json(ts.main_seed)
        w_seed = ts.random_state_to_json(ts.world_seed)
        
        json_data["seeds"] = {
            "main_seed": m_seed,
            "world_seed": w_seed,
            "tile_type_noise_seeds": ttn_seeds
        }
        save_version = "1.5"
        ts.logger("Corrected save data", "1.4.1 -> 1.5", Log_type.DEBUG)
    # 1.5 -> 1.5.1
    if save_version == "1.5":
        # ttn_seeds: population
        ts.world_seed.set_state(ts.json_to_random_state(json_data["seeds"]["world_seed"]))
        ttn_seeds = json_data["seeds"]["tile_type_noise_seeds"]["population"] = ts.make_perlin_noise_seed(ts.world_seed)
        json_data["seeds"]["world_seed"] = ts.random_state_to_json(ts.world_seed)
        save_version = "1.5.1"
        ts.logger("Corrected save data", "1.5 -> 1.5.1", Log_type.DEBUG)
    # 1.5.1 -> 1.5.2
    if save_version == "1.5.1":
        # ttn_seeds: danger -> hostility
        json_data["seeds"]["tile_type_noise_seeds"]["hostility"] = json_data["seeds"]["tile_type_noise_seeds"]["danger"]
        save_version = "1.5.2"
        ts.logger("Corrected save data", "1.5.1 -> 1.5.2", Log_type.DEBUG)
    # 1.5.2 -> 1.5.3
    if save_version == "1.5.2":
        # entity properties updated + inventory to dict
        player = json_data["player"]
        player["base_hp"] = player["hp"]
        player["base_attack"] = player["attack"]
        player["base_defence"] = player["defence"]
        player["base_speed"] = player["speed"]
        inventory = []
        for item in player["inventory"]:
            inventory.append({
                "type": item[0],
                "amount": item[1] 
            })
        player["inventory"] = inventory
        save_version = "1.5.3"
        ts.logger("Corrected save data", "1.5.2 -> 1.5.3", Log_type.DEBUG)
    return json_data


def load_save(save_name:str, is_file=False, backup_choice=True, automatic_backup=True):
    """
    Loads a save file into the `Save_data` object.\n
    If `backup_choice` is False the user can't choose wether or not to backup the save before loading it, or not, depending on `automatic_backup`.
    """
    
    save_folder_path = os.path.join(SAVES_FOLDER_PATH, save_name)
    # get if save is a file
    if is_file and os.path.isfile(f'{save_folder_path}.{SAVE_EXT}'):
        data = ts.decode_save_s(save_folder_path, 1, can_be_old=True)
        save_name = ts.correct_save_name(save_name)
        old_save_folder_path = save_folder_path
        save_folder_path = os.path.join(SAVES_FOLDER_PATH, save_name)
        os.rename(f"{old_save_folder_path}.{SAVE_EXT}", f"{save_folder_path}.{SAVE_EXT}")
    elif not is_file and os.path.isdir(save_folder_path):
        data = ts.decode_save_s(os.path.join(save_folder_path, SAVE_FILE_NAME_DATA, ), 1)
        is_file = False
    else:
        s_type = "file" if is_file else "folder"
        ts.logger(f"Not a valid save {s_type}", f"{s_type} name: {save_name}", Log_type.ERROR)
        raise FileNotFoundError
    # read data
    
    # auto backup
    if not backup_choice and automatic_backup:
        ts.make_backup(save_name)
    
    # save version
    try: save_version = str(data["save_version"])
    except KeyError: save_version = "0.0"
    if save_version != SAVE_VERSION:
        # backup
        if backup_choice:
            is_older = ts.is_up_to_date(save_version, SAVE_VERSION)
            ts.logger("Trying to load save with an incorrect version", f"{save_version} -> {SAVE_VERSION}", Log_type.WARN)
            ans = sfm.UI_list(["Yes", "No"], f"\"{save_name}\" is {('an older version' if is_older else 'a newer version')} than what it should be! Do you want to backup the save file before loading it?").display(Settings.keybinds)
            if ans == 0:
                ts.make_backup(save_name)
        # delete save file
        if is_file:
            os.remove(f'{save_folder_path}.{SAVE_EXT}')
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
    ts.logger("Loaded save", f'save name: {save_name}, player name: "{player.full_name}", last saved: {u.make_date(last_access)} {u.make_time(last_access[3:])}')
    
    # PREPARING
    ts.logger("Preparing game data")
    # load seeds
    seeds = data["seeds"]
    ts.main_seed.set_state(ts.json_to_random_state(seeds["main_seed"]))
    ts.world_seed.set_state(ts.json_to_random_state(seeds["world_seed"]))
    ts.tile_type_noise_seeds = seeds["tile_type_noise_seeds"]
    # load to class
    Save_data(save_name, display_name, last_access, player, ts.main_seed, ts.world_seed, ts.tile_type_noise_seeds)
    World()
    if is_file:
        make_save(clear_chunks=False)


def _process_save_display_data(data:tuple[str, dict[str, Any] | Literal[-1]]):
    """
    Turns the json display data from a json into more uniform data.\n
    Returns a tuple of (save_name, display_text, is_file)
    """
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
    except (TypeError, IndexError, KeyError):
        ts.logger("Parse error", f"Save name: {data[0]}", Log_type.ERROR)
        u.press_key(f"\"{data[0]}\" could not be parsed!")
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
    datas:list[tuple[str, dict[str, Any]|Literal[-1]]] = []
    for folder in folders:
        try:
            data = ts.decode_save_s(os.path.join(SAVES_FOLDER_PATH, folder, SAVE_FILE_NAME_DATA), 0)
        except ValueError:
            data = -1
        datas.append((folder, data))
    return datas

def get_saves_data():
    """Gets all save files from the save folder, and proceses them for display."""
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
            u.press_key(f"\"{data[0]}\" is corrupted!")
        else:
            processed_data = _process_save_display_data(data)
            if processed_data is not None:
                datas_processed.append(processed_data)
    return datas_processed
