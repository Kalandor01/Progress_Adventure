from __future__ import annotations
from tools import r
import tools as ts

import random_sentance as rs

ENCODING = "windows-1250"

class Key:
    def __init__(self, value:list):
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
    
    def change(self, key):
        self.value = key
        self.set_name()

class Settings:

    def __init__(self, auto_save:bool, keybinds):
        self.auto_save = auto_save
        for x in keybinds:
            keybinds[x] = Key(keybinds[x])
        self.keybinds = keybinds
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
        self.keybind_mapping = [[self.keybinds["esc"].value,
        self.keybinds["up"].value,
        self.keybinds["down"].value,
        self.keybinds["left"].value,
        self.keybinds["right"].value,
        self.keybinds["enter"].value], [b"\xe0", b"\x00"]]
        ts.settings_manager("keybinds", self.encode_keybinds())


class Save_data:
    def __init__(self, last_access:list, player:Player, seed):
        self.last_access = last_access
        self.player = player
        self.seed = seed


def entity_master(name:str, life:int|range, attack:int|range, deff:int|range, speed:int|range, fluc_small=2, fluc_big=3, c_rare=0.05, team=1, c_team_change=0.005):
    
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
        return stat_value
    
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
    # team
    switched = False
    if r.random() < c_team_change:
        team = 0
        switched = True
    # write
    return [name, life, attack, deff, speed, rare, team, switched]


class Entity:
    def __init__ (self, traits=entity_master("test", 1, 1, 1, 1)):
        self.name = traits[0]
        self.hp = traits[1]
        self.attack = traits[2]
        self.defence = traits[3]
        self.speed = traits[4]
        self.rare = traits[5]
        self.team = traits[6]
        self.switched = traits[7]
    
    def __str__(self):
        return f'Name: {self.name}\nHp: {self.hp}\nAttack: {self.attack}\nDefence: {self.defence}\nSpeed: {self.speed}\nRare: {self.rare}\nTeam: {"Player" if self.team==0 else self.team}\nSwitched sides: {self.switched}'


    def attack_entity(self, target:Entity):
        target.hp -= self.attack


class Player(Entity):
    def __init__(self, name=""):
        if name == "":
            name = "You"
        super().__init__(entity_master(name, range(14, 26), range(7, 13), range(7, 13), range(1, 20), 0, 0, 0, 0, 0))
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
        super().__init__(entity_master(__class__.__name__, 7, 7, 7, 7))


class Ghoul(Entity):
    def __init__(self):
        super().__init__(entity_master(__class__.__name__, 11, 9, 9, 9))


class Troll(Entity):
    def __init__(self):
        super().__init__(entity_master(__class__.__name__, 13, 11, 11, 5))


class Test(Entity):
    def __init__(self):
        super().__init__()
