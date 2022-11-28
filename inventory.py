import copy
from enum import Enum, auto


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
    

class Container:
    def __init__(self):
        self.items:list[Item] = []
    
    
    def find_item(self, name:Item_categories):
        for item in self.items:
            if item.name == name:
                return x
        return False
        

    def add(self, name:Item_categories, amount=1):
        item_num = self.find_item(name)
        if item_num != False:
            self.items[item_num].amount += amount
            return None
        else:
            self.items.append(Item(name, amount))
    

    def remove(self, name:Item_categories, amount=1):
        for item in self.items:
            if item.name == name:
                if item.amount >= amount:
                    item.amount -= amount
                    return True
                break
        return False


    def get_loot(self):
        items = copy.deepcopy(self.items)
        self.items.clear()
        return items
    

    def __str__(self):
        txt = f"{self.__class__.__name__}:"
        for item in self.items:
            txt += f"\n\t{item.d_name}{' x' + str(item.amount) if item.amount > 1 else ''}"
        return txt


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
    

    def __str__(self):
        txt = "Inventory:"
        for item in self.items:
            txt += f"\n\t{item.d_name}{' x' + str(item.amount) if item.amount > 1 else ''}"
        return txt
    

def item_finder(name:str) -> Enum|None:
    """
    Gives back the item enum, from the item name.\n
    Returns `None` if it doesn't exist.
    """

    for enum in Item_categories._value2member_map_:
        try: return enum._member_map_[name]
        except KeyError: pass

def inventory_converter(inventory:list):
    """
    Can convert between the json and object versions of the inventory items list.
    """

    items = []
    for item in inventory:
        if type(item) is list:
            items.append(Item(item_finder(item[0]), item[1]))
        else:
            item:Item
            items.append([item.name.name, item.amount])
    return items