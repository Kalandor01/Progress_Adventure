import copy

import tools as ts
from tools import getch
from tools import ENCODING, DOUBLE_KEYS

from entities import Player


class Globals:
    def __init__(self, in_game_loop:bool, in_fight:bool, exiting:bool):
        self.in_game_loop = bool(in_game_loop)
        self.in_fight = bool(in_fight)
        self.exiting = bool(exiting)


class Key:
    def __init__(self, value:list[bytes, int]):
        self.value = value
        self.name = self.value[0].decode(ENCODING)
        self.set_name()
    
    def set_name(self):
        match self.value:
            case [(b"H"|b"P"|b"K"|b"M"), 1]:
                match self.value[0]:
                    case b"H":
                        self.name = "up"
                    case b"P":
                        self.name = "down"
                    case b"K":
                        self.name = "left"
                    case b"M":
                        self.name = "right"
                self.name += " arrow"
            case _:
                match self.value[0]:
                    case b"\r":
                        self.name = "enter"
                    case b"\x1b":
                        self.name = "escape"
                    case _:
                        self.name = self.value[0].decode(ENCODING)
    
    def change(self, key:list):
        self.value = key
        self.set_name()


class Settings:

    DOUBLE_KEYS = DOUBLE_KEYS

    def __init__(self, auto_save:bool, logging:bool, keybinds:dict[list]):
        self.auto_save = auto_save
        self.logging = logging
        for key in keybinds:
            keybinds[key] = Key(keybinds[key])
        self.keybinds = dict[Key](keybinds)
        self.keybind_mapping = []
        self.save_keybind_mapping()
    
    def change_others(self, auto_save=None, logging=None):
        # auto save
        if auto_save != None:
            self.auto_save = bool(auto_save)
            ts.settings_manager("auto_save", self.auto_save)
        # logging
        if auto_save != None:
            self.logging = bool(logging)
            ts.settings_manager("logging", self.logging)
            ts.change_logging(self.logging)
    
    def encode_keybinds(self):
        return {"esc": self.keybinds["esc"].value.copy(),
        "up": self.keybinds["up"].value.copy(),
        "down": self.keybinds["down"].value.copy(),
        "left": self.keybinds["left"].value.copy(),
        "right": self.keybinds["right"].value.copy(),
        "enter": self.keybinds["enter"].value.copy()}
    
    def save_keybind_mapping(self):
        # [[keybinds["esc"], keybinds["up"], keybinds["down"], keybinds["left"], keybinds["right"], keybinds["enter"]], [b"\xe0", b"\x00"]]
        # [[[b"\x1b"], [b"H", 1], [b"P", 1], [b"K", 1], [b"M", 1], [b"\r"]], [b"\xe0", b"\x00"]]
        self.keybind_mapping:list[list[list[bytes|int]]|list[bytes]] = [[
            self.keybinds["esc"].value,
            self.keybinds["up"].value,
            self.keybinds["down"].value,
            self.keybinds["left"].value,
            self.keybinds["right"].value,
            self.keybinds["enter"].value], self.DOUBLE_KEYS]
        ts.settings_manager("keybinds", self.encode_keybinds())


class Save_data:
    def __init__(self, save_name:str, display_save_name:str, last_access:list[int], player:Player, seed:tuple):
        self.save_name = str(save_name)
        self.display_save_name = str(display_save_name)
        self.last_access = list[int](last_access)
        self.player = copy.deepcopy(player)
        self.seed = tuple(seed)


def press_key(text=""):
    """
    Writes out text, and then stalls until the user presses any key.
    """

    print(text, end="", flush=True)
    if DOUBLE_KEYS.count(getch()):
        getch()
    print()


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
    return ((len(key.value) == 1 and not arrow) or (len(key.value) > 1 and arrow)) and key_in == key.value[0]