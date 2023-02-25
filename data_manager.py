from copy import deepcopy
from enum import Enum
from typing import Any
from os.path import join, isfile
from os import listdir

from utils import Double_keys, getwch, kbhit
from constants import                     \
    SAVES_FOLDER_PATH, SAVE_EXT,          \
    SAVE_FOLDER_NAME_CHUNKS,              \
    CHUNK_FILE_NAME, CHUNK_FILE_NAME_SEP, \
    DOUBLE_KEYS, SAVE_VERSION
import tools as ts
from save_file_manager import Keybinds, Key_action, Keys, Get_key_modes
from entities import Player
from keybinds import Action_keybinds, Action_key


class Globals:
    in_game_loop:bool
    in_fight:bool
    exiting:bool
    saving:bool


    def __init__(self, in_game_loop=False, in_fight=False, exiting=False, saving=False):
        Globals.in_game_loop = bool(in_game_loop)
        Globals.in_fight = bool(in_fight)
        Globals.exiting = bool(exiting)
        Globals.saving = bool(saving)


class Settings:
    auto_save:bool
    logging_level:int
    keybinds:Action_keybinds
    ask_package_check_fail:bool
    ask_delete_save:bool
    ask_regenerate_save:bool
    def_backup_action:int


    def __init__(self, auto_save:bool|None=None, logging_level:int|None=None, keybinds:Action_keybinds|None=None,
                ask_package_check_fail:bool|None=None, ask_delete_save:bool|None=None, ask_regenerate_save:bool|None=None, def_backup_action:int|None=None):
        if auto_save is None:
            auto_save = Settings.get_auto_save()
        if logging_level is None:
            logging_level = Settings.get_logging_level()
        if keybinds is None:
            keybinds = Settings.get_keybins()
        if ask_package_check_fail is None:
            ask_package_check_fail = Settings.get_ask_package_check_fail()
        if ask_delete_save is None:
            ask_delete_save = Settings.get_ask_delete_save()
        if ask_regenerate_save is None:
            ask_regenerate_save = Settings.get_ask_regenerate_save()
        if def_backup_action is None:
            def_backup_action = Settings.get_def_backup_action()
        Settings.auto_save = bool(auto_save)
        Settings.logging = (int(logging_level) != -1)
        Settings.logging_level = int(logging_level)
        Settings.keybinds = keybinds
        Settings.ask_package_check_fail = bool(ask_package_check_fail)
        Settings.ask_delete_save = bool(ask_delete_save)
        Settings.ask_regenerate_save = bool(ask_regenerate_save)
        Settings.def_backup_action = int(def_backup_action)
        ts.change_logging_level(Settings.logging_level)
        Settings.check_keybind_conflicts()
    

    @staticmethod
    def get_auto_save():
        """Returns the value of the `auto_save` from the setting file."""
        return bool(ts.settings_manager(ts.Settings_keys.AUTO_SAVE))
    

    @staticmethod
    def get_logging_level():
        """Returns the value of the `logging_level` from the setting file."""
        return int(ts.settings_manager(ts.Settings_keys.LOGGING_LEVEL))
    

    @staticmethod
    def get_keybins():
        """Returns the value of the `keybinds` from the setting file."""
        keybinds:Action_keybinds = ts.settings_manager(ts.Settings_keys.KEYBINDS)
        return keybinds
    
    
    @staticmethod
    def get_ask_package_check_fail():
        """Returns the value of the `ask_package_check_fail` from the setting file."""
        return bool(ts.settings_manager(ts.Settings_keys.ASK_PACKAGE_CHECK_FAIL))
    
    
    @staticmethod
    def get_ask_delete_save():
        """Returns the value of the `ask_delete_save` from the setting file."""
        return bool(ts.settings_manager(ts.Settings_keys.ASK_DELETE_SAVE))
    
    
    @staticmethod
    def get_ask_regenerate_save():
        """Returns the value of the `ask_regenerate_save` from the settings file."""
        return bool(ts.settings_manager(ts.Settings_keys.ASK_REGENERATE_SAVE))
    
    
    @staticmethod
    def get_def_backup_action():
        """Returns the value of the `def_backup_action` from the settings file."""
        return int(ts.settings_manager(ts.Settings_keys.DEF_BACKUP_ACTION))


    @staticmethod
    def update_logging_level(logging_level:int):
        """Updates the value of the `logging_level` in the program and in the settings file."""
        Settings.logging = (int(logging_level) != -1)
        Settings.logging_level = int(logging_level)
        ts.settings_manager(ts.Settings_keys.LOGGING_LEVEL, Settings.logging_level)
        ts.change_logging_level(Settings.logging_level)


    @staticmethod
    def update_auto_save(auto_save:bool):
        """Updates the value of the `auto_save` in the program and in the settings file."""
        Settings.auto_save = bool(auto_save)
        ts.settings_manager(ts.Settings_keys.AUTO_SAVE, Settings.auto_save)      


    @staticmethod
    def update_keybinds(keybinds:Action_keybinds):
        """Updates the value of the `keybinds` in the program and in the settings file."""
        Settings.keybinds = keybinds
        ts.settings_manager(ts.Settings_keys.KEYBINDS, keybinds)


    @staticmethod
    def check_keybind_conflicts(keybinds:Action_keybinds|None=None):
        """Checks the keybinds for keybind conflicts."""
        if keybinds is None:
            keybinds = Settings.keybinds
        for key in keybinds._actions:
            key.conflict = False
        for key1 in keybinds._actions:
            for key2 in keybinds._actions:
                if key1 != key2:
                    if (
                        len(key1.normal_keys) > 0 and len(key2.normal_keys) > 0 and  key1.normal_keys[0] == key2.normal_keys[0]
                        ) or (
                        len(key1.arrow_keys) > 0 and len(key2.arrow_keys) > 0 and key1.arrow_keys[0] == key2.arrow_keys[0]):
                        key1.conflict = True
                        key2.conflict = True


    @staticmethod
    def update_ask_package_check_fail(ask_package_check_fail:bool):
        """Updates the value of `ask_package_check_fail` in the program and in the setting file."""
        Settings.ask_package_check_fail = bool(ask_package_check_fail)
        ts.settings_manager(ts.Settings_keys.ASK_PACKAGE_CHECK_FAIL, Settings.ask_package_check_fail)


    @staticmethod
    def update_ask_delete_save(ask_delete_save:bool):
        """Updates the value of `ask_delete_save` in the program and in the setting file."""
        Settings.ask_delete_save = bool(ask_delete_save)
        ts.settings_manager(ts.Settings_keys.ASK_DELETE_SAVE, Settings.ask_delete_save)


    @staticmethod
    def update_ask_regenerate_save(ask_regenerate_save:bool):
        """Updates the value of `ask_regenerate_save` in the program and in the setting file."""
        Settings.ask_regenerate_save = bool(ask_regenerate_save)
        ts.settings_manager(ts.Settings_keys.ASK_REGENERATE_SAVE, Settings.ask_regenerate_save)


    @staticmethod
    def update_def_backup_action(def_backup_action:int):
        """Updates the value of `def_backup_action` in the program and in the setting file."""
        Settings.def_backup_action = int(def_backup_action)
        ts.settings_manager(ts.Settings_keys.DEF_BACKUP_ACTION, Settings.def_backup_action)


class Save_data:
    save_name:str
    display_save_name:str
    last_access:list[int]
    player:Player
    main_seed:ts.np.random.RandomState
    world_seed:ts.np.random.RandomState
    tile_type_noise_seeds:dict[str, int]

    def __init__(self, save_name:str, display_save_name:str|None=None, last_access:list[int]|None=None, player:Player|None=None,
                 main_seed:ts.np.random.RandomState|None=None, world_seed:ts.np.random.RandomState|None=None, tile_type_noise_seeds:dict[str, int]|None=None):
        Save_data.save_name = str(save_name)
        if display_save_name is None:
            display_save_name = Save_data.save_name
        Save_data.display_save_name = str(display_save_name)
        if last_access is None:
            now = ts.dtime.now()
            last_access = [now.year, now.month, now.day, now.hour, now.minute, now.second]
        Save_data.last_access = list[int](last_access)
        if player is None:
            player = Player()
        Save_data.player = player
        if main_seed is None:
            main_seed = ts.np.random.RandomState()
        Save_data.main_seed = main_seed
        if world_seed is None:
            world_seed = ts.make_random_seed(Save_data.main_seed)
        Save_data.world_seed = world_seed
        if tile_type_noise_seeds is None:
            tile_type_noise_seeds = ts.recalculate_tile_type_noise_seeds(world_seed)
        Save_data.tile_type_noise_seeds = tile_type_noise_seeds
        Save_data._update_seed_values()
    

    @staticmethod
    def _update_seed_values():
        ts.main_seed = Save_data.main_seed
        ts.world_seed = Save_data.world_seed
        ts.tile_type_noise_seeds = Save_data.tile_type_noise_seeds
        ts.recalculate_noise_generators(Save_data.tile_type_noise_seeds)
    

    @staticmethod
    def display_data_to_json():
        """Converts the data for the display part of the data file to a json format."""
        now = ts.dtime.now()
        display_data_json:dict[str, Any] = {
            "save_version": SAVE_VERSION,
            "display_name": Save_data.display_save_name,
            "last_access":  [now.year, now.month, now.day, now.hour, now.minute, now.second],
            "player_name":  Save_data.player.name
        }
        return display_data_json


    @staticmethod
    def seeds_to_json():
        """Converts the seeds data to json format."""
        seeds_json:dict[str, Any] = {
            "main_seed":                ts.random_state_to_json(Save_data.main_seed),
            "world_seed":               ts.random_state_to_json(Save_data.world_seed),
            "tile_type_noise_seeds":    Save_data.tile_type_noise_seeds
        }
        return seeds_json


    @staticmethod
    def main_data_to_json():
        """Converts the data for the main part of the data file to a json format."""
        now = ts.dtime.now()
        save_data_json:dict[str, Any] = {
            "save_version": SAVE_VERSION,
            "display_name": Save_data.display_save_name,
            "last_access":  [now.year, now.month, now.day, now.hour, now.minute, now.second],
            "player":       Save_data.player.to_json(),
            "seeds":        Save_data.seeds_to_json()
        }
        return save_data_json


def is_key(key:Action_key, allow_buffered_inputs=False):
    """
    Waits for a specific key.
    """

    if not allow_buffered_inputs:
        while kbhit():
            getwch()
    key_in = getwch()
    arrow = False
    if key_in in DOUBLE_KEYS:
        arrow = True
        key_in = getwch()
    
    return ((not arrow and key_in in key.normal_keys) or
            (arrow and key_in in key.arrow_keys))
