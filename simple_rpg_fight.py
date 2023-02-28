import random
import time
import _thread as thread


class obj:
    def __init__(self, name, hp, atk, attR, critP, critD):
        self.name = name
        self.hp = hp
        self.atk = atk
        self.attR = attR
        self.critP = critP
        self.critD = critD

    def __bool__(self):
        return self.is_survive()

    def is_survive(self):
        return self.hp > 0

    def _type_one_RNG(self, rng) -> bool:
        return random.random() < rng

    def get_hit(self, DMG_income):
        self.hp -= DMG_income
        if self.hp <= 0:
            self.hp = 0

    def attack(self, oppo) -> None:
        crit = self._type_one_RNG(self.critP)
        if crit:
            DMG = self.atk * (1 + self.critD)
        else:
            DMG = self.atk
        DMG = int(DMG)
        oppo.get_hit(DMG)
        if oppo:
            print(f'{self.name} deal {DMG} damage to {oppo.name}. {oppo.name} has {oppo.hp} hp remain.\n', end='')
        else:
            print(f'{self.name} deal {DMG} damage to {oppo.name}. {oppo.name} is dead.\n', end='')

    def battle(self, oppo) -> None:
        if not isinstance(oppo, obj):
            raise TypeError('Target is not attackable')
        while self and oppo:
            self.attack(oppo)
            time.sleep(1/self.attR)


player = obj('player', 8000, 200, 5, 0.3, 2.5)
mob = obj('dragon', 12000, 800, 1, 0.5, 1)
group = [player, mob]


# 创建两个线程
try:
    thread.start_new_thread(player.battle, (mob,))
    thread.start_new_thread(mob.battle, (player,))
except Exception:
    print(Exception.with_traceback())
