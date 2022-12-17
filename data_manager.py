from copy import deepcopy
from typing import Any

from utils import Double_Keys
from constants import ENCODING, DOUBLE_KEYS
from tools import Log_type, getch, logger, settings_manager, change_logging_level

from entities import Player
from chunk_manager import World


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


    def __init__(self, auto_save:bool, logging_level:int, keybinds:dict[str, list[list[bytes]]]):
        self.auto_save = bool(auto_save)
        self.logging = (int(logging_level) != -1)
        self.logging_level = int(logging_level)
        obj_kebinds = {}
        for key in keybinds:
            obj_kebinds[key] = Key(keybinds[key])
        self.keybinds = dict[str, Key](obj_kebinds)
        self.save_keybind_mapping()


    def change_others(self, auto_save:bool=None, logging_level:int=None):
        # auto save
        if auto_save is not None:
            self.auto_save = bool(auto_save)
            settings_manager("auto_save", self.auto_save)
        # logging
        if logging_level is not None:
            self.logging = (int(logging_level) != -1)
            self.logging_level = int(logging_level)
            settings_manager("logging_level", self.logging_level)
            change_logging_level(self.logging_level)


    def encode_keybinds(self):
        return {"esc": deepcopy(self.keybinds["esc"].value),
        "up": deepcopy(self.keybinds["up"].value),
        "down": deepcopy(self.keybinds["down"].value),
        "left": deepcopy(self.keybinds["left"].value),
        "right": deepcopy(self.keybinds["right"].value),
        "enter": deepcopy(self.keybinds["enter"].value)}


    def save_keybind_mapping(self):
        # ([keybinds["esc"], keybinds["up"], keybinds["down"], keybinds["left"], keybinds["right"], keybinds["enter"]], [b"\xe0", b"\x00"])
        # ([[[b"\x1b"]],     [[], [b"H"]],   [[], [b"P"]],     [[], [b"K"]],     [[], [b"M"]],      [[b"\r"]]],         [b"\xe0", b"\x00"])
        self.keybind_mapping:tuple[list[list[list[bytes]]], list[bytes]] = ([
            self.keybinds["esc"].value,
            self.keybinds["up"].value,
            self.keybinds["down"].value,
            self.keybinds["left"].value,
            self.keybinds["right"].value,
            self.keybinds["enter"].value], self.DOUBLE_KEYS)
        settings_manager("keybinds", self.encode_keybinds())


    def check_keybind_conflicts(self):
        for key in self.keybinds:
            self.keybinds[key].conflict = False
        for key1 in self.keybinds:
            for key2 in self.keybinds:
                if key1 != key2:
                    if self.keybinds[key1].value == self.keybinds[key2].value:
                        self.keybinds[key1].conflict = True
                        self.keybinds[key2].conflict = True

class Save_data:
    def __init__(self, save_name:str, display_save_name:str, last_access:list[int], player:Player, seed:tuple[Any]|dict[str, Any], world:World=None):
        self.save_name = str(save_name)
        self.display_save_name = str(display_save_name)
        self.last_access = list[int](last_access)
        self.player = deepcopy(player)
        self.seed = tuple(seed)
        if world is None:
            world = World()
        self.world = world


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