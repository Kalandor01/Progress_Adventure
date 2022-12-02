import copy
import math
import os
import shutil
import sys
import threading as thr
import time
import tkinter as tk

import dev_tools as dt
import tools as ts
import data_manager as dm
import entities as es
import save_manager as sm

from tools import r, sfm, col, getch
from tools import Log_type
from tools import MAIN_THREAD_NAME, AUTO_SAVE_THREAD_NAME, MANUAL_SAVE_THREAD_NAME
from tools import SAVES_FOLDER_PATH, SAVE_SEED, SAVE_EXT
from tools import AUTO_SAVE_DELAY, DOUBLE_KEYS
from tools import STANDARD_CURSOR_ICONS, DELETE_CURSOR_ICONS, ERROR_HANDLING


if __name__ == "__main__":
    try:
        print("Loading...")
        ts.threading.current_thread().name = MAIN_THREAD_NAME
        ts.begin_log()
        if ts.check_package_versions():
            ts.log_info("Preloading global variables")
            # dt.decode_save_file(SETTINGS_SEED, "settings")

            # GLOBAL VARIABLES
            GOOD_PACKAGES = True
            SETTINGS = dm.Settings(
                ts.settings_manager("auto_save"),
                ts.settings_manager("logging"),
                ts.settings_manager("keybinds"))
            ts.change_logging(SETTINGS.logging)
            SETTINGS.save_keybind_mapping()
            SAVE_DATA:dm.Save_data = None
            GLOBALS = dm.Globals(False, False, False, False)
            
            col.init()
        else:
            GOOD_PACKAGES = False
    except:
        ts.log_info("Preloading crashed", sys.exc_info(), Log_type.CRASH)
        raise



# Monster cheat sheet: name, life, attack, deff, speed, rare, team, switched
def fight_ran(num=1, cost=1, power_min=1, power_max=-1, round_up=False):
    monsters:list[es.Entity] = []
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
                    monster = es.Troll()
            cost -= 3
        elif monster_cost >= 2:
            monster_n = r.randint(0, 1)
            match monster_n:
                case 0:
                    monster = es.Ghoul()
            cost -= 2
        else:
            monster_n = r.randint(0, 1)
            match monster_n:
                case 0:
                    monster = es.Caveman()
            cost -= 1
        num -= 1
        monsters.append(monster)
    print("Random enemy maker:")
    fight(monsters)


# attacking with oop functions
def fight(monster_l:list[es.Entity]=None):
    player = SAVE_DATA.player
    if monster_l is None:
        monster_l = [es.Test()]
    # variables
    szum = 0
    for m in monster_l:
        szum += 1
        if m is None:
            monster_l = [es.Test()]
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


def save_game():
    frozen_data = copy.deepcopy(SAVE_DATA)
    sm.make_save(frozen_data)
    ts.log_info("Game saved", f'save name: {frozen_data.save_name}, player name: "{frozen_data.player.name}"')


# Auto save thread
def auto_saver():
    try:
        while True:
            time.sleep(AUTO_SAVE_DELAY)
            if GLOBALS.in_game_loop:
                if not GLOBALS.in_fight and not GLOBALS.saving:
                    GLOBALS.saving = True
                    ts.log_info("Beginning auto save", f"save name: {SAVE_DATA.save_name}")
                    save_game()
                    GLOBALS.saving = False
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
                if dm.is_key(SETTINGS.keybinds["esc"]):
                    if not GLOBALS.in_fight and not GLOBALS.saving:
                        GLOBALS.saving = True
                        ts.log_info("Beginning manual save", f"save name: {SAVE_DATA.save_name}")
                        GLOBALS.exiting = True
                        save_game()
                        GLOBALS.saving = False
                        break
                    else:
                        print("You can't exit now!")
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
    global SAVE_DATA
    SAVE_DATA = sm.create_save_data()
    sm.make_save(SAVE_DATA)
    ts.log_info("Created save", f'save_name: {SAVE_DATA.save_name}, player name: "{SAVE_DATA.player.name}"')
    game_loop()


def load_save(save_name:str):
    global SAVE_DATA
    SAVE_DATA = sm.load_save(save_name, SETTINGS.keybind_mapping)
    game_loop()


# REWORK THIS ASAP
def main_menu():
    # action functions
    def other_options():
        auto_save = sfm.Toggle(SETTINGS.auto_save, "Auto save: ")
        logging = sfm.Toggle(SETTINGS.logging, "Logging: ", "on", "minimal")
        other_settings = [auto_save, logging, None, sfm.UI_list(["Done"])]
        response = sfm.options_ui(other_settings, " Other options", key_mapping=SETTINGS.keybind_mapping)
        if response is not None:
            SETTINGS.change_others(auto_save.value, logging.value)

    def set_keybind(name:str):
        print("\n\nPress any key\n\n", end="")
        key = getch()
        if key in DOUBLE_KEYS:
            key = getch()
            key = [[], [key]]
        else:
            key = [[key], []]
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
                keybinds:dict[str, list[list[bytes]]] = ts.settings_manager("keybinds")
                new_keybinds:dict[str, dm.Key] = {}
                for x in keybinds:
                    new_keybinds[x] = dm.Key(keybinds[x])
                SETTINGS.keybinds = new_keybinds
                break
            # done
            elif ans > 5:
                SETTINGS.save_keybind_mapping()
                break
            else:
                set_keybind(list(SETTINGS.keybinds)[ans])

    files_data = sm.get_saves_data()
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
                            ts.log_info("Deleted save", f'save name: {files_data[option][0]}')
                            # remove
                            if os.path.isfile(f'{os.path.join(SAVES_FOLDER_PATH, files_data[option][0])}.{SAVE_EXT}'):
                                os.remove(f'{os.path.join(SAVES_FOLDER_PATH, files_data[option][0])}.{SAVE_EXT}')
                            else:
                                shutil.rmtree(os.path.join(SAVES_FOLDER_PATH, files_data[option][0]))
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
            files_data = sm.get_saves_data()
        # load
        elif status[0] == 0:
            ts.press_key(f"\nLoading save: {status[1]}!")
            load_save(status[1])
            files_data = sm.get_saves_data()


def gui_menu():
    # label = tk.Label(
    # text="Hello, Tkinter",
    # fg="white",
    # bg="black",
    # width=10,
    # height=10
    # )
    # button = tk.Button(
    # text="Click me!",
    # width=25,
    # height=5,
    # bg="blue",
    # fg="yellow",
    # )
    
    window = tk.Tk(className="Test window")
    window.mainloop()


def main():
    # dt.decode_save_file("settings", ROOT_FOLDER, SETTINGS_SEED)
    # dt.decode_save_file("new save")
    # dt.recompile_save_file("2022-07-10;16-58-51;save2", "old_save2", BACKUPS_FOLDER_PATH, SAVES_FOLDER_PATH, OLD_BACKUP_EXT, SAVE_EXT, 2, SAVE_SEED)
    # dt.encode_save_file("file_test")
    
    # dt.load_backup_menu()
    # main_menu()
    
    gui_menu()


def main_error_handler():
    # general crash handler (release only)

    exit_game = False
    while not exit_game:
        exit_game = True
        try:
            if GOOD_PACKAGES:
                ts.log_info("Beginning new instance")
                main()
        except:
            ts.log_info("Instance crashed", sys.exc_info(), Log_type.CRASH)
            if ERROR_HANDLING:
                print(f"ERROR: {sys.exc_info()[1]}")
                ans = input("Restart?(Y/N): ")
                if ans.upper() == "Y":
                    ts.log_info("Restarting instance")
                    exit_game = False
            else:
                raise
        else:
            col.deinit()
            # end log
            ts.log_info("Instance ended succesfuly")


if __name__ == "__main__":
    main_error_handler()
