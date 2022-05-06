import os
import time
from datetime import datetime
import json

import save_file_manager as sfm

from tools import r
import tools as ts
import classes as cl


def imput(ask="Num: ", type=int):
    """
    Only returns int/float.
    """
    while True:
        try: return type(input(ask))
        except ValueError: print(f'Not{" whole" if type == int else ""} number!')


# dummy player for global
player = cl.Player()


# Monster cheat sheet: name, life, attack, deff, speed, rare, team, switched
def fight_ran(num=1, cost=1, power_min=1, power_max=-1, round_up=True):
    global player
    monsters = []
    monster = None
    for x in range(num):
        # max cost calculation
        costnum = round(cost / num)
        if round_up and 0 < ((cost / num) % 1) <= 0.5:
            costnum += 1
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
    

def game_loop(data=None):
    if data == None:
        data = {}
    stats(-1)
    fight_ran(7, 15)

    
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
        f = open(f'{SAVE_NAME.replace("*", str(save_num))}.sav', "w")
        f.close()
    except FileNotFoundError:
        os.mkdir("saves")
        # log
        ts.log_info("Recreating saves folder")
    sfm.encode_save([json.dumps(new_display_data), json.dumps(new_save_data)], save_num, SAVE_NAME, SAVE_EXT)
    # log
    ts.log_info("Created save", f'slot number: {save_num}, player name: "{player.name}"')
    game_loop(new_save_data)

# json_j = json.loads(sfm.decode_save()[0])

def load_save(save_num=1):
    # read data
    datas = json.loads(sfm.decode_save(save_num, SAVE_NAME, SAVE_EXT)[1])
    # player
    player_data = datas["player"]
    player.name = player_data["name"]
    player.hp = int(player_data["hp"])
    player.attack = int(player_data["attack"])
    player.defence = int(player_data["defence"])
    player.speed = float(player_data["speed"])
    # log
    last_accessed = datas["last_access"]
    ts.log_info("Loaded save", f'slot number: {save_num}, hero name: "{player.name}", last saved: {ts.make_date(last_accessed)} {ts.make_time(last_accessed[3:])}')
    # load random state
    r.set_state(ts.random_state_converter(datas["seed"]))
    data = []
    game_loop(data)


def manage_saves(file_data, can_exit=False):

    in_main_menu = True
    while True:
        if len(file_data):
            if in_main_menu:
                in_main_menu = False
                option = sfm.UI_list(["New save", "Load/Delete save"], " Main menu", can_esc=can_exit).display()
            else:
                option = 1
            # new file
            if option == 0:
                new_slot = 1
                for data in file_data:
                    if data[0] == new_slot:
                        new_slot += 1
                return [1, new_slot]
            elif option == -1:
                return [-1, -1]
            # load/delete
            else:
                # get data from file_data
                list_data = []
                for data in file_data:
                    list_data.append(data[1])
                    list_data.append(None)
                list_data.append("Delete file")
                list_data.append("Back")
                option = sfm.UI_list(list_data, " Level select", multiline=True, can_esc=True).display()
                # load
                if option != -1 and option / 2 < len(file_data):
                    return [0, file_data[int(option / 2)][0]]
                # delete
                elif option / 2 == len(file_data):
                    list_data.pop(len(list_data) - 2)
                    delete_mode = True
                    while delete_mode and len(file_data) > 0:
                        option = sfm.UI_list(list_data, " Delete mode!", "X ", "  ", multiline=True, can_esc=True).display()
                        if option != -1 and option != len(list_data) - 1:
                            option = int(option / 2)
                            if sfm.UI_list(["No", "Yes"], f" Are you sure you want to remove Save file {file_data[option][0]}?", can_esc=True).display():
                                # log
                                datas = json.loads(sfm.decode_save(file_data[option][0], SAVE_NAME, SAVE_EXT, decode_until=1)[0])
                                last_accessed = datas["last_access"]
                                ts.log_info("Deleted save", f'slot number: {file_data[option][0]}, hero name: "{datas["player_name"]}", last saved: {ts.make_date(last_accessed)} {ts.make_time(last_accessed[3:])}')
                                # remove
                                os.remove(f'{SAVE_NAME.replace("*", str(file_data[option][0]))}.{SAVE_EXT}')
                                list_data.pop(option * 2)
                                list_data.pop(option * 2)
                                file_data.pop(option)
                        else:
                            delete_mode = False
                # back
                else:
                    in_main_menu = True
        else:
            input(f"\n No save files detected!")
            return [1, 1]



def main():
    # ts.decode_save_file(0, "metadata")
    # ts.decode_save_file(1, SAVE_NAME)

    # get save datas
    try:
        f = open(f'{SAVE_NAME.replace("*", str(0))}.sav', "w")
        f.close()
        os.remove(f'{SAVE_NAME.replace("*", str(0))}.sav')
    except FileNotFoundError:
        os.mkdir("saves")
        # log
        ts.log_info("Recreating saves folder")
    datas = sfm.file_reader(-1, dir_name=SAVE_LOCATION, decode_until=1)
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
    # manage saves
    status = manage_saves(datas_processed, True)
    # new save
    if status[0] == 1:
        input(f"\nNew game in slot {status[1]}!\n")
        # new slot?
        new_save(status[1])
    # load
    elif status[0] == 0:
        input(f"\nLoading slot {status[1]}!")
        load_save(status[1])


# constants
SAVE_LOCATION = os.path.dirname(os.path.abspath(__file__)) + "/saves"
SAVE_NAME = os.path.dirname(os.path.abspath(__file__)) + "/saves/save*"
SAVE_EXT = "sav"

if __name__ == "__main__":
    import sys

    # ultimate error handlind (release only)
    error_handling = False

    # begin log
    ts.threading.current_thread().name = "Main"
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
