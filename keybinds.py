from enum import Enum

from save_file_manager import Keybinds, Key_action, Get_key_modes, Keys

from utils import Double_keys, Normal_keys
from constants import DOUBLE_KEYS


class Action_types(Enum):
    ESCAPE  = "esc"
    UP      = "up"
    DOWN    = "down"
    LEFT    = "left"
    RIGHT   = "right"
    ENTER   = "enter"

action_type_ignore_mapping:dict[Action_types, list[Get_key_modes]|tuple[list[Get_key_modes], list[Get_key_modes]]] = {
    Action_types.ESCAPE:    [Get_key_modes.IGNORE_ESCAPE],
    Action_types.UP:        [Get_key_modes.IGNORE_VERTICAL],
    Action_types.DOWN:      [Get_key_modes.IGNORE_VERTICAL],
    Action_types.LEFT:      [Get_key_modes.IGNORE_HORIZONTAL],
    Action_types.RIGHT:     [Get_key_modes.IGNORE_HORIZONTAL],
    Action_types.ENTER:     [Get_key_modes.IGNORE_ENTER]
}

action_type_response_mapping:dict[Action_types, Keys] = {
    Action_types.ESCAPE:    Keys.ESCAPE,
    Action_types.UP:        Keys.UP,
    Action_types.DOWN:      Keys.DOWN,
    Action_types.LEFT:      Keys.LEFT,
    Action_types.RIGHT:     Keys.RIGHT,
    Action_types.ENTER:     Keys.ENTER
}


_special_normal_key_name_map:dict[str, str] = {
    Normal_keys.ENTER.value: "enter",
    Normal_keys.ESCAPE.value: "escape",
    Normal_keys.SPACE.value: "space"
}


_special_arrow_key_name_map:dict[str, str] = {
    Double_keys.ARROW_UP.value: "up arrow",
    Double_keys.ARROW_DOWN.value: "down arrow",
    Double_keys.ARROW_LEFT.value: "left arrow",
    Double_keys.ARROW_RIGHT.value: "right arrow",
    Double_keys.NUM_0.value: "insert",
    Double_keys.NUM_1.value: "end",
    Double_keys.NUM_3.value: "page down",
    Double_keys.NUM_7.value: "home",
    Double_keys.NUM_9.value: "page up",
    Double_keys.DELETE.value: "delete"
}


class Action_key(Key_action):
    def __init__(self, action_type:Action_types, normal_keys:list[str]|None=None, arrow_keys:list[str]|None=None):
        self.action_type = action_type
        response = action_type_response_mapping[self.action_type]
        ignore_modes = action_type_ignore_mapping[self.action_type]
        super().__init__(response, normal_keys, arrow_keys, ignore_modes)
        self.set_keys(self.normal_keys, self.arrow_keys)
        self.conflict = False


    def set_name(self):
        if len(self.normal_keys) > 0:
            if self.normal_keys[0] in _special_normal_key_name_map.keys():
                self.name = _special_normal_key_name_map[self.normal_keys[0]]
            else:
                if self.normal_keys[0] == "":
                    self.name = "special key"
                else:
                    self.name = self.normal_keys[0]
        else:
            if self.arrow_keys[0] in _special_arrow_key_name_map.keys():
                self.name = _special_arrow_key_name_map[self.arrow_keys[0]]
            else:
                if self.arrow_keys[0] == "":
                    self.name = "special key"
                else:
                    self.name = self.arrow_keys[0]


    def set_keys(self, normal_keys:list[str], arrow_keys:list[str]):
        if len(normal_keys) == 0 and len(arrow_keys) == 0:
            raise KeyError
        self.normal_keys = normal_keys
        self.arrow_keys = arrow_keys
        self.set_name()


    def __str__(self):
        return f"{self.name}: {self.normal_keys}, {self.arrow_keys}"


class Action_keybinds(Keybinds):
    def __init__(self, actions:list[Action_key]):
        super().__init__(actions, DOUBLE_KEYS)
        self._actions:list[Action_key]
    
    
    def get_action_key(self, action_type:Action_types):
        """
        Returns the `Action_key` by type.
        """
        for key in self._actions:
            if key.action_type == action_type:
                return key
        from tools import logger, Log_type
        logger("Unknown Action_type", "trying to create placeholder key", Log_type.ERROR)
        return Action_key(action_type.ESCAPE, [Normal_keys.ESCAPE.value])
    
    
    def to_json(self):
        """Turns the `Action_keybinds` objest into a json object for the settings file."""
        keybinds_json:dict[str, list[list[str]]] = {}
        for action in self._actions:
            keybinds_json[action.action_type.value] = [action.normal_keys, action.arrow_keys]
        return keybinds_json


def get_def_keybinds():
    return Action_keybinds([
            Action_key(Action_types.ESCAPE, [Normal_keys.ESCAPE.value], []),
            Action_key(Action_types.UP,     [],                         [Double_keys.ARROW_UP.value]),
            Action_key(Action_types.DOWN,   [],                         [Double_keys.ARROW_DOWN.value]),
            Action_key(Action_types.LEFT,   [],                         [Double_keys.ARROW_LEFT.value]),
            Action_key(Action_types.RIGHT,  [],                         [Double_keys.ARROW_RIGHT.value]),
            Action_key(Action_types.ENTER,  [Normal_keys.ENTER.value],  [])
        ])


def keybinds_from_json(keybinds_json:dict[str, list[list[str]]]):
    """Turns the settings part of the settings file into an `Action_keybinds` objest."""
    actions = []
    for action_type_str in keybinds_json:
        if action_type_str in Action_types._value2member_map_.keys():
            action_type:Action_types = Action_types._value2member_map_[action_type_str]
            key_list = keybinds_json[action_type_str]
            # normal keys
            if len(key_list) > 0 and len(key_list[0]) > 0:
                normal_keys = key_list[0]
            else:
                normal_keys = []
            # arrow keys
            if len(key_list) > 1 and len(key_list[1]) > 0:
                arrow_keys = key_list[1]
            else:
                arrow_keys = []
            actions.append(Action_key(action_type, normal_keys, arrow_keys))
    return Action_keybinds(actions)