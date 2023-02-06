from copy import deepcopy
from typing import Any
from os.path import join, isfile
from os import listdir

from utils import Double_Keys, getch
from constants import                     \
    ENCODING,                             \
    SAVES_FOLDER_PATH, SAVE_EXT,          \
    SAVE_FOLDER_NAME_CHUNKS,              \
    CHUNK_FILE_NAME, CHUNK_FILE_NAME_SEP, \
    DOUBLE_KEYS, SAVE_VERSION
import tools as ts

from entities import Player


class Globals:
    in_game_loop:bool
    in_fight:bool
    exiting:bool
    saving:bool


    def __init__(self, in_game_loop:bool, in_fight:bool, exiting:bool, saving:bool):
        Globals.in_game_loop = bool(in_game_loop)
        Globals.in_fight = bool(in_fight)
        Globals.exiting = bool(exiting)
        Globals.saving = bool(saving)


class Key:
    def __init__(self, value:list[list[bytes]]):
        self.set_value(value)
        self.conflict = False


    def set_name(self):
        if len(self.value[0]) > 0:
            match self.value[0][0]:
                case b"\r":
                    self.name = "enter"
                case b"\x1b":
                    self.name = "escape"
                case b" ":
                    self.name = "space"
                case b"\x94":
                    self.name = "ö"
                case b"\x99":
                    self.name = "Ö"
                case b"\x81":
                    self.name = "ü"
                case b"\x9a":
                    self.name = "Ü"
                case b"\xa2":
                    self.name = "ó"
                # case b"\xe0":
                #     self.name = "Ó"
                case b"\xa3":
                    self.name = "ú"
                case b"\xe9":
                    self.name = "Ú"
                case b"\xfb":
                    self.name = "ű"
                case b"\xeb":
                    self.name = "Ű"
                case b"\xa0":
                    self.name = "á"
                case b"\xb5":
                    self.name = "Á"
                case b"\x82":
                    self.name = "é"
                case b"\x90":
                    self.name = "É"
                case b"\xa1":
                    self.name = "í"
                case b"\xd6":
                    self.name = "Í"
                case b"\x8b":
                    self.name = "ő"
                case b"\x8a":
                    self.name = "Ő"
                case _:
                    self.name = self.value[0][0].decode(ENCODING)
        else:
            match self.value[1][0]:
                case Double_Keys.ARROW_UP.value:
                    self.name = "up arrow"
                case Double_Keys.ARROW_DOWN.value:
                    self.name = "down arrow"
                case Double_Keys.ARROW_LEFT.value:
                    self.name = "left arrow"
                case Double_Keys.ARROW_RIGHT.value:
                    self.name = "right arrow"
                case Double_Keys.NUM_0.value:
                    self.name = "num 0"
                case Double_Keys.NUM_1.value:
                    self.name = "num 1"
                case Double_Keys.NUM_3.value:
                    self.name = "num 3"
                case Double_Keys.NUM_7.value:
                    self.name = "num 7"
                case Double_Keys.NUM_9.value:
                    self.name = "num 9"
                case Double_Keys.DELETE.value:
                    self.name = "delete"
                case _:
                    self.name = self.value[1][0].decode(ENCODING)


    def set_value(self, key_value:list[list[bytes]]):
        try:
            if len(key_value[0]) > 0:
                key_value[0][0].decode(ENCODING)
            elif len(key_value) > 1 and len(key_value) > 0:
                key_value[1][0].decode(ENCODING)
            else:
                raise KeyError
        except UnicodeDecodeError:
            ts.logger("Unknown key", "cannot decode key", ts.Log_type.ERROR)
            raise
        else:
            self.value = key_value
            self.set_name()


    def change(self, key_value:list[list[bytes]]):
        try: self.set_value(key_value)
        except UnicodeDecodeError: pass


    def __str__(self):
        return f"{self.name}: {self.value}"


class Settings:
    DOUBLE_KEYS = DOUBLE_KEYS
    auto_save:bool
    logging_level:int
    keybinds:dict[str, Key]
    ask_package_check_fail:bool
    ask_delete_save:bool
    ask_regenerate_save:bool
    def_backup_action:int
    keybind_mapping:tuple[list[list[list[bytes]]], list[bytes]]


    def __init__(self, auto_save:bool|None=None, logging_level:int|None=None, keybinds:dict[str, list[list[bytes]]]|None=None,
                ask_package_check_fail:bool|None=None, ask_delete_save:bool|None=None, ask_regenerate_save:bool|None=None, def_backup_action:int|None=None):
        if auto_save is None:
            auto_save = Settings.get_auto_save()
        if logging_level is None:
            logging_level = Settings.get_logging_level()
        if keybinds is None:
            keybind_obj = Settings.get_keybins()
        else:
            keybind_obj = {}
            for key in keybinds:
                keybind_obj[key] = Key(keybinds[key])
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
        Settings.keybinds = dict[str, Key](keybind_obj)
        Settings.ask_package_check_fail = bool(ask_package_check_fail)
        Settings.ask_delete_save = bool(ask_delete_save)
        Settings.ask_regenerate_save = bool(ask_regenerate_save)
        Settings.def_backup_action = int(def_backup_action)
        Settings.update_keybinds()
    

    @staticmethod
    def get_auto_save():
        """Returns the value of the `auto_save` from the setting file."""
        return bool(ts.settings_manager("auto_save"))
    

    @staticmethod
    def get_logging_level():
        """Returns the value of the `logging_level` from the setting file."""
        return int(ts.settings_manager("logging_level"))
    

    @staticmethod
    def get_keybins():
        """Returns the value of the `keybinds` from the setting file."""
        keybinds:dict[str, list[list[bytes]]] = ts.settings_manager("keybinds")
        keybind_obj:dict[str, Key] = {}
        for key in keybinds:
            keybind_obj[key] = Key(keybinds[key])
        return keybind_obj
    
    
    @staticmethod
    def get_ask_package_check_fail():
        """Returns the value of the `ask_package_check_fail` from the setting file."""
        return bool(ts.settings_manager("ask_package_check_fail"))
    
    
    @staticmethod
    def get_ask_delete_save():
        """Returns the value of the `ask_delete_save` from the setting file."""
        return bool(ts.settings_manager("ask_delete_save"))
    
    
    @staticmethod
    def get_ask_regenerate_save():
        """Returns the value of the `ask_regenerate_save` from the setting file."""
        return bool(ts.settings_manager("ask_regenerate_save"))
    
    
    @staticmethod
    def get_def_backup_action():
        """Returns the value of the `def_backup_action` from the setting file."""
        return int(ts.settings_manager("def_backup_action"))


    @staticmethod
    def update_logging_level(logging_level:int):
        """Updates the value of the `logging_level` in the program and in the setting file."""
        Settings.logging = (int(logging_level) != -1)
        Settings.logging_level = int(logging_level)
        ts.settings_manager("logging_level", Settings.logging_level)
        ts.change_logging_level(Settings.logging_level)


    @staticmethod
    def update_auto_save(auto_save:bool):
        """Updates the value of the `auto_save` in the program and in the setting file."""
        Settings.auto_save = bool(auto_save)
        ts.settings_manager("auto_save", Settings.auto_save)


    @staticmethod
    def _encode_keybinds():
        """Returns a json formated deepcopy of the `keybinds`."""
        return {"esc": deepcopy(Settings.keybinds["esc"].value),
        "up": deepcopy(Settings.keybinds["up"].value),
        "down": deepcopy(Settings.keybinds["down"].value),
        "left": deepcopy(Settings.keybinds["left"].value),
        "right": deepcopy(Settings.keybinds["right"].value),
        "enter": deepcopy(Settings.keybinds["enter"].value)}


    @staticmethod
    def update_keybinds():
        """Updates the value of the `keybind_mapping` in the program and in the setting file, with the `keybinds`."""
        # ([keybinds["esc"], keybinds["up"], keybinds["down"], keybinds["left"], keybinds["right"], keybinds["enter"]], [b"\xe0", b"\x00"])
        # ([[[b"\x1b"]],     [[], [b"H"]],   [[], [b"P"]],     [[], [b"K"]],     [[], [b"M"]],      [[b"\r"]]],         [b"\xe0", b"\x00"])
        Settings.keybind_mapping = ([
            Settings.keybinds["esc"].value,
            Settings.keybinds["up"].value,
            Settings.keybinds["down"].value,
            Settings.keybinds["left"].value,
            Settings.keybinds["right"].value,
            Settings.keybinds["enter"].value], Settings.DOUBLE_KEYS)
        ts.settings_manager("keybinds", Settings._encode_keybinds())


    @staticmethod
    def check_keybind_conflicts():
        for key in Settings.keybinds:
            Settings.keybinds[key].conflict = False
        for key1 in Settings.keybinds:
            for key2 in Settings.keybinds:
                if key1 != key2:
                    if Settings.keybinds[key1].value == Settings.keybinds[key2].value:
                        Settings.keybinds[key1].conflict = True
                        Settings.keybinds[key2].conflict = True


    @staticmethod
    def update_ask_package_check_fail(ask_package_check_fail:bool):
        """Updates the value of `ask_package_check_fail` in the program and in the setting file."""
        Settings.ask_package_check_fail = bool(ask_package_check_fail)
        ts.settings_manager("ask_package_check_fail", Settings.ask_package_check_fail)


    @staticmethod
    def update_ask_delete_save(ask_delete_save:bool):
        """Updates the value of `ask_delete_save` in the program and in the setting file."""
        Settings.ask_delete_save = bool(ask_delete_save)
        ts.settings_manager("ask_delete_save", Settings.ask_delete_save)


    @staticmethod
    def update_ask_regenerate_save(ask_regenerate_save:bool):
        """Updates the value of `ask_regenerate_save` in the program and in the setting file."""
        Settings.ask_regenerate_save = bool(ask_regenerate_save)
        ts.settings_manager("ask_regenerate_save", Settings.ask_regenerate_save)


    @staticmethod
    def update_def_backup_action(def_backup_action:int):
        """Updates the value of `def_backup_action` in the program and in the setting file."""
        Settings.def_backup_action = int(def_backup_action)
        ts.settings_manager("def_backup_action", Settings.def_backup_action)


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


def is_key(key:Key):
    """
    Waits for a specific key.
    """

    key_in = getch()
    arrow = False
    if key_in in DOUBLE_KEYS:
        arrow = True
        key_in = getch()
    
    return ((not arrow and len(key.value) > 0 and key_in in key.value[0]) or
            (arrow and len(key.value) > 1 and key_in in key.value[1]))
