import copy
import json
import math
import os
import sys
import threading as thr
import time
from datetime import datetime as dtime
from msvcrt import getch

import tools as ts
import dev_tools as dt
import classes as cl

from tools import r, sfm
from tools import MAIN_THREAD_NAME, AUTO_SAVE_THREAD_NAME, MANUAL_SAVE_THREAD_NAME
from tools import SAVES_FOLDER_PATH, SAVE_SEED, SAVE_EXT
from tools import BACKUPS_FOLDER_PATH, ROOT_FOLDER, BACKUP_EXT
from tools import AUTO_SAVE_DELAY, ENCODING, SETTINGS_SEED, FILE_ENCODING_VERSION, SAVE_VERSION
from tools import SAVE_FILE_NAME_DATA
from tools import SAVE_FOLDER_NAME_CHUNKS
from tools import Color, Style, Log_type
from tools import STANDARD_CURSOR_ICONS, DELETE_CURSOR_ICONS

if __name__ == "__main__":
    try:
        ts.threading.current_thread().name = MAIN_THREAD_NAME
        ts.begin_log()
        if ts.check_package_versions():
            ts.log_info("Preloading global variables")
            # dt.decode_save_file(SETTINGS_SEED, "settings")

            # GLOBAL VARIABLES
            GOOD_PACKAGES = True
            SETTINGS = cl.Settings(
                ts.settings_manager("auto_save"),
                ts.settings_manager("logging"),
                ts.settings_manager("keybinds"))
            ts.change_logging(SETTINGS.logging)
            SETTINGS.save_keybind_mapping()
            SAVE_DATA = cl.Save_data
            GLOBALS = cl.Globals(False, False, False)
        else:
            GOOD_PACKAGES = False
    except:
        ts.log_info("Preloading crashed", sys.exc_info(), Log_type.CRASH)
        raise


def imput(ask="Num: ", type=int):
    """
    Only returns int/float.
    """
    while True:
        try: return type(input(ask))
        except ValueError: print(f'Not{" whole" if type == int else ""} number!')


# Monster cheat sheet: name, life, attack, deff, speed, rare, team, switched
def fight_ran(num=1, cost=1, power_min=1, power_max=-1, round_up=False):
    monsters:list[cl.Entity] = []
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
def fight(monster_l:list[cl.Entity]=None):
    player = SAVE_DATA.player
    if monster_l == None:
        monster_l = [cl.Test()]
    # variables
    szum = 0
    for m in monster_l:
        szum += 1
        if m is None:
            monster_l = [cl.Test()]
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
    # fight
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
        loots = []
        for m in monster_l:
            loots.extend(m.drops)
            print(loots)
        player.inventory.loot(loots)


# stats
def stats(won=0):
    player = SAVE_DATA.player
    if won == 1:
        print("\nYou Win!!!")
    elif won == 0:
        print("\nYou lost!!!")
    print(f"\nName: {player.name}\n\nSTATS:")
    if won != 0:
        print(f"HP: {player.hp}")
    print(f"Attack: {player.attack}\nDefence: {player.defence}\nSpeed: {player.speed}\n")
    if won == 0 or won == 1:
        print(player.inventory)
        print()


def prepair_fight():
    GLOBALS.in_fight = True
    ts.log_info("Fight started")
    fight_ran(3, 5)
    stats(1)
    ts.log_info("Fight ended")
    GLOBALS.in_fight = False


def make_save(data:cl.Save_data):
    # make backup
    backup_status = ts.make_backup(data.save_name, True)
    # DATA FILE
    # make player
    player = data.player
    # make new save data
    display_data = {}
    save_data = {}
    # save_version
    display_data["save_version"] = SAVE_VERSION
    save_data["save_version"] = SAVE_VERSION
    # display_name
    display_data["display_name"] = data.display_save_name
    save_data["display_name"] = data.display_save_name
    # last_access
    now = dtime.now()
    last_access = [now.year, now.month, now.day, now.hour, now.minute, now.second]
    display_data["last_access"] = last_access
    save_data["last_access"] = last_access
    # player
    display_data["player_name"] = player.name
    save_data["player"] = {"name": player.name, "hp": player.hp, "attack": player.attack, "defence": player.defence, "speed": player.speed}
    save_data["player"]["inventory"] = list(ts.inventory_converter(player.inventory.items))
    # randomstate
    save_data["seed"] = ts.random_state_converter(r)
    # create new save
    ts.encode_save_s([display_data, save_data], os.path.join(SAVES_FOLDER_PATH, data.save_name, SAVE_FILE_NAME_DATA))
    # remove backup
    if backup_status != False:
        os.remove(backup_status[0])
        ts.log_info("Removed temporary backup", backup_status[1])


def save_game():
    frozen_data = copy.deepcopy(SAVE_DATA)
    make_save(frozen_data)
    ts.log_info("Game saved", f'save name: {frozen_data.save_name}, player name: "{frozen_data.player.name}"')


# Auto save thread
def auto_saver():
    try:
        while True:
            time.sleep(AUTO_SAVE_DELAY)
            if GLOBALS.in_game_loop:
                if not GLOBALS.in_fight:
                    ts.log_info("Beginning auto save", f"save name: {SAVE_DATA.save_name}")
                    save_game()
            else:
                break
    except:
        ts.log_info("Thread crashed", sys.exc_info(), Log_type.CRASH)
        raise


# quit thread
def quit_game():
    try:
        while True:
            if GLOBALS.in_game_loop:
                if ts.is_key(SETTINGS.keybinds["esc"]):
                    if not GLOBALS.in_fight:
                        ts.log_info("Beginning manual save", f"save name: {SAVE_DATA.save_name}")
                        GLOBALS.exiting = True
                        save_game()
                        break
                    else:
                        print("You can't exit while a fight is happening!")
            else:
                break
    except:
        ts.log_info("Thread crashed", sys.exc_info(), Log_type.CRASH)
        raise
    

def game_loop():
    GLOBALS.in_game_loop = True
    # GAME LOOP
    ts.log_info("Game loop started")
    # TRHEADS
    # manual quit
    thread_quit = thr.Thread(target=quit_game, name=MANUAL_SAVE_THREAD_NAME, daemon=True)
    thread_quit.start()
    # auto saver
    if SETTINGS.auto_save:
        thread_save = thr.Thread(target=auto_saver, name=AUTO_SAVE_THREAD_NAME, daemon=True)
        thread_save.start()
    # GAME
    stats(-1)
    print("Wandering...")
    time.sleep(5)
    if not GLOBALS.exiting:
        prepair_fight()
        save_game()
        # save_game() maybe instead of the auto save
        # ENDING
    GLOBALS.exiting = False
    GLOBALS.in_game_loop = False
    ts.press_key("Exiting...Press keys!")
    ts.log_info("Game loop ended")

    
def new_save():
    ts.log_info("Preparing game data")
    # make save name
    display_save_name = input("Name your save: ")
    if display_save_name == "":
        display_save_name = "new save"
    save_name = ts.remove_bad_characters(display_save_name)
    if save_name == "":
        save_name = "new_save"
    if ts.check_save_name(save_name):
        extra_num = 1
        while ts.check_save_name(save_name + "_" + str(extra_num)):
            extra_num += 1
        save_name += "_" + str(extra_num)
    # make player
    player = cl.Player(input("What is your name?: "))
    # last_access
    now = dtime.now()
    last_access = [now.year, now.month, now.day, now.hour, now.minute, now.second]
    # load to class
    global SAVE_DATA
    SAVE_DATA = cl.Save_data(save_name, display_save_name, last_access, player, r.get_state())
    make_save(SAVE_DATA)
    ts.log_info("Created save", f'save_name: {save_name}, player name: "{player.name}"')
    game_loop()


def correct_save_data(data:dict, save_version:int, extra_data:dict):
    ts.log_info("Correcting save data")
    # 0.0 -> 1.0
    if save_version == 0.0:
        save_version = 1.0
        ts.log_info("Corrected save data", "0.0 -> 1.0")
    # 1.0 -> 1.1
    if save_version == 1.0:
        data["player"]["inventory"] = []
        save_version = 1.1
        ts.log_info("Corrected save data", "1.0 -> 1.1")
    # 1.1 -> 1.2
    if save_version == 1.1:
        data["display_name"] = extra_data["save_name"]
        save_version = 1.2
        ts.log_info("Corrected save data", "1.1 -> 1.2")
    return data


def load_save(save_name:str):
    # read data
    data = ts.decode_save_s(os.path.join(SAVES_FOLDER_PATH, save_name), 1)
    # save version
    try: save_version = data["save_version"]
    except KeyError: save_version = 0.0
    if save_version != SAVE_VERSION:
        is_older = ts.check_p_version(str(save_version), str(SAVE_VERSION))
        ts.log_info("Trying to load save with an incorrect version", f"{SAVE_VERSION} -> {save_version}", Log_type.WARN)
        ans = sfm.UI_list(["Yes", "No"], f"\"{save_name}\" is {('an older version' if is_older else 'a newer version')} than what it should be! Do you want to back up the save file before loading it?").display(SETTINGS.keybind_mapping)
        if ans == 0:
            ts.make_backup(save_name)
        data = correct_save_data(data, save_version, {"save_name": save_name})
    # display_name
    display_name = data["display_name"]
    # last access
    last_access = data["last_access"]
    # player
    player_data = data["player"]
    player = cl.Player(player_data["name"])
    player.hp = int(player_data["hp"])
    player.attack = int(player_data["attack"])
    player.defence = int(player_data["defence"])
    player.speed = float(player_data["speed"])
    player.inventory.items = list(ts.inventory_converter(player_data["inventory"]))
    # log
    ts.log_info("Loaded save", f'save name: {save_name}, hero name: "{player.name}", last saved: {ts.make_date(last_access)} {ts.make_time(last_access[3:])}')
    
    # PREPARING
    ts.log_info("Preparing game data")
    # load random state
    r.set_state(ts.random_state_converter(data["seed"]))
    # load to class
    global SAVE_DATA
    SAVE_DATA = cl.Save_data(save_name, display_name, last_access, player, r.get_state())
    game_loop()


def get_saves_data():
    ts.recreate_saves_folder()
    # read saves
    datas = sfm.file_reader_blank(SAVE_SEED, SAVES_FOLDER_PATH, 1)
    # process file data
    datas_processed = []
    for data in datas:
        if data[1] == -1:
            ts.log_info("Decode error", f"Save name: {data[0]}", Log_type.ERROR)
            ts.press_key(f"\"{data[0]}\" is corrupted!")
        else:
            try:
                data[1] = json.loads(data[1][0])
                data_processed = ""
                try:
                    dispaly_name = data[1]['display_name']
                except KeyError:
                    dispaly_name = data[0]
                data_processed += f"{dispaly_name}: {data[1]['player_name']}\n"
                last_access = data[1]["last_access"]
                data_processed += f"Last opened: {ts.make_date(last_access, '.')} {ts.make_time(last_access[3:])}"
                # check version
                try: save_version = data[1]["save_version"]
                except KeyError: save_version = 0.0
                data_processed += ts.stylized_text(f" v.{save_version}", (Color.GREEN if save_version == SAVE_VERSION else Color.RED))
                datas_processed.append([data[0], data_processed])
            except (TypeError, IndexError):
                ts.log_info("Parse error", f"Save name: {data[0]}", Log_type.ERROR)
                ts.press_key(f"\"{data[0]}\" could not be parsed!")
    return datas_processed


# REWORK THIS ASAP
def main_menu():
    # action functions
    def other_options():
        auto_save = sfm.Toggle(SETTINGS.auto_save, "Auto save: ")
        logging = sfm.Toggle(SETTINGS.logging, "Logging: ", "on", "minimal")
        other_settings = [auto_save, logging, None, sfm.UI_list(["Done"])]
        response = sfm.options_ui(other_settings, " Other options", key_mapping=SETTINGS.keybind_mapping)
        if response != None:
            SETTINGS.change_others(auto_save.value, logging.value)

    def set_keybind(name:str):
        print("\n\nPress any key\n\n", end="")
        key = getch()
        if key in [b"\xe0", b"\x00"]:
            key = getch()
            key = [key, 1]
        else:
            key = [key]
        SETTINGS.keybinds[name].change(key)

    def keybind_setting():
        while True:
            ans = sfm.UI_list_s([
            f"Escape: {SETTINGS.keybinds['esc'].name}",
            f"Up: {SETTINGS.keybinds['up'].name}",
            f"Down: {SETTINGS.keybinds['down'].name}",
            f"Left: {SETTINGS.keybinds['left'].name}",
            f"Right: {SETTINGS.keybinds['right'].name}",
            f"Enter: {SETTINGS.keybinds['enter'].name}",
            None, "Done"
            ], " Keybinds", False, True).display(SETTINGS.keybind_mapping)
            # exit
            if ans == -1:
                keybinds = ts.settings_manager("keybinds")
                for x in keybinds:
                    keybinds[x] = cl.Key(keybinds[x])
                SETTINGS.keybinds = keybinds
                break
            # done
            elif ans > 5:
                SETTINGS.save_keybind_mapping()
                break
            else:
                set_keybind(list(SETTINGS.keybinds)[ans])

    files_data = get_saves_data()
    in_main_menu = True
    while True:
        status = [-1, -1]
        if in_main_menu:
            in_main_menu = False
            if len(files_data):
                mm_list = ["New save", "Load/Delete save", "Options"]
            else:
                mm_list = ["New save", "Options"]
            option = sfm.UI_list_s(mm_list, " Main menu", can_esc=True).display(SETTINGS.keybind_mapping)
        elif len(files_data):
            option = 1
        else:
            option = -2
            in_main_menu = True
        # new file
        if option == 0:
            status = [1, ""]
        elif option == -1:
            break
        # load/delete
        elif option == 1 and len(files_data):
            # get data from file_data
            list_data = []
            for data in files_data:
                print(data[1])
                list_data.append(data[1])
                list_data.append(None)
            list_data.append("Delete file")
            list_data.append("Back")
            option = sfm.UI_list_s(list_data, " Level select", True, True, exclude_nones=True).display(SETTINGS.keybind_mapping)
            # load
            if option != -1 and option < len(files_data):
                status = [0, files_data[int(option)][0]]
            # delete
            elif option == len(files_data):
                # remove "delete file"
                list_data.pop(len(list_data) - 2)
                while len(files_data) > 0:
                    option = sfm.UI_list(list_data, " Delete mode!", DELETE_CURSOR_ICONS, True, True, exclude_nones=True).display(SETTINGS.keybind_mapping)
                    if option != -1 and option < (len(list_data) - 1) / 2:
                        if sfm.UI_list_s(["No", "Yes"], f" Are you sure you want to remove Save file {files_data[option][0]}?", can_esc=True).display(SETTINGS.keybind_mapping):
                            # log
                            datas = ts.decode_save_s(os.path.join(SAVES_FOLDER_PATH, files_data[option][0]), 0)
                            last_access = datas["last_access"]
                            ts.log_info("Deleted save", f'save name: {files_data[option][0]}, hero name: "{datas["player_name"]}", last saved: {ts.make_date(last_access)} {ts.make_time(last_access[3:])}')
                            # remove
                            os.remove(f'{os.path.join(SAVES_FOLDER_PATH, files_data[option][0])}.{SAVE_EXT}')
                            list_data.pop(option * 2)
                            list_data.pop(option * 2)
                            files_data.pop(option)
                    else:
                        break
                if len(files_data) == 0:
                    in_main_menu = True
            # back
            else:
                in_main_menu = True
        elif (option == 2 and len(files_data)) or (option == 1 and not len(files_data)):
            sfm.UI_list(["Keybinds", "Other", None, "Back"], " Options", None, False, True, [keybind_setting, other_options], True).display(SETTINGS.keybind_mapping)
            in_main_menu = True

        # action
        # new save
        if status[0] == 1:
            ts.press_key(f"\nCreating new save!\n")
            new_save()
            files_data = get_saves_data()
        # load
        elif status[0] == 0:
            ts.press_key(f"\nLoading save: {status[1]}!")
            load_save(status[1])
            files_data = get_saves_data()


def main():
    # dt.decode_save_file("settings", ROOT_FOLDER, SETTINGS_SEED)
    # dt.decode_save_file("plz_work_00_52_16")
    # dt.recompile_save_file("2022-07-10;16-58-51;save2", "old_save2", BACKUPS_FOLDER_PATH, SAVES_FOLDER_PATH, BACKUP_EXT, SAVE_EXT, 2, SAVE_SEED)
    
    # dt.load_backup_menu()
    main_menu()


def main_error_handler():
    # ultimate error handlind (release only)
    error_handling = False

    exit_game = False
    while not exit_game:
        exit_game = True
        try:
            if GOOD_PACKAGES:
                ts.log_info("Beginning new instance")
                main()
        except:
            ts.log_info("Instance crashed", sys.exc_info(), 3)
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


if __name__ == "__main__":
    main_error_handler()
