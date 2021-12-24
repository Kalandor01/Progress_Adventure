import random
import logging
import time

# variables
game = True
# SEED
# seed = 100
seed = random.randint(-1000000, 1000000)
random.seed(seed)
r = random
name = "You"
life = r.randint(1, 6) + r.randint(1, 6) + 12
skill = r.randint(1, 6) + 6
luck = round(r.random() * 100 / 5, 1)
gold = 0
no = False
page = 1


def monster_master(m_name, m_life, m_attack, m_deff, m_speed, m_small=-2, m_big=3, m_rare=0.05, small_l=None, big_l=None, small_a=None, big_a=None, small_d=None, big_d=None, small_s=None, big_s=None):
    if small_l is None:
        small_l = m_small
    if big_l is None:
        big_l = m_big
    if small_a is None:
        small_a = m_small
    if big_a is None:
        big_a = m_big
    if small_d is None:
        small_d = m_small
    if big_d is None:
        big_d = m_big
    if small_s is None:
        small_s = m_small
    if big_s is None:
        big_s = m_big

    # stat fluctuation
    m_life += round(r.triangular(small_l, big_l))
    m_attack += round(r.triangular(small_a, big_a))
    m_deff += round(r.triangular(small_d, big_d))
    m_speed += round(r.triangular(small_s, big_s))
    # rare
    rare = False
    if r.random() < m_rare:
        rare = True
        m_name = "Rare " + m_name
        m_life *= 2
        m_attack *= 2
        m_deff *= 2
        m_speed *= 2
    # write
    return [m_name, m_life, m_attack, m_deff, m_speed, rare]


# MONSTERS
def caveman():
    return monster_master("Caveman", 7, 7, 7, 7)


def ghoul():
    return monster_master("Ghoul", 11, 9, 9, 9)


def troll():
    return monster_master("Troll", 13, 11, 11, 5)


def fight_ran(num=1, cost=1, power_min=1, power_max=-1, round_up=True):
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
            monster_cost = r.randint(power_min, costnum)
        else:
            monster_cost = cost
        # cost adjustment
        if monster_cost < power_min:
            monster_cost = power_min
        if power_max != -1 and monster_cost > power_max:
            monster_cost = power_max

        # monster choice
        if monster_cost >= 3:
            monster_n = r.randint(0, 0)
            match monster_n:
                case 0:
                    monster = troll()
            cost -= 3
        elif monster_cost >= 2:
            monster_n = r.randint(0, 0)
            match monster_n:
                case 0:
                    monster = ghoul()
            cost -= 2
        else:
            monster_n = r.randint(0, 0)
            match monster_n:
                case 0:
                    monster = caveman()
            cost -= 1
        num -= 1
        monsters.append(monster)
    print("Random enemy maker:")
    fight(monsters)


def fight(monster_l=[["test", 1, 1, 1, 1, False]]):
    # name, life, skill
    global name, life, skill, luck
    # variables
    szum = 0
    for m in monster_l:
        szum += 1
        if m is None:
            monster_l = [["test", 1, 1, 1, 1, False]]
            break
    attacking_m = ""
    # enemys
    print("\nEnemys:")
    for m in monster_l:
        print(f"\n{m[0]}\nHP: {m[1]}\nAttack: {m[2]}\nDefence: {m[3]}\nSpeed: {m[4]}")
    print()
    while life > 0 and szum > 0:
        for m in monster_l:
            if m[1] > 0:
                attack = r.randint(1, 6) + skill
                attack_e = r.randint(1, 6) + m[2]
                # clash
                if attack == attack_e:
                    print("\nCLASH!")
                # damage
                elif attack < attack_e:
                    print(f"\n{m[0]} attacked {name}: ", end="")
                    if r.random() * 100 > luck:
                        life -= 2
                        if life < 0:
                            life = 0
                        print(f"-2 HP({life})")
                        if life <= 0:
                            attacking_m = m[0]
                            break
                    else:
                        print("BLOCKED!")
                # attack
                else:
                    print(f"\n{name} attacked {m[0]}: ", end="")
                    if r.random() * 100 > luck:
                        m[1] -= 2
                        if m[1] < 0:
                            m[1] = 0
                        print(f"-2 HP({m[1]})")
                    else:
                        m[1] -= 4
                        if m[1] < 0:
                            m[1] = 0
                        print(f"CRITICAL HIT: -4 HP({m[1]})")
                    if m[1] <= 0:
                        print(f"{name} defeated {m[0]}")
                time.sleep(0.5)
        # sum life
        szum = 0
        for m in monster_l:
            if m[1] > 0:
                szum += 1
    # outcome
    if life <= 0:
        life = 0
        print(f"\n{attacking_m} defeated {name}!")
        stats()
    else:
        monsters_n = ""
        for x in range(len(monster_l)):
            monsters_n += monster_l[x][0]
            if len(monster_l) - 2 == x:
                monsters_n += " and "
            elif len(monster_l) - 2 > x:
                monsters_n += ", "
        print(f"\n{name} defeated {monsters_n}!\n")


# stats
def stats(won=0):
    global game
    if won == 1:
        print("\nYou Win!!!")
    elif won == 0:
        print("\nYou lost!!!")
    print(f"\nName: {name}\n\nSTATS:")
    if won != 0:
        print(f"HP: {life}")
    print(f"Skill: {skill}\nLuck: {luck}%\n")
    if 0 <= won <= 1:
        print(f"OTHER:\nGold: {gold}")
        game = False


fight_ran(7, 15)


# + extra: full heal...
def modify(stat, value, write=True):
    global life, skill, luck, gold
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


# pages
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
            fight([["Caveman", 7, 7]])
            stats(1)
        case _:
            no = True
            logging.warning("Wrong page number!!!")


# main
"""
    
    olalak:
    1   -> 3, 6 -> 3
    2   -> 5, 8
    3   -> 2, 7
    4   -> vége
    5   -> vége
    7   -> 4, 9
    8   -> vége
    9   -> fight

igazi könyvekben nem így van a fight?
"""


def page_turning():
    global game, seed, name, life, skill, luck, gold, no, page
    page_old = page
    try:
        page = int(input("\nWhich page do you want to go to?: "))
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


def main():
    global game, name
    name = input("What is your name?: ")
    if name == "":
        name = "You"
    stats(-1)
    print("Kezdés:\nEgy versenyre nevezel, aminek a lényege, hogy át kell kelni a halállabirintuson. A labirintusban tárgyakat találhatsz és szörnyekkel kell harcoljál.")
    print("\nMiután öt percet haladtál lassan az alagútban, egy kőasztalhoz érsz, amely a bal oldali fal mellett áll. Hat doboz van rajta, egyikükre a te neved festették.\n1: Ha kiakarod nyitni a dobozt.\n2: Ha inkább tovább haladsz észak felé.")
    while game:
        page_turning()


if __name__ == "__main__":
    main()
