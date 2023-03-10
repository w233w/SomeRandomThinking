import random
import time
import _thread as thread


class game_obj:
    '''
    A simple game sprite
    name, hp, atk: you know the meaning.
    arrR: attack rate; how many attacks can this object do in one second
    critC, critical chance; critC = 0.3 meaning 30% chance
    critD: critical damage; cridD = 0.5 meaning extra 50% damage when crit.
    '''

    def __init__(self, name, hp, atk, attR, critC, critD):
        self.name = name
        self.hp = hp
        self.atk = atk
        self.attR = attR
        self.critP = critC
        self.critD = critD

    def __bool__(self) -> bool:
        return self.is_survive()

    def _type_one_RNG(self, rng_ratio) -> bool:
        return random.random() < rng_ratio

    def _cal_damage(self) -> int:
        crit = self._type_one_RNG(self.critC)
        if crit:
            DMG = self.atk * (1 + self.critD)
        else:
            DMG = self.atk
        return int(DMG)

    def is_survive(self) -> bool:
        return self.hp > 0

    def get_hit(self, DMG_income) -> None:
        self.hp -= DMG_income
        if self.hp <= 0:
            self.hp = 0

    def attack(self, oppo) -> None:
        '''simgle attack peocess with some log.
        '''
        DMG = self._cal_damage()
        oppo.get_hit(DMG)
        if oppo:
            print(f'{self.name} deal {DMG} damage to {oppo.name}. {oppo.name} has {oppo.hp} hp remain.\n', end='')
        else:
            print(f'{self.name} deal {DMG} damage to {oppo.name}. {oppo.name} is dead.\n', end='')

    def fight(self, oppo) -> None:
        '''keep attack an opponent with time interval (1 / attR) until any sprite die.
        '''
        if not isinstance(oppo, self.__class__):
            raise TypeError('Target is not attackable')
        while self and oppo:
            self.attack(oppo)
            time.sleep(1/self.attR)


player = game_obj('player', 8000, 200, 5, 0.3, 2.5)
mob = game_obj('dragon', 12000, 800, 1, 0.5, 1)
group = [player, mob]


# Create two threads
try:
    thread.start_new_thread(player.fight, (mob,))
    thread.start_new_thread(mob.fight, (player,))
except Exception:
    print(Exception.with_traceback())

# This will keep program run until the fight end.
while all(group):
    pass
