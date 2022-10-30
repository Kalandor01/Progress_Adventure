import copy

from utils import Double_Keys
import tools as ts
from tools import getch
from tools import ENCODING, DOUBLE_KEYS

from entities import Player
from chunk_manager import Chunk


class Globals:
    def __init__(self, in_game_loop:bool, in_fight:bool, exiting:bool, saving:bool):
        self.in_game_loop = bool(in_game_loop)
        self.in_fight = bool(in_fight)
        self.exiting = bool(exiting)
        self.saving = bool(saving)


class Key:
    def __init__(self, value:list[list[bytes]]):
        self.value = value
        self.set_name()
    
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
        elif len(self.value) > 1 and len(self.value[1]) > 0:
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
        else:
            self.name = "key error"

    def change(self, key_value:list[list[bytes]]):
        self.value = key_value
        self.set_name()
        print(self.name, self.value)
    
    def __str__(self):
        return f"{self.name}: {self.value}"


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
        if auto_save is not None:
            self.auto_save = bool(auto_save)
            ts.settings_manager("auto_save", self.auto_save)
        # logging
        if auto_save is not None:
            self.logging = bool(logging)
            ts.settings_manager("logging", self.logging)
            ts.change_logging(self.logging)
    
    def encode_keybinds(self):
        return {"esc": copy.deepcopy(self.keybinds["esc"].value),
        "up": copy.deepcopy(self.keybinds["up"].value),
        "down": copy.deepcopy(self.keybinds["down"].value),
        "left": copy.deepcopy(self.keybinds["left"].value),
        "right": copy.deepcopy(self.keybinds["right"].value),
        "enter": copy.deepcopy(self.keybinds["enter"].value)}
    
    def save_keybind_mapping(self):
        # [[keybinds["esc"], keybinds["up"], keybinds["down"], keybinds["left"], keybinds["right"], keybinds["enter"]], [b"\xe0", b"\x00"]]
        # [[[[b"\x1b"]],     [[], [b"H"]],   [[], [b"P"]],     [[], [b"K"]],     [[], [b"M"]],      [[b"\r"]]],         [b"\xe0", b"\x00"]]
        self.keybind_mapping:list[list[list[list[bytes]]|bytes]] = [[
            self.keybinds["esc"].value,
            self.keybinds["up"].value,
            self.keybinds["down"].value,
            self.keybinds["left"].value,
            self.keybinds["right"].value,
            self.keybinds["enter"].value], self.DOUBLE_KEYS]
        ts.settings_manager("keybinds", self.encode_keybinds())

class Save_data:
    def __init__(self, save_name:str, display_save_name:str, last_access:list[int], player:Player, seed:tuple, chunks:list[Chunk]=None):
        self.save_name = str(save_name)
        self.display_save_name = str(display_save_name)
        self.last_access = list[int](last_access)
        self.player = copy.deepcopy(player)
        self.seed = tuple(seed)
        self.chunks:list[Chunk] = []
        if chunks is not None:
            for chunk in chunks:
                self.chunks.append(copy.deepcopy(chunk))


def press_key(text=""):
    """
    Writes out text, and then stalls until the user presses any key.
    """

    print(text, end="", flush=True)
    if getch() in DOUBLE_KEYS:
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
    
    return ((not arrow and len(key.value) > 0 and key_in in key.value[0]) or
            (arrow and len(key.value) > 1 and key_in in key.value[1]))