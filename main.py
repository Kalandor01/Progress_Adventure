import logging
import os
import numpy as np
import sys
import time
from datetime import datetime

import random_sentance as rs
import save_file_manager as sfm

import classes as cl


def imput(ask="Num: ", type=int):
    """
    Only returns int/float.
    """
    while True:
        try: return type(input(ask))
        except ValueError: print(f'Not{" whole" if type == int else ""} number!')

# variables
game = True
# SEED
r_seed = np.random.RandomState()
seed = r_seed.randint(0, 1000000000)
r = np.random.RandomState(seed)

player = cl.Player()
# name = "You"
# life = r.randint(1, 6) + r.randint(1, 6) + 12
# skill = r.randint(1, 6) + 6
# luck = round(r.random() * 100 / 5, 1)
gold = 0
no = False
page = 1


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
def fight(monster_l=None):
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
        print(f"OTHER:\nGold: {gold}")


# + extra: full heal...                     DEPRECATED?
def modify(stat, value=0, write=True):
    global life, gold
    match stat:
        case "life":
            life += value
            if write:
                print(f"HP: {life}")
        case "skill":
            skill += value
            if write:
                print(f"Skill: {skill}")
        case "luck":
            luck += value
            if write:
                print(f"Luck: {luck}")
        case "gold":
            gold += value
            if write:
                print(f"Gold: {gold}")
        case _:
            logging.warning(f"{stat} is not a valid stat!!!")


# pages                                     DEPRECATED
def pages(p):
    global page, life, gold, no
    page = p
    match page:
        case 2:
            print("\nLátod, hogy az akadály egy széles, barna, sziklaszerű tárgy. Megérinted, és meglepve tapasztalod, hogy lágy, szivacsszerű.\n1: Ha át szeretnél mászni rajta.\n2: Ha ketté akarod vágni a kardoddal.")
            page = 2
        case 3:
            print("\nNéhány perc gyaloglás után egy elágazáshoz érsz az alagútban. Egy, a falra festett fehér nyíl nyugatfelé mutat. A földön nedves lábnyomok jelzik, merre haladtak az előtted járók. Nehéz biztosan megmondani, de úgy tűnik, hogy három közülük a nyíl irányába halad, míg egyikük úgy döntött, hogy klifenek megy.\n1: Ha nyugat felé kívánsz menni.\n2: Ha keletnek.")
            page = 3
        case 4:
            print("\nAhogy végigmész az alagúton, csodálkozva látod, hogy egy jókora vasharang csüng alá a boltozatról.")
            stats()
        case 5:
            print("\nKardod könnyedén áthatol a spóragolyó vékonykülső burkán. Sűrű barna spórafelhő csap ki a golyóból, és körülvesz. Némelyik spóra a bőrödhöz tapad, és rettenetes viszketést okoz. Nagy daganatok nőnek az arcodon és karodon, és a bőröd mintha égne. 2 ÉLETERŐ pontot veszítesz. Vadul vakarózva átléped a leeresztett golyót, és klifenek veszed az utad.")
            modify("life", -2)
            stats()
        case 6:
            print("\nA doboz teteje könnyedén nyílik. Benne két aranypénzt találsz, és egy üzenetet, amely egy kis pergamenen neked szól. Előbb zsebre vágod az aranyakat, aztán elolvasod az üzenetet: - „Jól tetted. Legalább volt annyi eszed, hogy megállj és elfogadd az ajándékot. Most azt tanácsolom neked, hogy keress és használj különféle tárgyakat, ha sikerrel akarsz áthaladni Halállabirintusomon.” Az aláírás Szukumvit. Megjegyzed a tanácsot, apródarabokra téped a pergament, és tovább mész észak felé.")
            modify("gold", 2)
            page = 6
            pages(3)
        case 7:
            print("\nA három pár nedves lábnyomot követve az alagút nyugati elágazásában hamarosan egy újabb elágazáshoz érsz.\n1: Ha továbbmész nyugat felé a lábnyomokat követve.\n2: Ha inkább észak felé mész a harmadik pár lábnyom után.")
            page = 7
        case 8:
            print("\nFölmászol a lágy sziklára, attól tartasz, hogy bár-melyik pillanatban elnyelhet. Nehéz átvergődni rajta, mert puha anyagában alig tudod a lábadat emelni, de végül átvergődsz rajta. Megkönnyebbülten érsz újra szilárd talajra, és fordulsz klife felé.")
            stats()
        case 9:
            print("\nHallod, hogy elölről súlyos lépések közelednek. Egy széles, állatbőrökbe öltözött, kőbaltás, primitívlény lép elő. Ahogy meglát, morog, a földre köp, majd a kőbaltát felemelve közeledik, és mindennek kinéz, csak barátságosnak nem. Előhúzod kardodat, és felkészülsz, hogy megküzdj a Barlangi Emberrel.")
            fight([cl.Caveman()])
            stats(1)
        case _:
            no = True
            logging.warning("Wrong page number!!!")


# page choice                                   DEPRECATED
def page_turning():
    global game, seed, name, life, gold, no, page
    page_old = page
    try:
        page = int(imput("\nWhich page do you want to go to?: "))
    except ValueError:
        page = -1
    if page == 1:
        match page_old:
            case 1:
                pages(6)
            case 2:
                pages(8)
            case 3:
                pages(7)
            case 7:
                pages(4)
            case _:
                no = True
    elif page == 2:
        match page_old:
            case 1:
                pages(3)
            case 2:
                pages(5)
            case 3:
                pages(2)
            case 7:
                pages(9)
            case _:
                no = True
    else:
        no = True
    # wrong
    if no:
        print("Wrong page number!")
        page = page_old
        no = False
    

def game_loop(data=None):
    if data == None:
        data = []
    fight_ran(7, 15)

    
def new_save(save_num=1, save_name="save*"):
    new_save_data = []
    # get new save data
    global game, name
    name = input("What is your name?: ")
    if name == "":
        name = "You"
    player.name = name
    stats(-1)
    today = datetime.today()
    new_save_data.append(f"{today.year}, {today.month}, {today.day}, {today.hour}, {today.minute}, {today.second}")
    new_save_data.append(f"{player.name}, {player.hp}, {player.attack}, {player.defence}, {player.speed}")
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
    data = []
    game_loop(data)


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
    max_saves = 5

    options_status = True
    while options_status:
        # get save datas
        datas = sfm.file_reader(max_saves, save_name=save_name)
        # write id data
        for data in datas:
            print(f"Save file {data[0]}: {data[1][1].split(', ')[0]}")
            last_acces = data[1][0].split(", ")
            print(f"Last opened: {last_acces[0]}.{'0' if int(last_acces[1]) < 10 else ''}{last_acces[1]}.{last_acces[2]} {last_acces[3]}:{last_acces[4]}:{last_acces[5]}\n")
        # manage saves
        status = sfm.manage_saves(datas, max_saves, save_name)
        if status[0] == 1 or status[0] == 0:
            options_status = False
        else:
            print(f"Deleted save in slot {status[1]}!")
    if status[0] == 1:
        input(f"New game in slot {status[1]}!")
        new_save(status[1], save_name)
    elif status[0] == 0:
        input(f"Loading slot {status[1]}!")
        load_save(status[1], save_name)


if __name__ == "__main__":
    error_handling = False
    # ultimate error handlind (release only)
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
