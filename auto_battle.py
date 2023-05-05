import random

#对游戏：《女娲捏人》的简单模仿，本质上就是一个自动打怪升级的游戏
#这里仅仅是他的简单实现，事件，升级等都是TODO

class Utils:
    @staticmethod
    def check_happen(chance):
        return random.randint(1, 100) <= 100 * chance

class P:
    def __init__(self):
        self.h = 200
        self.maxh = 200
        self.eng = 50
        self.atk = 5
        self.critc = 0.05
        self.critd = 0.2
        self.defs = 0.0
        self.dodge = 0.1
        self.oneshot = 0.0
        self.regen = 5
        self.hitregen = 0
        self.gold = 0
        self.exp = 0
        self.level = 1
        self.buff = {}

    def __bool__(self):
        return not self.die()

    def die(self):
        return self.h < 0

    def hregen(self, amount):
        self.h += amount
        if self.h > self.maxh:
            self.h = self.maxh

    def on_hit(self, dmg_income):
        if Utils.check_happen(self.dodge):
            return
        self.h -= dmg_income * (1 - self.defs)

    def deal_reward(self, reward):
        self.gold += reward['g']
        self.exp += reward['e']
        if self.exp >= 100 * self.level:
            self.exp -= 100 * self.level
            self.level += 1

    def action(self):
        if Utils.check_happen(self.oneshot):
            return 99999
        if Utils.check_happen(self.critc):
            return self.atk * (1 + self.critd) * (1 + 0.05 * self.level)
        return self.atk

class E:
    def __init__(self, diff, level):
        self.h = int((40 + 1 * diff) * (1.03 ** level))
        self.atk = int((3 + 0.3 * diff) * (1.03 ** level))
        self.reward = {'g':3, 'e':1}

    def __repr__(self):
        return f'{self.h}, {self.atk}'

    def __bool__(self):
        return not self.die()

    def die(self):
        return self.h < 0
    
    def action(self):
        return self.atk

class G:
    def __init__(self):
        self.diff = 1
        self.level = 1
        self.modify = []
        self.p = P()
        self.enemy_rate = 0.6

    def round(self):
        self.level += 1
        events = []
        for i in range(3):
            if Utils.check_happen(self.enemy_rate):
                events.append(E(self.diff, self.level))
            else:
                events.append(None)
        for e in events:
            if isinstance(e, E):
                while e:
                    e.h -= self.p.action()
                    if not e:
                        break
                    self.p.on_hit(e.action())
                self.p.deal_reward(e.reward)
                self.p.hregen(self.p.regen)
            else:
                self.p.atk += 1
                self.p.h += 10
                self.p.maxh += 10

    def run(self):
        while self.p:
            self.round()

if __name__ == '__main__':
    game = G()
    game.run()
    print('Finished at: Level', game.level)
