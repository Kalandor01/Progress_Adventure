from __future__ import annotations
from enum import Enum, auto
from inspect import stack
from typing import Any

from utils import vector_add, vector_multiply
from tools import main_seed, logger, Log_type

from inventory import Inventory, Base_items, Weapon_items, Armour_items, Material_items, Misc_items


class Rotation(Enum):
    NORTH = 0
    SOUTH = 1
    WEST = 2
    EAST = 3


class Attributes(Enum):
    RARE = auto()
    


def entity_master(base_hp:int|range, base_attack:int|range, base_defence:int|range, base_speed:int|range, fluc_small=2, fluc_big=3, c_rare=0.02, team=1, c_team_change=0.005, name:str|None=None):
    
    def configure_stat(stat_value:int|range):
        # int or range
        if isinstance(stat_value, int):
            stat_value = range(stat_value - fluc_small, stat_value + fluc_big)
        # fluctuation
        if stat_value.start == stat_value.stop:
            stat_value = stat_value.start
        else:
            stat_value = round(main_seed.triangular(stat_value.start, (stat_value.start + stat_value.stop) / 2, stat_value.stop))
        if stat_value < 0:
            stat_value = 0
        return int(stat_value)
    
    if name is None:
        frame_stack = stack()
        name = str(frame_stack[1][0].f_locals["self"].__class__.__name__)
    name = name.replace("_", " ")
    base_hp = configure_stat(base_hp)
    base_attack = configure_stat(base_attack)
    base_defence = configure_stat(base_defence)
    base_speed = configure_stat(base_speed)
    attributes:list[Attributes] = []
    if main_seed.random() < c_rare:
        attributes.append(Attributes.RARE)
    if base_hp <= 0:
        base_hp = 1
    # team
    switched = False
    if main_seed.random() < c_team_change:
        team = 0
        switched = True
    # write
    return (name, base_hp, base_attack, base_defence, base_speed, team, switched, attributes)


def _facing_to_movement_vector(facing:Rotation) -> tuple[int, int]:
    """
    Converts the `Rotation` enum into the equivalent vector.
    """
    move_vector = (0, 0)
    match facing:
        case Rotation.NORTH:
            move_vector = (0, 1)
        case Rotation.SOUTH:
            move_vector = (0, -1)
        case Rotation.WEST:
            move_vector = (-1, 0)
        case Rotation.EAST:
            move_vector = (1, 0)
    return move_vector


def _movement_vector_to_facing(vector:tuple[int, int]):
    """
    Converts the vector into the equivalent `Rotation` enum, if there is one.\n
    Otherwise returns `None`.
    """
    for rot in Rotation:
        if _facing_to_movement_vector(rot) == vector:
            return rot
    return None


class Loot_controller:
    def __init__(self, item:Base_items, chance=1.0, item_num:int|range=1, rolls=1):
        self.item = item
        self.chance = float(chance)
        if isinstance(item_num, int):
            item_num = range(item_num, item_num)
        self.item_num:range = item_num
        self.rolls = int(rolls)


def loot_manager(drops:list[Loot_controller]|None=None):
    """Converts a list of `Loot_manager`s into a list of `Item`s an their amounts."""
    loot:list[tuple[Base_items, int]] = []
    if drops is not None:
        for drop in drops:
            num = 0
            for _ in range(drop.rolls):
                num += (1 if main_seed.random() <= drop.chance else 0) * main_seed.randint(drop.item_num.start, drop.item_num.stop + 1)
            if num > 0:
                loot.append((drop.item, num))
    return loot


class Entity:
    def __init__(self, name:str, base_hp:int, base_attack:int, base_defence:int, base_speed:int, team:int=0, switched:bool=False, attributes:list[Attributes]|None=None, drops:list[tuple[Base_items, int]]|None=None):
        if attributes is None:
            attributes = []
        if drops is None:
            drops = []
        self.name = str(name)
        self.base_hp = int(base_hp)
        self.base_attack = int(base_attack)
        self.base_defence = int(base_defence)
        self.base_speed = int(base_speed)
        self.team = int(team)
        self.switched = bool(switched)
        self.attributes:list[Attributes] = attributes
        self.drops:list[tuple[Base_items, int]] = drops
        # adjust properties
        self._apply_attributes()
        self.full_name = ""
        self.update_full_name()


    def _apply_attributes(self):
        """Modifys the entity's stats acording to the entity's attributes."""
        self.hp = self.base_hp
        self.attack = self.base_attack
        self.defence = self.base_defence
        self.speed = self.base_speed
        if Attributes.RARE in self.attributes:
            self.hp *= 2
            self.attack *= 2
            self.defence *= 2
            self.speed *= 2


    def update_full_name(self):
        """Updates the full name of the entity."""
        full_name = self.name
        if Attributes.RARE in self.attributes:
            full_name = "Rare " + full_name
        self.full_name = full_name


    def to_json(self):
        """Returns a json representation of the `Entity`."""
        # drops
        drops_json:list[dict[str, Any]] = []
        for item in self.drops:
            drops_json.append({
                "type": item[0].name,
                "amount": item[1]
            })
        # attributes processing
        attributes_processed:list[str] = []
        for attribute in self.attributes:
            attributes_processed.append(attribute.name)
        # properties
        entity_json:dict[str, Any] = {
            "name": self.name,
            "base_hp": self.base_hp,
            "base_attack": self.base_attack,
            "base_defence": self.base_defence,
            "base_speed": self.base_speed,
            "team": self.team,
            "switched": self.switched,
            "attributes": attributes_processed,
            "drops": drops_json
        }
        return entity_json


    def __str__(self):
        return f'Name: {self.name}\nFull name: {self.full_name}\nHp: {self.hp}\nAttack: {self.attack}\nDefence: {self.defence}\nSpeed: {self.speed}\nAttributes: {self.attributes}\nTeam: {"Player" if self.team==0 else self.team}\nSwitched sides: {self.switched}\nDrops: {self.drops}'


    def attack_entity(self, target:Entity):
        target.hp -= self.attack


class Player(Entity):
    def __init__(self, name="", base_hp:int|None=None, base_attack:int|None=None, base_defence:int|None=None, base_speed:int|None=None, inventory:Inventory|None=None, position:tuple[int, int]|None=None, rotation:Rotation|None=None):
        """
        If any argument other than `name`, `inventory`, `position` or `rotation` is `None`, it will treat it as a new player, and generate new stats.
        """
        if name == "":
            name = "You"
        if base_hp is None or base_attack is None or base_defence is None or base_speed is None:
            super().__init__(*entity_master(range(14, 26), range(7, 13), range(7, 13), range(1, 20), 0, 0, 0, 0, 0, name))
        else:
            super().__init__(name, base_hp, base_attack, base_defence, base_speed)
        if inventory is None:
            inventory = Inventory()
        if position is None:
            position = (0, 0)
        if rotation is None:
            rotation = Rotation.NORTH
        self.inventory = inventory
        self.pos:tuple[int, int] = (int(position[0]), int(position[1]))
        self.rotation:Rotation = rotation
        self.update_full_name()


    def weighted_turn(self):
        """Turns the player in a random direction, that is weighted in the direction that it's already going towards."""
        # turn
        if main_seed.rand() > 0.75:
            old_rot = self.rotation
            move_vec = _facing_to_movement_vector(self.rotation)
            # back
            if main_seed.rand() > 0.75:
                new_dir = _movement_vector_to_facing(vector_multiply(move_vec, (-1, -1), True))
            else:
                new_dir = _movement_vector_to_facing((move_vec[1], move_vec[0]))
                new_dir = _movement_vector_to_facing((move_vec[1], move_vec[0]))
            
            if new_dir is not None:
                self.rotation = new_dir
                logger("Player turned", f"{old_rot} -> {self.rotation}", Log_type.DEBUG)


    def move(self, amount:tuple[int, int]|None=None, direction:Rotation|None=None):
        """
        Moves the player in the direction it's facing.\n
        If `direction` is specified, it will move in that direction instead.\n
        the amount the player is moved in the x and y direction is specified by the `amount` tuple.
        """
        old_pos = self.pos
        if direction is None:
            direction = self.rotation
        if amount is None:
            amount = (1, 1)
        move_raw = _facing_to_movement_vector(direction)
        move = vector_multiply(move_raw, amount)
        self.pos = vector_add(self.pos, move, True)
        logger("Player moved", f"{old_pos} -> {self.pos}", Log_type.DEBUG)


    def to_json(self):
        """Returns a json representation of the `Entity`."""
        player_json = super().to_json()
        player_json["x_pos"] = self.pos[0]
        player_json["y_pos"] = self.pos[1]
        player_json["rotation"] = self.rotation.value
        player_json["inventory"] = self.inventory.to_json()
        return player_json


    def __str__(self):
        return f"{super().__str__()}\n{self.inventory}\nPosition: {self.pos}\nRotation: {self.rotation}"


class Caveman(Entity):
    def __init__(self):
        super().__init__(*entity_master(7, 7, 7, 7), loot_manager(
            [Loot_controller(Weapon_items.WOODEN_CLUB, 0.3),
            Loot_controller(Material_items.CLOTH, 0.15, range(0, 1), 3),
            Loot_controller(Misc_items.COPPER_COIN, 0.35, range(0, 4), 3)]))


class Ghoul(Entity):
    def __init__(self):
        super().__init__(*entity_master(11, 9, 9, 9), loot_manager(
            [Loot_controller(Weapon_items.STONE_SWORD, 0.2),
            Loot_controller(Misc_items.ROTTEN_FLESH, 0.55, range(0, 3)),
            Loot_controller(Misc_items.COPPER_COIN, 0.40, range(0, 5), 4)]))


class Troll(Entity):
    def __init__(self):
        super().__init__(*entity_master(13, 11, 11, 5), loot_manager(
            [Loot_controller(Weapon_items.CLUB_WITH_TEETH, 0.25),
            Loot_controller(Material_items.CLOTH, 0.25, range(1, 3), 2),
            Loot_controller(Material_items.TEETH, 0.35, range(1, 5), 2),
            Loot_controller(Misc_items.SILVER_COIN, 0.30, range(1, 3), 3)]))
