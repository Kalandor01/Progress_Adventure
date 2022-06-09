from __future__ import annotations
import inspect
import copy

import random_sentance as rs

import tools as ts

from tools import ENCODING, DOUBLE_KEYS, r


class Globals:
    def __init__(self, in_game_loop:bool, in_fight:bool):
        self.in_game_loop = bool(in_game_loop)
        self.in_fight = bool(in_fight)


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

    def __init__(self, auto_save:bool, keybinds:dict[list]):
        self.auto_save = auto_save
        for x in keybinds:
            keybinds[x] = Key(keybinds[x])
        self.keybinds = dict[Key](keybinds)
        self.keybind_mapping = []
        self.save_keybind_mapping()
    
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
        self.keybind_mapping:list[list[list[bytes|int]]|list[bytes]] = [[self.keybinds["esc"].value,
        self.keybinds["up"].value,
        self.keybinds["down"].value,
        self.keybinds["left"].value,
        self.keybinds["right"].value,
        self.keybinds["enter"].value], self.DOUBLE_KEYS]
        ts.settings_manager("keybinds", self.encode_keybinds())


class Save_data:
    def __init__(self, save_num:int, last_access:list[int], player:Player, seed:tuple):
        self.save_num = int(save_num)
        self.last_access = list[int](last_access)
        self.player = copy.deepcopy(player)
        self.seed = tuple(seed)


def entity_master(life:int|range, attack:int|range, deff:int|range, speed:int|range, fluc_small=2, fluc_big=3, c_rare=0.05, team=1, c_team_change=0.005, name:str=None):
    
    def configure_stat(stat_value:int|range):
        # int or range
        if type(stat_value) == int:
            stat_value = range(stat_value - fluc_small, stat_value + fluc_big)
        # fluctuation
        if stat_value.start == stat_value.stop:
            stat_value = stat_value.start
        else:
            stat_value = round(r.triangular(stat_value.start, (stat_value.start + stat_value.stop) / 2, stat_value.stop))
        if stat_value < 0:
            stat_value = 0
        return int(stat_value)
    
    if name == None:
        stack = inspect.stack()
        name = stack[1][0].f_locals["self"].__class__.__name__
    name = name.replace("_", " ")
    life = configure_stat(life)
    attack = configure_stat(attack)
    deff = configure_stat(deff)
    speed = configure_stat(speed)
    # rare
    rare = False
    if r.random() < c_rare:
        rare = True
        name = "Rare " + name
        life *= 2
        attack *= 2
        deff *= 2
        speed *= 2
    if life == 0:
        life = 1
    # team
    switched = False
    if r.random() < c_team_change:
        team = 0
        switched = True
    # write
    return [name, life, attack, deff, speed, rare, team, switched]


class Entity:
    def __init__(self, traits:list=None):
        if traits == None:
            traits = entity_master(1, 1, 1, 1, name="test")
        self.name = str(traits[0])
        self.hp = int(traits[1])
        self.attack = int(traits[2])
        self.defence = int(traits[3])
        self.speed = int(traits[4])
        self.rare = bool(traits[5])
        self.team = int(traits[6])
        self.switched = bool(traits[7])
    
    def __str__(self):
        return f'Name: {self.name}\nHp: {self.hp}\nAttack: {self.attack}\nDefence: {self.defence}\nSpeed: {self.speed}\nRare: {self.rare}\nTeam: {"Player" if self.team==0 else self.team}\nSwitched sides: {self.switched}'


    def attack_entity(self, target:Entity):
        target.hp -= self.attack


class Player(Entity):
    def __init__(self, name=""):
        if name == "":
            name = "You"
        super().__init__(entity_master(range(14, 26), range(7, 13), range(7, 13), range(1, 20), 0, 0, 0, 0, 0, name))
        # self.name = "You"
        # self.hp = r.randint(1, 7) + r.randint(1, 7) + 12
        # self.attack = r.randint(1, 7) + 6
        # self.defence = r.randint(1, 7) + 6
        # self.speed = round(r.random() * 100 / 5, 1)
        # self.rare = False
        # self.team = 0
        # self.switched = False


class Caveman(Entity):
    def __init__(self):
        super().__init__(entity_master(7, 7, 7, 7))


class Ghoul(Entity):
    def __init__(self):
        super().__init__(entity_master(11, 9, 9, 9))


class Troll(Entity):
    def __init__(self):
        super().__init__(entity_master(13, 11, 11, 5))


class Test(Entity):
    def __init__(self):
        super().__init__()
