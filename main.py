from copy import deepcopy
import math
from sys import exc_info
from threading import Thread
from time import sleep
from typing import Literal

try:
    from utils import Color, stylized_text, getwch, press_key
    import tools as ts
    from keybinds import Action_types, Action_key, Action_keybinds
    from data_manager import Settings, Globals, Save_data, is_key
    from chunk_manager import World
    import entities as es
    import save_manager as sm

    from tools import main_seed, Log_type, sfm, col
    from constants import                                                   \
        MAIN_THREAD_NAME, AUTO_SAVE_THREAD_NAME, MANUAL_SAVE_THREAD_NAME,   \
        DELETE_CURSOR_ICONS,                                                \
        ERROR_HANDLING,                                                     \
        AUTO_SAVE_INTERVAL, AUTO_SAVE_DELAY,                                \
        DOUBLE_KEYS
except (ModuleNotFoundError, ImportError):
    input(f"ERROR: {exc_info()[1]}")
    import sys
    sys.exit(1)


if __name__ == "__main__":
    try:
        print("Loading...")
        ts.threading.current_thread().name = MAIN_THREAD_NAME
        ts.log_separator()
        if ts.check_package_versions():
            ts.logger("Preloading global variables")
            # import dev_tools as dt
            # dt.decode_save_file(SETTINGS_SEED, SETTINGS_FILE_NAME)

            # GLOBAL VARIABLES
            GOOD_PACKAGES = True
            Settings()
            Globals()
            
            col.init()
        else:
            GOOD_PACKAGES = False
    except:
        ts.logger("Preloading crashed", str(exc_info()), Log_type.FATAL)
        if ERROR_HANDLING:
            input(f"ERROR: {exc_info()[1]}")
        raise



# MOVE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
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
            monster_cost = main_seed.randint(power_min, costnum + 1)
        else:
            monster_cost = cost
        # cost adjustment
        if monster_cost < power_min:
            monster_cost = power_min
        if power_max != -1 and monster_cost > power_max:
            monster_cost = power_max

        # monster choice
        monster = None
        if monster_cost >= 3:
            monster_n = main_seed.randint(0, 1)
            match monster_n:
                case 0:
                    monster = es.Troll()
            cost -= 3
        elif monster_cost >= 2:
            monster_n = main_seed.randint(0, 1)
            match monster_n:
                case 0:
                    monster = es.Ghoul()
            cost -= 2
        else:
            monster_n = main_seed.randint(0, 1)
            match monster_n:
                case 0:
                    monster = es.Caveman()
            cost -= 1
        num -= 1
        if monster is not None:
            monsters.append(monster)
    print("Random enemy maker:")
    fight(monsters)


# attacking with oop functions
def fight(monster_l:list[es.Entity]|None=None):
    player = Save_data.player
    if monster_l is None:
        monster_l = [es.Caveman()]
    # variables
    szum = 0
    for m in monster_l:
        szum += 1
        if m is None:
            monster_l = [es.Caveman()]
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
            print(f"{player.full_name}\nHP: {player.hp}\nAttack: {player.attack}\nDefence: {player.defence}\nSpeed: {player.speed}\n")
        for m in monster_l:
            if m.team == x:
                print(f"{m.full_name}", end="")
                if m.switched:
                    print(f" (Switched to this side!)", end="")
                print(f"\nHP: {m.hp}\nAttack: {m.attack}\nDefence: {m.defence}\nSpeed: {m.speed}\n")
    print()
    # fight
    while player.hp > 0 and szum > 0:
        for m in monster_l:
            if m.hp > 0:
                attack = main_seed.randint(1, 7) + player.attack
                attack_e = main_seed.randint(1, 7) + m.attack
                # clash
                if attack == attack_e:
                    print("\nCLASH!")
                # damage
                elif attack < attack_e:
                    print(f"\n{m.full_name} attacked {player.full_name}: ", end="")
                    if main_seed.random() > player.speed:
                        player.hp -= 2
                        if player.hp < 0:
                            player.hp = 0
                        print(f"-2 HP({player.hp})")
                        if player.hp <= 0:
                            attacking_m = m.full_name
                            break
                    else:
                        print("BLOCKED!")
                # attack
                else:
                    print(f"\n{player.full_name} attacked {m.full_name}: ", end="")
                    if main_seed.random() > player.speed:
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
                        print(f"{player.full_name} defeated {m.full_name}")
                sleep(0.5)
        # sum life
        szum = 0
        for m in monster_l:
            if m.hp > 0:
                szum += 1
    # outcome
    if player.hp <= 0:
        player.hp = 0
        print(f"\n{attacking_m} defeated {player.full_name}!")
        stats()
    else:
        monsters_n = ""
        for x in range(len(monster_l)):
            monsters_n += monster_l[x].full_name
            if len(monster_l) - 2 == x:
                monsters_n += " and "
            elif len(monster_l) - 2 > x:
                monsters_n += ", "
        print(f"\n{player.full_name} defeated {monsters_n}!\n")
        loots = []
        for m in monster_l:
            loots.extend(m.drops)
        player.inventory.loot(loots)


# stats
def stats(won=0):
    player = Save_data.player
    if won == 1:
        print("\nYou Win!!!")
    elif won == 0:
        print("\nYou lost!!!")
    print(f"\nName: {player.full_name}\n\nSTATS:")
    if won != 0:
        print(f"HP: {player.hp}")
    print(f"Attack: {player.attack}\nDefence: {player.defence}\nSpeed: {player.speed}\n")
    if won == 0 or won == 1:
        print(player.inventory)
        print()
# MOVE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!



def prepair_fight():
    Globals.in_fight = True
    ts.logger("Fight started")
    fight_ran(3, 5)
    stats(1)
    ts.logger("Fight ended")
    Globals.in_fight = False


def save_game():
    Globals.saving = True
    sm.make_save()
    ts.logger("Game saved", f'save name: {Save_data.save_name}, player name: "{Save_data.player.full_name}"')
    Globals.saving = False


# Auto save thread
def auto_saver():
    try:
        while True:
            sleep(AUTO_SAVE_INTERVAL)
            if Globals.in_game_loop:
                saved = False
                while not saved:
                    if Globals.in_game_loop and not Globals.saving and not Globals.in_fight:
                        ts.logger("Beginning auto save", f"save name: {Save_data.save_name}")
                        save_game()
                        saved = True
                    elif Globals.in_game_loop:
                        sleep(AUTO_SAVE_DELAY)
                    else:
                        break
            if not Globals.in_game_loop:
                break
    except:
        ts.logger("Thread crashed", str(exc_info()), Log_type.FATAL)
        raise


# quit thread
def quit_game():
    try:
        while True:
            if Globals.in_game_loop:
                if is_key(Settings.keybinds.get_action_key(Action_types.ESCAPE)):
                    if not Globals.in_fight and not Globals.saving:
                        ts.logger("Beginning manual save", f"save name: {Save_data.save_name}")
                        Globals.exiting = True
                        save_game()
                        break
                    else:
                        print("You can't exit now!")
            else:
                break
    except:
        ts.logger("Thread crashed", str(exc_info()), Log_type.FATAL)
        raise


def game_loop():
    Globals.in_game_loop = True
    # GAME LOOP
    ts.logger("Game loop started")
    # TRHEADS
    # manual quit
    thread_quit = Thread(target=quit_game, name=MANUAL_SAVE_THREAD_NAME, daemon=True)
    thread_quit.start()
    # auto saver
    if Settings.auto_save:
        thread_save = Thread(target=auto_saver, name=AUTO_SAVE_THREAD_NAME, daemon=True)
        thread_save.start()
    # GAME
    if sfm.UI_list(["NO", "YES"], "FILL?").display():
        from constants import SAVES_FOLDER_PATH
        from os.path import join
        World.load_all_chunks_from_folder()
        World.make_rectangle(False, join(SAVES_FOLDER_PATH, "jh"))
        World.fill_all_chunks("fill...")
        save_game()
    else:
        stats(-1)
        print("Wandering...")
        for _ in range(200):
            if not Globals.exiting:
                sleep(0.1)
                Save_data.player.weighted_turn()
                Save_data.player.move()
                pos = Save_data.player.pos
                tile = World.get_tile(pos[0], pos[1], True, Save_data.save_name)
                World.get_chunk(pos[0], pos[1]).fill_chunk()
                tile.visit()
        if not Globals.exiting:
            sleep(5)
        if not Globals.exiting:
            prepair_fight()
            save_game()
        # save_game() maybe instead of the auto save
        # ENDING
    Globals.exiting = False
    Globals.in_game_loop = False
    press_key("Exiting...Press keys!")
    ts.logger("Game loop ended")


def new_save():
    sm.create_save_data()
    sm.make_save()
    ts.logger("Created save", f'save_name: {Save_data.save_name}, player name: "{Save_data.player.full_name}"')
    game_loop()


def load_save(save_name:str, is_file=False):
    backup_choice = Settings.def_backup_action == -1
    automatic_backup = bool(Settings.def_backup_action)
    sm.load_save(save_name, is_file, backup_choice, automatic_backup)
    game_loop()


def regenerate_save_file(save_name:str, is_file=False, make_backup=True):
    print(f'Regenerating "{save_name}":')
    ts.logger("Regenerating save file", f"save_name: {save_name}")
    print(f"\tLoading...", end="", flush=True)
    sm.load_save(save_name, is_file, False, make_backup)
    print(f"DONE!")
    if not is_file:
        ts.logger("Loading all chunks from file", f"save_name: {save_name}")
        World.load_all_chunks_from_folder(show_progress_text="\tLoading world...")
        print(f"\tDeleting...", end="", flush=True)
        ts.remove_save(save_name, is_file)
        print(f"DONE!")
    else:
        print(f"\tAlready deleted because it was a file.")
    print("\tSaving...\r", end="", flush=True)
    sm.make_save(show_progress_text="\tSaving...")
    ts.logger("Save file regenerated", f"save_name: {save_name}")



# REWORK!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def main_menu():
    # action functions
    def other_options():
        # auto save
        auto_save = sfm.Toggle(Settings.auto_save, "Auto save: ")
        # logging
        logging_values = [-1, 4, 3, 2, 1, 0]
        logging_value = len(logging_values)
        for x in range(len(logging_values)):
            if logging_values[x] == Settings.logging_level:
                logging_value = x
                break
        logging_level_names = ["MINIMAL", Log_type.FATAL.name, Log_type.ERROR.name, Log_type.WARN.name, Log_type.INFO.name, "ALL"]
        logging = ts.sfm_choice_s(logging_level_names, logging_value, "Logging: ")
        other_settings = [auto_save, logging, None, sfm.UI_list(["Done"])]
        # response
        response = sfm.options_ui(other_settings, " Other options", keybinds=Settings.keybinds)
        if response is not None:
            Settings.update_auto_save(bool(auto_save.value))
            Settings.update_logging_level(logging_values[logging.value])

    def ask_options():
        ask_package_check_fail = sfm.Toggle(Settings.ask_package_check_fail, "!!!Ask on package check fail!!!: ", "YES", "no")
        ask_delete_save = sfm.Toggle(Settings.ask_delete_save, "Ask on save folder delete: ", "yes", "no")
        ask_regenerate_save = sfm.Toggle(Settings.ask_regenerate_save, "Ask on save folders regeneration: ", "yes", "no")
        # def_backup_action
        backup_action_values = [-1, 0, 1]
        backup_action_value = backup_action_values[0]
        for x in range(len(backup_action_values)):
            if backup_action_values[x] == Settings.def_backup_action:
                backup_action_value = x
                break
        backup_action__names = ["ask", "don't backup", "backup"]
        def_backup_action = ts.sfm_choice_s(backup_action__names, backup_action_value, "On save folder backup prompt: ")
        ask_settings = [ask_package_check_fail, ask_delete_save, ask_regenerate_save, def_backup_action, None, sfm.UI_list(["Done"])]
        # response
        response = sfm.options_ui(ask_settings, " Question popups", keybinds=Settings.keybinds)
        if response is not None:
            Settings.update_ask_package_check_fail(bool(ask_package_check_fail.value))
            Settings.update_ask_delete_save(bool(ask_delete_save.value))
            Settings.update_ask_regenerate_save(bool(ask_regenerate_save.value))
            Settings.update_def_backup_action(backup_action_values[def_backup_action.value])

    def set_keybind(keybind:Action_key):
        print("\n\nPress any key\n\n", end="")
        normal_keys = []
        arrow_keys = []
        key = getwch()
        if key in DOUBLE_KEYS:
            key = getwch()
            arrow_keys = [key]
        else:
            normal_keys = [key]
        keybind.set_keys(normal_keys, arrow_keys)

    def get_keybind_name(keybinds:Action_keybinds, action_type:Action_types):
        key = keybinds.get_action_key(action_type)
        return stylized_text(key.name, (Color.RED if key.conflict else Color.RESET))

    def keybind_setting():
        temp_keybinds = deepcopy(Settings.keybinds)
        while True:
            ans = sfm.UI_list_s([
            f"Escape: {get_keybind_name(temp_keybinds, Action_types.ESCAPE)}",
            f"Up: {get_keybind_name(temp_keybinds, Action_types.UP)}",
            f"Down: {get_keybind_name(temp_keybinds, Action_types.DOWN)}",
            f"Left: {get_keybind_name(temp_keybinds, Action_types.LEFT)}",
            f"Right: {get_keybind_name(temp_keybinds, Action_types.RIGHT)}",
            f"Enter: {get_keybind_name(temp_keybinds, Action_types.ENTER)}",
            None, "Done"
            ], " Keybinds", False, True).display(Settings.keybinds)
            # exit
            if ans == -1:
                break
            # done
            elif ans > 5:
                Settings.update_keybinds(temp_keybinds)
                break
            else:
                set_keybind(temp_keybinds._actions[ans])
                Settings.check_keybind_conflicts(temp_keybinds)

    files_data = sm.get_saves_data()
    in_main_menu = True
    while True:
        status:tuple[int, str|Literal[-1], bool] = (-1, -1, False)
        if in_main_menu:
            in_main_menu = False
            if len(files_data):
                mm_list = ["New save", "Load/Delete save", "Options"]
            else:
                mm_list = ["New save", "Options"]
            option = sfm.UI_list_s(mm_list, " Main menu", can_esc=True).display(Settings.keybinds)
        elif len(files_data):
            option = 1
        else:
            option = -2
            in_main_menu = True
        # new file
        if option == 0:
            status = (1, "", False)
        elif option == -1:
            break
        # load/delete
        elif option == 1 and len(files_data):
            # get data from file_data
            list_data = []
            for data in files_data:
                list_data.append(data[1])
                list_data.append(None)
            list_data.append("Regenerate all save files")
            list_data.append("Delete file")
            list_data.append("Back")
            option = sfm.UI_list_s(list_data, " Level select", True, True, exclude_nones=True).display(Settings.keybinds)
            # load
            if option != -1 and option < len(files_data):
                status = (0, files_data[int(option)][0], files_data[int(option)][2])
            # regenerate
            elif option == len(files_data):
                if not Settings.ask_regenerate_save or sfm.UI_list_s(["No", "Yes"], f" Are you sure you want to regenerate ALL save files? This will load, delete then resave EVERY save file!", can_esc=True).display(Settings.keybinds) == 1:
                    if Settings.def_backup_action == -1:
                        backup_saves = bool(sfm.UI_list_s(["Yes", "No"], f" Do you want to backup your save files before regenerating them?", can_esc=True).display(Settings.keybinds) == 0)
                    else:
                        backup_saves = bool(Settings.def_backup_action)
                    print("Regenerating save files...\n")
                    for save in files_data:
                        regenerate_save_file(save[0], save[2], backup_saves)
                    files_data = sm.get_saves_data()
                    print("\nDONE!")
            # delete
            elif option == len(files_data) + 1:
                # remove "delete file" + "regenerate save files"
                list_data.pop(len(list_data) - 2)
                list_data.pop(len(list_data) - 2)
                while len(files_data) > 0:
                    option = sfm.UI_list(list_data, " Delete mode!", DELETE_CURSOR_ICONS, True, True, exclude_nones=True).display(Settings.keybinds)
                    if option != -1 and option < (len(list_data) - 1) / 2:
                        if not Settings.ask_delete_save or sfm.UI_list_s(["No", "Yes"], f" Are you sure you want to remove Save file {files_data[option][0]}?", can_esc=True).display(Settings.keybinds):
                            ts.remove_save(files_data[option][0], files_data[option][2])
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
            sfm.UI_list(["Keybinds", "Question popups", "Other", None, "Back"], " Options", None, False, True, [keybind_setting, ask_options, other_options], True).display(Settings.keybinds)
            in_main_menu = True

        # action
        # new save
        if status[0] == 1:
            press_key(f"\nCreating new save!\n")
            new_save()
            files_data = sm.get_saves_data()
        # load
        elif status[0] == 0:
            press_key(f"\nLoading save: {status[1]}!")
            load_save(status[1], status[2])
            files_data = sm.get_saves_data()
# REWORK!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!



def main():
    # dt.decode_save_file(SETTINGS_FILE_NAME, ROOT_FOLDER, SETTINGS_SEED)
    # dt.decode_save_file("new save")
    # dt.recompile_save_file("2022-07-10;16-58-51;save2", "old_save2", BACKUPS_FOLDER_PATH, SAVES_FOLDER_PATH, OLD_BACKUP_EXT, SAVE_EXT, 2, SAVE_SEED)
    # dt.encode_save_file("file_test")
    
    # dt.load_backup_menu()
    main_menu()


def main_error_handler():
    # general crash handler (release only)

    exit_game = False
    while not exit_game:
        exit_game = True
        try:
            if GOOD_PACKAGES:
                ts.logger("Beginning new instance")
                main()
        except:
            ts.logger("Instance crashed", str(exc_info()), Log_type.FATAL)
            if ERROR_HANDLING:
                print(f"ERROR: {exc_info()[1]}")
                ans = input("Restart?(Y/N): ")
                if ans.upper() == "Y":
                    ts.logger("Restarting instance")
                    exit_game = False
            else:
                raise
        else:
            col.deinit()
            # end log
            ts.logger("Instance ended succesfuly")


if __name__ == "__main__":
    main_error_handler()
