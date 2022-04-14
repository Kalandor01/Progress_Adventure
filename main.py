import logging
import os
import numpy as np
import sys
import time
from datetime import datetime

import random_sentance as rs
import save_file_manager as sfm

import classes as cl
from classes import r


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
    fight_ran(7, 15)

    
def new_save(save_num=1, save_name="save*"):
    # make player
    # cl.r.set_state(r.get_state())
    print(r.get_state())
    name = input("What is your name?: ")
    if name == "":
        name = "You"
    player.name = name
    stats(-1)
    # get new save data
    new_save_data = []
    today = datetime.today()
    new_save_data.append(f"{today.year}, {today.month}, {today.day}, {today.hour}, {today.minute}, {today.second}")
    new_save_data.append(f"{player.name}, {player.hp}, {player.attack}, {player.defence}, {player.speed}")
    new_save_data.append(random_state_converter(r))
    # write new save
    sfm.encode_save(new_save_data, save_num, save_name)
    data = []
    game_loop(data)


def load_save(save_num=1, save_name="save*"):
    # read data
    datas = sfm.decode_save(save_num, save_name)
    # last access
    last_acces = datas[0].split(", ")
    print(f"\nLast opened: {last_acces[0]}.{'0' if int(last_acces[1]) < 10 else ''}{last_acces[1]}.{last_acces[2]} {last_acces[3]}:{last_acces[4]}:{last_acces[5]}")
    # player
    player_data = datas[1].split(", ")
    player.name = player_data[0]
    player.hp = int(player_data[1])
    player.attack = int(player_data[2])
    player.defence = int(player_data[3])
    player.speed = float(player_data[4])
    stats(-1)
    r.set_state(random_state_converter(datas[2]))
    print(r.get_state())
    data = []
    game_loop(data)


def manage_saves(file_data, max_saves=5, save_name="save*", save_ext="sav", can_exit=False):
    from os import remove

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
                                remove(f'{save_name.replace("*", str(file_data[option][0]))}.{save_ext}')
                                if option == len(file_data) - 1:
                                    max_saves -= 1
                                    metadata_manager(0, max_saves)
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


def metadata_manager(line_num:int, write_value=None):
    """
    STRUCTURE:\n
    0 = max_saves
    """
    # default values
    max_saves = 5
    try:
        metadata = sfm.decode_save(0, "metadata")
    except FileNotFoundError:
        metadata = [max_saves]
        sfm.encode_save(metadata, 0, "metadata")
    # formating
    metadata[0] = int(metadata[0])
    if write_value == None:
        return metadata[line_num]
    else:
        metadata[line_num] = write_value
        sfm.encode_save(metadata, 0, "metadata")


def random_state_converter(random_state:np.random.RandomState | tuple | str):
    """
    Can convert a numpy RandomState.getstate() into an easily storable string and back.
    """
    if type(random_state) == str:
        lines = random_state.split(";")
        states = [int(num) for num in lines[1].split("|")]
        return (str(lines[0]), np.array(states, dtype=np.uint32), int(lines[2]), int(lines[3]), float(lines[4]))
    else:
        if type(random_state) == tuple:
            state = random_state
        else:
            state = random_state.get_state()
        state_txt = state[0] + ";"
        for num in state[1]:
            state_txt += str(num) + "|"
        return f"{state_txt[:-1]};{str(state[2])};{str(state[3])};{str(state[4])}"


def decode_save_file(save_num=1, save_name="save*", save_ext="sav"):
    save_data = sfm.decode_save(save_num, save_name, save_ext)
    f = open(f'{save_name.replace("*", str(save_num))}.decoded.txt', "w")
    for line in save_data:
        f.write(line + "\n")
    f.close()

decode_save_file()

def main():
    """
    global game, name
    name = input("What is your name?: ")
    if name == "":
        name = "You"
    stats(-1)
    print("Kezdés:\nEgy versenyre nevezel, aminek a lényege, hogy át kell kelni a halállabirintuson. A labirintusban tárgyakat találhatsz és szörnyekkel kell harcoljál.")
    print("\nMiután öt percet haladtál lassan az alagútban, egy kőasztalhoz érsz, amely a bal oldali fal mellett áll. Hat doboz van rajta, egyikükre a te neved festették.\n1: Ha kiakarod nyitni a dobozt.\n2: Ha inkább tovább haladsz észak felé.")
    while game:
        page_turning()
    """

    save_name = os.path.dirname(os.path.abspath(__file__)) + "/save*"

    # get max saves
    max_saves = metadata_manager(0)

    # get save datas
    datas = sfm.file_reader(max_saves, save_name=save_name)
    # write id data
    datas_processed = []
    for data in datas:
        data_processed = ""
        data_processed += f"Save file {data[0]}: {data[1][1].split(', ')[0]}\n"
        last_acces = data[1][0].split(", ")
        data_processed += f"Last opened: {last_acces[0]}.{'0' if int(last_acces[1]) < 10 else ''}{last_acces[1]}.{last_acces[2]} {last_acces[3]}:{last_acces[4]}:{last_acces[5]}"
        datas_processed.append([data[0], data_processed])
    # manage saves
    status = manage_saves(datas_processed, max_saves, save_name, "sav", True)
    # new save
    if status[0] == 1:
        input(f"\nNew game in slot {status[1]}!")
        # new slot?
        if status[1] > max_saves:
            max_saves += 1
            metadata_manager(0, max_saves)
        new_save(status[1], save_name)
    # load
    elif status[0] == 0:
        input(f"\nLoading slot {status[1]}!")
        load_save(status[1], save_name)

# print(cl.Player())

if __name__ == "__main__":
    error_handling = False
    # ultimate error handelind (release only)
    if error_handling:
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
