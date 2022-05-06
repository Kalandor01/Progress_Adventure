from __future__ import annotations
from tools import r

import random_sentance as rs


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
