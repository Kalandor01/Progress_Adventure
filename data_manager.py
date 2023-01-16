from copy import deepcopy
from typing import Any

from utils import Double_Keys, getch
from constants import ENCODING, DOUBLE_KEYS
from tools import np, Log_type, logger, settings_manager, change_logging_level

from entities import Player


class Globals:
    def __init__(self, in_game_loop:bool, in_fight:bool, exiting:bool, saving:bool):
        self.in_game_loop = bool(in_game_loop)
        self.in_fight = bool(in_fight)
        self.exiting = bool(exiting)
        self.saving = bool(saving)


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
            logger("Unknown key", "cannot decode key", Log_type.ERROR)
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


    def __init__(self, auto_save:bool|None=None, logging_level:int|None=None, keybinds:dict[str, list[list[bytes]]]|None=None,
                ask_package_check_fail:bool|None=None, ask_delete_save:bool|None=None, ask_regenerate_save:bool|None=None, def_backup_action:int|None=None):
        if auto_save is None:
            auto_save = self.get_auto_save()
        if logging_level is None:
            logging_level = self.get_logging_level()
        if keybinds is None:
            keybind_obj = self.get_keybins()
        else:
            keybind_obj = {}
            for key in keybinds:
                keybind_obj[key] = Key(keybinds[key])
        if ask_package_check_fail is None:
            ask_package_check_fail = self.get_ask_package_check_fail()
        if ask_delete_save is None:
            ask_delete_save = self.get_ask_delete_save()
        if ask_regenerate_save is None:
            ask_regenerate_save = self.get_ask_regenerate_save()
        if def_backup_action is None:
            def_backup_action = self.get_def_backup_action()
        self.auto_save = bool(auto_save)
        self.logging = (int(logging_level) != -1)
        self.logging_level = int(logging_level)
        self.keybinds = dict[str, Key](keybind_obj)
        self.ask_package_check_fail = bool(ask_package_check_fail)
        self.ask_delete_save = bool(ask_delete_save)
        self.ask_regenerate_save = bool(ask_regenerate_save)
        self.def_backup_action = int(def_backup_action)
        self.update_keybinds()
    

    def get_auto_save(self):
        """Returns the value of the `auto_save` from the setting file."""
        return bool(settings_manager("auto_save"))
    

    def get_logging_level(self):
        """Returns the value of the `logging_level` from the setting file."""
        return int(settings_manager("logging_level"))
    

    def get_keybins(self):
        """Returns the value of the `keybinds` from the setting file."""
        keybinds:dict[str, list[list[bytes]]] = settings_manager("keybinds")
        keybind_obj:dict[str, Key] = {}
        for key in keybinds:
            keybind_obj[key] = Key(keybinds[key])
        return keybind_obj
    
    
    def get_ask_package_check_fail(self):
        """Returns the value of the `ask_package_check_fail` from the setting file."""
        return bool(settings_manager("ask_package_check_fail"))
    
    
    def get_ask_delete_save(self):
        """Returns the value of the `ask_delete_save` from the setting file."""
        return bool(settings_manager("ask_delete_save"))
    
    
    def get_ask_regenerate_save(self):
        """Returns the value of the `ask_regenerate_save` from the setting file."""
        return bool(settings_manager("ask_regenerate_save"))
    
    
    def get_def_backup_action(self):
        """Returns the value of the `def_backup_action` from the setting file."""
        return int(settings_manager("def_backup_action"))


    def update_logging_level(self, logging_level:int):
        """Updates the value of the `logging_level` in the program and in the setting file."""
        self.logging = (int(logging_level) != -1)
        self.logging_level = int(logging_level)
        settings_manager("logging_level", self.logging_level)
        change_logging_level(self.logging_level)


    def update_auto_save(self, auto_save:bool):
        """Updates the value of the `auto_save` in the program and in the setting file."""
        self.auto_save = bool(auto_save)
        settings_manager("auto_save", self.auto_save)


    def _encode_keybinds(self):
        """Returns a json formated deepcopy of the `keybinds`."""
        return {"esc": deepcopy(self.keybinds["esc"].value),
        "up": deepcopy(self.keybinds["up"].value),
        "down": deepcopy(self.keybinds["down"].value),
        "left": deepcopy(self.keybinds["left"].value),
        "right": deepcopy(self.keybinds["right"].value),
        "enter": deepcopy(self.keybinds["enter"].value)}


    def update_keybinds(self):
        """Updates the value of the `keybind_mapping` in the program and in the setting file, with the `keybinds`."""
        # ([keybinds["esc"], keybinds["up"], keybinds["down"], keybinds["left"], keybinds["right"], keybinds["enter"]], [b"\xe0", b"\x00"])
        # ([[[b"\x1b"]],     [[], [b"H"]],   [[], [b"P"]],     [[], [b"K"]],     [[], [b"M"]],      [[b"\r"]]],         [b"\xe0", b"\x00"])
        self.keybind_mapping:tuple[list[list[list[bytes]]], list[bytes]] = ([
            self.keybinds["esc"].value,
            self.keybinds["up"].value,
            self.keybinds["down"].value,
            self.keybinds["left"].value,
            self.keybinds["right"].value,
            self.keybinds["enter"].value], self.DOUBLE_KEYS)
        settings_manager("keybinds", self._encode_keybinds())


    def check_keybind_conflicts(self):
        for key in self.keybinds:
            self.keybinds[key].conflict = False
        for key1 in self.keybinds:
            for key2 in self.keybinds:
                if key1 != key2:
                    if self.keybinds[key1].value == self.keybinds[key2].value:
                        self.keybinds[key1].conflict = True
                        self.keybinds[key2].conflict = True


    def update_ask_package_check_fail(self, ask_package_check_fail:bool):
        """Updates the value of `ask_package_check_fail` in the program and in the setting file."""
        self.ask_package_check_fail = bool(ask_package_check_fail)
        settings_manager("ask_package_check_fail", self.ask_package_check_fail)


    def update_ask_delete_save(self, ask_delete_save:bool):
        """Updates the value of `ask_delete_save` in the program and in the setting file."""
        self.ask_delete_save = bool(ask_delete_save)
        settings_manager("ask_delete_save", self.ask_delete_save)


    def update_ask_regenerate_save(self, ask_regenerate_save:bool):
        """Updates the value of `ask_regenerate_save` in the program and in the setting file."""
        self.ask_regenerate_save = bool(ask_regenerate_save)
        settings_manager("ask_regenerate_save", self.ask_regenerate_save)


    def update_def_backup_action(self, def_backup_action:int):
        """Updates the value of `def_backup_action` in the program and in the setting file."""
        self.def_backup_action = int(def_backup_action)
        settings_manager("def_backup_action", self.def_backup_action)


class Save_data:
    def __init__(self, save_name:str, display_save_name:str, last_access:list[int], player:Player,
                 main_seed:np.random.RandomState, world_seed:np.random.RandomState, tile_type_noise_seeds:dict[str, int],
                 world:Any|None=None):
        self.save_name = str(save_name)
        self.display_save_name = str(display_save_name)
        self.last_access = list[int](last_access)
        self.player = deepcopy(player)
        self.main_seed = main_seed
        self.world_seed = world_seed
        self.tile_type_noise_seeds = tile_type_noise_seeds
        
        from chunk_manager import World
        if world is not None:
            new_world:World = world
        else:
            new_world = World()
        self.world = new_world


def is_key(key:Key) -> bool:
    """
    Waits for a specific key.\n
    key should be a Key object.
    """

    key_in = getch()
    arrow = False
    if key_in in DOUBLE_KEYS:
        arrow = True
        key_in = getch()
    
    return ((not arrow and len(key.value) > 0 and key_in in key.value[0]) or
            (arrow and len(key.value) > 1 and key_in in key.value[1]))
