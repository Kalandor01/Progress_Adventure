from enum import Enum, auto

from tools import logger


class Weapon_items(Enum):
    WOODEN_SWORD = auto()
    STONE_SWORD = auto()
    STEEL_SWORD = auto()
    WOODEN_BOW = auto()
    STEEL_ARROW = auto()
    WOODEN_CLUB = auto()
    CLUB_WITH_TEETH = auto()

class Armour_items(Enum):
    WOODEN_SHIELD = auto()
    LEATHER_CAP = auto()
    LEATHER_TUNIC = auto()
    LEATHER_PANTS = auto()
    LEATHER_BOOTS = auto()

class Material_items(Enum):
    BOTTLE = auto()
    WOOL = auto()
    CLOTH = auto()
    WOOD = auto()
    STONE = auto()
    STEEL = auto()
    GOLD = auto()
    TEETH = auto()

class Misc_items(Enum):
    HEALTH_POTION = auto()
    GOLD_COIN = auto()
    SILVER_COIN = auto()
    COPPER_COIN = auto()
    ROTTEN_FLESH = auto()

class Item_categories(Enum):
    WEAPONS = Weapon_items
    ARMOUR = Armour_items
    MATERIALS = Material_items
    MISC = Misc_items


class Item:
    def __init__(self, name:Item_categories, amount=1):
        self.name = name
        self.amount = amount
        self.make_item()
    
    def make_item(self):
        match(self.name):
            case Weapon_items.CLUB_WITH_TEETH:
                self.d_name = "Club with teeth"
            case _:
                self.d_name = self.name.name.lower().capitalize().replace("_", " ")

    def use(self):
        return False


class Inventory:
    def __init__(self):
        self.items:list[Item] = []
    

    def add(self, name:Item_categories, amount=1):
        for item in self.items:
            if item.name == name:
                item.amount += amount
                return None
        self.items.append(Item(name, amount))
    

    def remove(self, name:Item_categories, amount=1):
        for item in self.items:
            if item.name == name:
                if item.amount >= amount:
                    item.amount -= amount
                    return True
                break
        return False


    def loot(self, loot:list):
        for item in loot:
            self.add(item[0], item[1])


    def use(self, name:Item_categories):
        for x in range(len(self.items)):
            if self.items[x].name == name:
                if self.items[x].use():
                    self.items[x].amount -= 1
                    if self.items[x].amount <= 0:
                        self.items.pop(x)
                break
    
    
    def to_json(self):
        """Convert the items in the inventory into a list for a json format."""

        items_json = []
        for item in self.items:
            items_json.append([item.name.name, item.amount])
        return items_json
    

    def __str__(self):
        txt = "Inventory:"
        for item in self.items:
            txt += f"\n\t{item.d_name}{' x' + str(item.amount) if item.amount > 1 else ''}"
        return txt
    

def item_finder(name:str) -> Item_categories|None:
    """
    Gives back the item, from the item's enum name.\n
    Returns `None` if it doesn't exist.
    """
    for enum in Item_categories._value2member_map_:
        try: return enum._member_map_[name]
        except KeyError: pass
    logger("Unknown item type", f"item type: {name}", ts.Log_type.WARN)
    return None