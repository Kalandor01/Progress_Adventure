from __future__ import annotations
import inspect

from tools import r

from inventory import Inventory, Item_categories


def entity_master(life:int|range, attack:int|range, deff:int|range, speed:int|range, fluc_small=2, fluc_big=3, c_rare=0.02, team=1, c_team_change=0.005, name:str=None):
    
    def configure_stat(stat_value:int|range):
        # int or range
        if type(stat_value) is int:
            stat_value = range(stat_value - fluc_small, stat_value + fluc_big)
        # fluctuation
        if stat_value.start == stat_value.stop:
            stat_value = stat_value.start
        else:
            stat_value = round(r.triangular(stat_value.start, (stat_value.start + stat_value.stop) / 2, stat_value.stop))
        if stat_value < 0:
            stat_value = 0
        return int(stat_value)
    
    if name is None:
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


class Loot_controller:
    def __init__(self, item:Item_categories, chance=1.0, item_num:int|range=1, rolls=1):
        self.item = item
        self.chance = float(chance)
        if type(item_num) is int:
            item_num = range(item_num, item_num)
        self.item_num = item_num
        self.rolls = int(rolls)

def loot_manager(drops:list[Loot_controller]=None):
    loot = []
    for drop in drops:
        num = 0
        for _ in range(drop.rolls):
            num += (1 if r.random() <= drop.chance else 0) * r.randint(drop.item_num.start, drop.item_num.stop + 1)
        if num > 0:
            loot.append([drop.item, num])
    return loot


class Entity:
    def __init__(self, traits:list=None, drops:list=None):
        if traits is None:
            traits = entity_master(1, 1, 1, 1, name="test")
        if drops is None:
            drops = []
        self.name = str(traits[0])
        self.hp = int(traits[1])
        self.attack = int(traits[2])
        self.defence = int(traits[3])
        self.speed = int(traits[4])
        self.rare = bool(traits[5])
        self.team = int(traits[6])
        self.switched = bool(traits[7])
        self.drops = drops
    
    def __str__(self):
        return f'Name: {self.name}\nHp: {self.hp}\nAttack: {self.attack}\nDefence: {self.defence}\nSpeed: {self.speed}\nRare: {self.rare}\nTeam: {"Player" if self.team==0 else self.team}\nSwitched sides: {self.switched}'


    def attack_entity(self, target:Entity):
        target.hp -= self.attack


class Player(Entity):
    def __init__(self, name=""):
        if name == "":
            name = "You"
        super().__init__(entity_master(range(14, 26), range(7, 13), range(7, 13), range(1, 20), 0, 0, 0, 0, 0, name))
        self.inventory = Inventory()
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
        super().__init__(entity_master(7, 7, 7, 7), loot_manager(
            [Loot_controller(Item_categories.WEAPONS.value.WOODEN_CLUB, 0.3),
            Loot_controller(Item_categories.MATERIALS.value.CLOTH, 0.15, range(0, 1), 3),
            Loot_controller(Item_categories.MISC.value.COPPER_COIN, 0.35, range(0, 4), 3)]))


class Ghoul(Entity):
    def __init__(self):
        super().__init__(entity_master(11, 9, 9, 9), loot_manager(
            [Loot_controller(Item_categories.WEAPONS.value.STONE_SWORD, 0.2),
            Loot_controller(Item_categories.MISC.value.ROTTEN_FLESH, 0.55, range(0, 3)),
            Loot_controller(Item_categories.MISC.value.COPPER_COIN, 0.40, range(0, 5), 4)]))


class Troll(Entity):
    def __init__(self):
        super().__init__(entity_master(13, 11, 11, 5), loot_manager(
            [Loot_controller(Item_categories.WEAPONS.value.CLUB_WITH_TEETH, 0.25),
            Loot_controller(Item_categories.MATERIALS.value.CLOTH, 0.25, range(1, 3), 2),
            Loot_controller(Item_categories.MATERIALS.value.TEETH, 0.35, range(1, 5), 2),
            Loot_controller(Item_categories.MISC.value.SILVER_COIN, 0.30, range(1, 3), 3)]))


class Test(Entity):
    def __init__(self):
        super().__init__()
