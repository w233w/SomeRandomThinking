# Escape of the dead minigame
import random
import time
from IPython.display import clear_output


def validation(func):
    def warpper(*args, **kwargs):
        while True:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(e)
    return warpper


class Game:
    def __init__(self, diff=0):
        self.diff = diff
        self.lawn = 0
        self.barricade = 10 - self.diff
        self.garage = 10
        self.zombies = 0
        self.zombies_come = True
        self.action = []

    def reset(self, diff=0):
        self.lawn = 0
        self.barricade = 10 - self.diff
        self.garage = 10
        self.zombies = 0
        self.action = []

    def event_zombie_income(self):
        if self.zombies_come is False:
            self.zombies_come = True
            return
        if 10 <= self.garage < 40:
            self.zombies += 1
        elif 40 <= self.garage < 60:
            self.zombies += 2
        elif 60 <= self.garage < 90:
            self.zombies += 3
        elif 90 <= self.garage < 100:
            self.zombies += 4
        else:
            raise ValueError('Impossible garage value.')

    @validation
    def event_make_action(self):
        l, b, g = input().split(' ')
        l, b, g = int(l), int(b), int(g)
        if l + b + g == 4:
            self.action = [l, b, g]
        else:
            raise ValueError('Total actions must be 4.')

    def event_on_action(self):
        l, b, g = self.action
        for _ in range(l):
            # roll a dice, if hit [3,4,5,6] then pass, else fail.
            # pass check will kill 1 zombie.
            # for every zombie killed, player gain 1 lawn.
            if random.choice(range(1, 7)) in range(3, 7):
                if self.zombies >= 1:
                    self.lawn += 1
                    self.zombies -= 1
        for _ in range(b):
            if random.choice(range(1, 7)) in range(3, 7):
                self.barricade += 1
                if self.barricade > 10 - self.diff:
                    self.barricade = 10 - self.diff
        for _ in range(g):
            if random.choice(range(1, 7)) in range(5, 7):
                self.garage += 10

    def event_zombies_attack(self):
        self.barricade -= self.zombies

    @validation
    def event_make_reward_decision(self):
        if self.lawn < 10:
            return
        else:
            print('Enter 1 to get reward\nEnter 0 to skip.')
            decision = input()
            if decision == '1':
                self.lawn = 0
                self.do_reward()
            elif decision == '0':
                return
            else:
                raise ValueError('input must be 1 or 0')

    @validation
    def do_reward(self):
        option = input()
        if option == '1':
            self.zombies = 0
        elif option == '2':
            self.garage += 10
        elif option == '3':
            self.zombies_come = False
        elif option == '4':
            self.barricade += 3
            if self.barricade > 10 - self.diff:
                self.barricade = 10 - self.diff
        else:
            raise ValueError('input must be in the [1, 2, 3, 4]')

    def show_state(self):
        clear_output(wait=True)
        print(f'Zombies: {self.zombies}')
        print(f'Lawn: {self.lawn}')
        print(f'HP: {self.barricade}')
        print(f'Process: {self.garage}')
        time.sleep(1)

    def run(self):
        self.reset()
        while self.barricade > 0:
            if self.garage >= 100:
                return 'win'
            self.event_zombie_income()
            self.show_state()
            self.event_make_action()
            self.event_on_action()
            self.show_state()
            self.event_zombies_attack()
            self.show_state()
            self.event_make_reward_decision()
            self.show_state()
        return 'lose'


if __name__ == '__main__':
    Game().run()
