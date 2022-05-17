﻿import copy
import json
import math
import os
import sys
import threading as thr
import time
from datetime import datetime
from msvcrt import getch

import save_file_manager as sfm

import classes as cl
import tools as ts

from tools import MAIN_THREAD_NAME, r

try:
    ts.threading.current_thread().name = MAIN_THREAD_NAME
    ts.log_info("Preloading global variables", new_line=True)
    # ts.decode_save_file(0, "settings")

    # CONSTANTS
    SAVE_FOLDER = os.path.dirname(os.path.abspath(__file__)) + "/saves"
    SAVE_NAME = "save*"
    SAVE_EXT = "sav"
    SAVE_FILE_PATH = os.path.join(SAVE_FOLDER, SAVE_NAME)

    # GLOBAL VARIABLES
    settings = cl.Settings(ts.settings_manager("auto_save"), ts.settings_manager("keybinds"))
    settings.save_keybind_mapping()
    save_data = cl.Save_data(None, None, None, None)

    _in_game_loop = False
    _in_fight = False

    # GLOBAL MODIFIERS


    def mod_in_game_loop(val=None):
        global _in_game_loop
        if val==None:
            return _in_game_loop
        else:
            _in_game_loop = val
    
    def mod_in_fight(val=None):
        global _in_fight
        if val==None:
            return _in_fight
        else:
            _in_fight = val


    def imput(ask="Num: ", type=int):
        """
        Only returns int/float.
        """
        while True:
            try: return type(input(ask))
            except ValueError: print(f'Not{" whole" if type == int else ""} number!')


    # dummy player for global
    player = cl.Player()
except:
    ts.log_info("Preloading crahed", sys.exc_info(), "ERROR")
    raise


# Monster cheat sheet: name, life, attack, deff, speed, rare, team, switched
def fight_ran(num=1, cost=1, power_min=1, power_max=-1, round_up=False):
    global player
    monsters = []
    monster = None
    for _ in range(num):
        # max cost calculation
        if round_up:
            costnum = math.ceil(cost / num)
        else:
            costnum = round(cost / num)
        if costnum < power_min:
            costnum = power_min
        # cost calculation
        if num > 1:
            monster_cost = r.randint(power_min, costnum + 1)
        else:
            monster_cost = cost
        # cost adjustment
        if monster_cost < power_min:
            monster_cost = power_min
        if power_max != -1 and monster_cost > power_max:
            monster_cost = power_max

        # monster choice
        if monster_cost >= 3:
            monster_n = r.randint(0, 1)
            match monster_n:
                case 0:
                    monster = cl.Troll()
            cost -= 3
        elif monster_cost >= 2:
            monster_n = r.randint(0, 1)
            match monster_n:
                case 0:
                    monster = cl.Ghoul()
            cost -= 2
        else:
            monster_n = r.randint(0, 1)
            match monster_n:
                case 0:
                    monster = cl.Caveman()
            cost -= 1
        num -= 1
        monsters.append(monster)
    print("Random enemy maker:")
    fight(monsters)


# attacking with oop functions
def fight(monster_l:list=None):
    if monster_l == None:
        monster_l = [cl.Test()]
    global player
    # variables
    szum = 0
    for m in monster_l:
        szum += 1
        if m is None:
            monster_l = [["test", 1, 1, 1, 1, False]]
            break
    attacking_m = ""
    # enemys
    max_team_n = 0
    for m in monster_l:
        if m.team > max_team_n:
            max_team_n = m.team
    for x in range(max_team_n + 1):
        print(f"\nTeam {x}:\n")
        if x == 0:
            print(f"{player.name}\nHP: {player.hp}\nAttack: {player.attack}\nDefence: {player.defence}\nSpeed: {player.speed}\n")
        for m in monster_l:
            if m.team == x:
                print(f"{m.name}", end="")
                if m.switched:
                    print(f" (Switched to this side!)", end="")
                print(f"\nHP: {m.hp}\nAttack: {m.attack}\nDefence: {m.defence}\nSpeed: {m.speed}\n")
    print()
    while player.hp > 0 and szum > 0:
        for m in monster_l:
            if m.hp > 0:
                attack = r.randint(1, 7) + player.attack
                attack_e = r.randint(1, 7) + m.attack
                # clash
                if attack == attack_e:
                    print("\nCLASH!")
                # damage
                elif attack < attack_e:
                    print(f"\n{m.name} attacked {player.name}: ", end="")
                    if r.random() > player.speed:
                        player.hp -= 2
                        if player.hp < 0:
                            player.hp = 0
                        print(f"-2 HP({player.hp})")
                        if player.hp <= 0:
                            attacking_m = m.name
                            break
                    else:
                        print("BLOCKED!")
                # attack
                else:
                    print(f"\n{player.name} attacked {m.name}: ", end="")
                    if r.random() > player.speed:
                        m.hp -= 2
                        if m.hp < 0:
                            m.hp = 0
                        print(f"-2 HP({m.hp})")
                    else:
                        m.hp -= 4
                        if m.hp < 0:
                            m.hp = 0
                        print(f"CRITICAL HIT: -4 HP({m.hp})")
                    if m.hp <= 0:
                        print(f"{player.name} defeated {m.name}")
                time.sleep(0.5)
        # sum life
        szum = 0
        for m in monster_l:
            if m.hp > 0:
                szum += 1
    # outcome
    if player.hp <= 0:
        player.hp = 0
        print(f"\n{attacking_m} defeated {player.name}!")
        stats()
    else:
        monsters_n = ""
        for x in range(len(monster_l)):
            monsters_n += monster_l[x].name
            if len(monster_l) - 2 == x:
                monsters_n += " and "
            elif len(monster_l) - 2 > x:
                monsters_n += ", "
        print(f"\n{player.name} defeated {monsters_n}!\n")


# stats
def stats(won=0):
    global player
    if won == 1:
        print("\nYou Win!!!")
    elif won == 0:
        print("\nYou lost!!!")
    print(f"\nName: {player.name}\n\nSTATS:")
    if won != 0:
        print(f"HP: {player.hp}")
    print(f"Attack: {player.attack}\nDefence: {player.defence}\nSpeed: {player.speed}\n")
    if won == 0 or won == 1:
        print(f"OTHER:")


def prepair_fight(data):
    mod_in_fight(True)
    fight_ran(3, 5)
    mod_in_fight(False)


def save_game():
    frozen_data = copy.deepcopy(save_data)


# Auto save thread
def auto_saver():
    try:
        while True:
            time.sleep(5)
            if mod_in_game_loop():
                ts.log_info("Beggining auto save", f"slot number: {save_data.save_num}")
                save_game()
            else:
                break
    except:
        ts.log_info("Thread crahed", sys.exc_info(), "ERROR")
        raise


# quit thread
def quit_game():
    try:
        while True:
            if mod_in_game_loop():
                if ts.is_key([settings.keybinds["esc"].value, settings.DOUBLE_KEYS]):
                    if not mod_in_fight():
                        ts.log_info("Beggining manual save", f"slot number: {save_data.save_num}")
                        save_game()
                        break
                    else:
                        print("You can't exit while a fight happening!")
            else:
                break
    except:
        ts.log_info("Thread crahed", sys.exc_info(), "ERROR")
        raise
    

def game_loop(data):
    # PREPARING
    ts.log_info("Preparing game data")
    # load random state
    r.set_state(ts.random_state_converter(data["seed"]))
    # load to class
    global save_data
    save_data = cl.Save_data(data["save_num"], data["last_access"], data["player"], r.get_state())
    mod_in_game_loop(True)
    # GAME LOOP
    ts.log_info("Game loop started")
    # TRHEADS
    # manual quit
    thread_quit = thr.Thread(target=quit_game, name="Quit manager", daemon=True)
    thread_quit.start()
    # auto saver
    if settings.auto_save:
        thread_save = thr.Thread(target=auto_saver, name="Auto saver", daemon=True)
        thread_save.start()
    # GAME
    stats(-1)
    print("Wandering...")
    time.sleep(5)
    prepair_fight(save_data)
    # ENDING
    mod_in_game_loop(False)
    input("Exiting...Press keys!")
    ts.log_info("Game loop ended")

    
def new_save(save_num=1):
    # make player
    global player
    player = cl.Player(input("What is your name?: "))
    # make new save data
    new_display_data = {}
    new_save_data = {}
    # last_acces
    now = datetime.now()
    last_access = {"last_access": [now.year, now.month, now.day, now.hour, now.minute, now.second]}
    new_display_data.update(last_access)
    new_save_data.update(last_access)
    # player
    player_data = {"player": {"name": player.name, "hp": player.hp, "attack": player.attack, "defence": player.defence, "speed": player.speed}}
    new_display_data.update({"player_name": player.name})
    new_save_data.update(player_data)
    # randomstate
    new_save_data.update(ts.random_state_converter(r))
    # create new save
    try:
        f = open(f'{SAVE_FILE_PATH.replace("*", str(save_num))}.{SAVE_EXT}', "w")
        f.close()
    except FileNotFoundError:
        os.mkdir("saves")
        # log
        ts.log_info("Recreating saves folder")
    sfm.encode_save([json.dumps(new_display_data), json.dumps(new_save_data)], save_num, SAVE_FILE_PATH, SAVE_EXT)
    # log
    ts.log_info("Created save", f'slot number: {save_num}, player name: "{player.name}"')
    # extra data
    new_save_data["save_num"] = save_num
    new_save_data["player"] = player
    game_loop(new_save_data)

# json_j = json.loads(sfm.decode_save()[0])

def load_save(save_num=1):
    # read data
    datas = json.loads(sfm.decode_save(save_num, SAVE_FILE_PATH, SAVE_EXT)[1])
    # player
    player_data = datas["player"]
    player.name = str(player_data["name"])
    player.hp = int(player_data["hp"])
    player.attack = int(player_data["attack"])
    player.defence = int(player_data["defence"])
    player.speed = float(player_data["speed"])
    # log
    last_accessed = datas["last_access"]
    ts.log_info("Loaded save", f'slot number: {save_num}, hero name: "{player.name}", last saved: {ts.make_date(last_accessed)} {ts.make_time(last_accessed[3:])}')
    # extra data
    datas["save_num"] = save_num
    datas["player"] = player
    game_loop(datas)


def get_saves_data():
    try:
        f = open(f'{SAVE_FILE_PATH.replace("*", "0")}.{SAVE_EXT}', "w")
        f.close()
        os.remove(f'{SAVE_FILE_PATH.replace("*", "0")}.{SAVE_EXT}')
    except FileNotFoundError:
        os.mkdir("saves")
        # log
        ts.log_info("Recreating saves folder")
    datas = sfm.file_reader_s(SAVE_NAME, SAVE_FOLDER, 1)
    # process file data
    datas_processed = []
    for data in datas:
        if data[1] == -1:
            ts.log_info("Decode error", f"Slot number: {data[0]}", "ERROR")
            input(f"Save file {data[0]} is corrupted!")
        else:
            try:
                data[1] = json.loads(data[1][0])
                data_processed = ""
                data_processed += f"Save file {data[0]}: {data[1]['player_name']}\n"
                last_accessed = data[1]["last_access"]
                data_processed += f"Last opened: {ts.make_date(last_accessed, '.')} {ts.make_time(last_accessed[3:])}"
                datas_processed.append([data[0], data_processed])
            except (TypeError, IndexError):
                ts.log_info("Parse error", f"Slot number: {data[0]}", "ERROR")
                input(f"Save file {data[0]} could not be parsed!")
    return datas_processed


def main_menu():
    # action functions
    def other_options():
        auto_save = sfm.Toggle(settings.auto_save, "Auto save: ")
        sfm.options_ui([auto_save, None, sfm.UI_list(["Back"])], " Other options", key_mapping=settings.keybind_mapping)
        settings.auto_save = bool(auto_save.value)
        ts.settings_manager("auto_save", settings.auto_save)

    def set_keybind(name:str):
        print("\n\nPress any key\n\n", end="")
        key = getch()
        if key in [b"\xe0", b"\x00"]:
            key = getch()
            key = [key, 1]
        else:
            key = [key]
        settings.keybinds[name].change(key)

    def keybind_setting():
        while True:
            ans = sfm.UI_list_s([
            f"Escape: {settings.keybinds['esc'].name}",
            f"Up: {settings.keybinds['up'].name}",
            f"Down: {settings.keybinds['down'].name}",
            f"Left: {settings.keybinds['left'].name}",
            f"Right: {settings.keybinds['right'].name}",
            f"Enter: {settings.keybinds['enter'].name}",
            None, "Done"
            ], " Keybinds", False, True).display(settings.keybind_mapping)
            # exit
            if ans == -1:
                keybinds = ts.settings_manager("keybinds")
                for x in keybinds:
                    keybinds[x] = cl.Key(keybinds[x])
                settings.keybinds = keybinds
                break
            # done
            elif ans > 5:
                settings.save_keybind_mapping()
                break
            else:
                set_keybind(list(settings.keybinds)[ans])

    files_data = get_saves_data()
    in_main_menu = True
    while True:
        status = [-1, -1]
        if len(files_data):
            if in_main_menu:
                in_main_menu = False
                option = sfm.UI_list(["New save", "Load/Delete save", "Options"], " Main menu", can_esc=True).display(settings.keybind_mapping)
            else:
                option = 1
            # new file
            if option == 0:
                new_slot = 1
                for data in files_data:
                    if data[0] == new_slot:
                        new_slot += 1
                status = [1, new_slot]
            elif option == -1:
                break
            # load/delete
            elif option == 1:
                # get data from file_data
                list_data = []
                for data in files_data:
                    list_data.append(data[1])
                    list_data.append(None)
                list_data.append("Delete file")
                list_data.append("Back")
                option = sfm.UI_list_s(list_data, " Level select", True, True, exclude_none=True).display(settings.keybind_mapping)
                # load
                if option != -1 and option < len(files_data):
                    status = [0, files_data[int(option)][0]]
                # delete
                elif option == len(files_data):
                    # remove "delete file"
                    list_data.pop(len(list_data) - 2)
                    while len(files_data) > 0:
                        option = sfm.UI_list(list_data, " Delete mode!", "X ", "  ", multiline=True, can_esc=True, exclude_none=True).display(settings.keybind_mapping)
                        if option != -1 and option < (len(list_data) - 1) / 2:
                            if sfm.UI_list_s(["No", "Yes"], f" Are you sure you want to remove Save file {files_data[option][0]}?", can_esc=True).display(settings.keybind_mapping):
                                # log
                                datas = json.loads(sfm.decode_save(files_data[option][0], SAVE_FILE_PATH, SAVE_EXT, decode_until=1)[0])
                                last_accessed = datas["last_access"]
                                ts.log_info("Deleted save", f'slot number: {files_data[option][0]}, hero name: "{datas["player_name"]}", last saved: {ts.make_date(last_accessed)} {ts.make_time(last_accessed[3:])}')
                                # remove
                                os.remove(f'{SAVE_FILE_PATH.replace("*", str(files_data[option][0]))}.{SAVE_EXT}')
                                list_data.pop(option * 2)
                                list_data.pop(option * 2)
                                files_data.pop(option)
                        else:
                            break
                # back
                else:
                    in_main_menu = True
            elif option == 2:
                sfm.UI_list_s(["Keybinds", "Other", None, "Back"], " Options", False, True, [keybind_setting, other_options], True).display(settings.keybind_mapping)
                in_main_menu = True
        else:
            input(f"\n No save files detected!")
            status = [1, 1]

        # action
        # new save
        if status[0] == 1:
            input(f"\nNew game in slot {status[1]}!\n")
            # new slot?
            new_save(status[1])
        # load
        elif status[0] == 0:
            input(f"\nLoading slot {status[1]}!")
            load_save(status[1])


def main():
    # ts.decode_save_file(0, "settings")
    # ts.decode_save_file(1, SAVE_FILE_PATH)
    main_menu()


if __name__ == "__main__":
    # ultimate error handlind (release only)
    error_handling = False

    # begin log
    ts.log_info("Beginning new instance")

    exit_game = False
    while not exit_game:
        exit_game = True
        try:
            main()
        except:
            ts.log_info("Instance crahed", sys.exc_info(), "ERROR")
            if error_handling:
                print(f"ERROR: {sys.exc_info()[1]}")
                ans = input("Restart?(Y/N): ")
                if ans.upper() == "Y":
                    ts.log_info("Restarting instance")
                    exit_game = False
            else:
                raise
        else:
            # end log
            ts.log_info("Instance ended succesfuly")
