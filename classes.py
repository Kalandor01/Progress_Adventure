import numpy as np
r = np.random.RandomState()


def entity_master(name, life, attack, deff, speed, d_small=-2, d_big=3, c_rare=0.05, team=1, c_team_change=0.005, small_l=None, big_l=None, small_a=None, big_a=None, small_d=None, big_d=None, small_s=None, big_s=None):
    if small_l is None:
        small_l = d_small
    if big_l is None:
        big_l = d_big
    if small_a is None:
        small_a = d_small
    if big_a is None:
        big_a = d_big
    if small_d is None:
        small_d = d_small
    if big_d is None:
        big_d = d_big
    if small_s is None:
        small_s = d_small
    if big_s is None:
        big_s = d_big

    # stat fluctuation
    life += round(r.triangular(small_l, (small_l + big_l) / 2, big_l))
    attack += round(r.triangular(small_a, (small_a + big_a) / 2, big_a))
    deff += round(r.triangular(small_d, (small_d + big_d) / 2, big_d))
    speed += round(r.triangular(small_s, (small_s + big_s) / 2, big_s))
    # rare
    rare = False
    if r.random() < c_rare:
        rare = True
        name = "Rare " + name
        life *= 2
        attack *= 2
        deff *= 2
        speed *= 2
    # team
    switched = False
    if r.random() < c_team_change:
        team = 0
        switched = True
    # write
    return [name, life, attack, deff, speed, rare, team, switched]


class Entity:
    def __init__ (self, traits=entity_master("test", 1, 1, 1, 1)):
        self.name = traits[0]
        self.hp = traits[1]
        self.attack = traits[2]
        self.defence = traits[3]
        self.speed = traits[4]
        self.rare = traits[5]
        self.team = traits[6]
        self.switched = traits[7]


    def attack_entity(self, target):
        target.hp -= self.attack


class Player(Entity):
    def __init__(self):
        self.name = "You"
        self.hp = r.randint(1, 7) + r.randint(1, 7) + 12
        self.attack = r.randint(1, 7) + 6
        self.defence = r.randint(1, 7) + 6
        self.speed = round(r.random() * 100 / 5, 1)
        self.rare = False
        self.team = 0
        self.switched = False


class Caveman(Entity):
    def __init__(self):
        super().__init__(entity_master(__class__.__name__, 7, 7, 7, 7))


class Ghoul(Entity):
    def __init__(self):
        super().__init__(entity_master(__class__.__name__, 11, 9, 9, 9))


class Troll(Entity):
    def __init__(self):
        super().__init__(entity_master(__class__.__name__, 13, 11, 11, 5))


class Test(Entity):
    def __init__(self):
        super().__init__()
