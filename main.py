import os
import time
from datetime import datetime

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
    

def game_loop(data:list=None):
    if data == None:
        data = []
    stats(-1)
    fight_ran(7, 15)

    
def new_save(save_num=1, save_name="save*"):
    # make player
    name = input("What is your name?: ")
    if name == "":
        name = "You"
    player.name = name
    # get new save data
    new_save_data = []
    today = datetime.today()
    new_save_data.append(f"{today.year}¤{today.month}¤{today.day}¤{today.hour}¤{today.minute}¤{today.second}")
    new_save_data.append(f"{player.name}¤{player.hp}¤{player.attack}¤{player.defence}¤{player.speed}")
    new_save_data.append(ts.random_state_converter(r))
    # write new save
    try:
        f = open(f'{save_name.replace("*", str(save_num))}.sav', "w")
        f.close()
    except FileNotFoundError:
        os.mkdir("saves")
        # log
        ts.log_info("Recreating saves folder")
    sfm.encode_save(new_save_data, save_num, save_name)
    # log
    ts.log_info("Created save", f'slot number: {save_num}, player name: "{player.name}"')
    data = []
    game_loop(data)


def load_save(save_num=1, save_name="save*"):
    # read data
    datas = sfm.decode_save(save_num, save_name)
    # player
    player_data = datas[1].split("¤")
    player.name = player_data[0]
    player.hp = int(player_data[1])
    player.attack = int(player_data[2])
    player.defence = int(player_data[3])
    player.speed = float(player_data[4])
    # log
    last_accessed = datas[0].split("¤")
    ts.log_info("Loaded save", f'slot number: {save_num}, hero name: "{player.name}", last saved: {last_accessed[0]}-{last_accessed[1]}-{last_accessed[2]} {last_accessed[3]}:{last_accessed[4]}:{last_accessed[5]}')
    # load random state
    r.set_state(ts.random_state_converter(datas[2]))
    data = []
    game_loop(data)


def manage_saves(file_data, save_name="save*", save_ext="sav", can_exit=False):

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
                                datas = sfm.decode_save(file_data[option][0], save_name)
                                last_accessed = datas[0].split("¤")
                                ts.log_info("Deleted save", f'slot number: {file_data[option][0]}, hero name: "{datas[1].split("¤")[0]}", last saved: {last_accessed[0]}-{last_accessed[1]}-{last_accessed[2]} {last_accessed[3]}:{last_accessed[4]}:{last_accessed[5]}')
                                # remove
                                os.remove(f'{save_name.replace("*", str(file_data[option][0]))}.{save_ext}')
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
    # begin log
    ts.threading.current_thread().name = "Main"
    ts.log_info("Beginning new instance")

    save_location = os.path.dirname(os.path.abspath(__file__)) + "/saves"
    save_name = os.path.dirname(os.path.abspath(__file__)) + "/saves/save*"
    # ts.decode_save_file(0, "metadata")
    # ts.decode_save_file(1, save_name)

    # get save datas
    datas = sfm.file_reader(-1, dir_name=save_location)
    # process file data
    datas_processed = []
    for data in datas:
        if data[1] == -1:
            ts.log_info("Decode error", f"Slot number: {data[0]}", "ERROR")
            input(f"Save file {data[0]} is corrupted!")
        else:
            try:
                data_processed = ""
                data_processed += f"Save file {data[0]}: {data[1][1].split('¤')[0]}\n"
                last_accessed = data[1][0].split("¤")
                data_processed += f"Last opened: {last_accessed[0]}.{'0' if int(last_accessed[1]) < 10 else ''}{last_accessed[1]}.{last_accessed[2]} {last_accessed[3]}:{last_accessed[4]}:{last_accessed[5]}"
                datas_processed.append([data[0], data_processed])
            except TypeError:
                ts.log_info("Parse error", f"Slot number: {data[0]}", "ERROR")
                input(f"Save file {data[0]} could not be parsed!")
            except IndexError:
                ts.log_info("Parse error", f"Slot number: {data[0]}", "ERROR")
                input(f"Save file {data[0]} could not be parsed!")
    # manage saves
    status = manage_saves(datas_processed, save_name, "sav", True)
    # new save
    if status[0] == 1:
        input(f"\nNew game in slot {status[1]}!\n")
        # new slot?
        new_save(status[1], save_name)
    # load
    elif status[0] == 0:
        input(f"\nLoading slot {status[1]}!")
        load_save(status[1], save_name)
    
    # end log
    ts.log_info("Instance ended succesfuly")


if __name__ == "__main__":
    error_handling = False
    # ultimate error handelind (release only)
    if error_handling:
        import sys

        exit_game = False
        while not exit_game:
            try:
                main()
            except:
                print(f"ERROR: {sys.exc_info()[1]}")
                ans = input("Restart?(Y/N): ")
                if ans.upper() == "N":
                    exit_game = True
    else:
        main()
