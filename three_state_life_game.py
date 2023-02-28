# 仅限notebook使用
# 以及可以玩了，不过参数还得调调
from itertools import product
from IPython.display import clear_output
import random
import time


class map_tile:
    '''三状态的生命游戏,每个tile都是一个状态机
    '''

    def __init__(self, x, y, level=0) -> None:
        self.x = x
        self.y = y
        self.loc = (x, y)
        self.level = level
        self.temp_level = level

    def _visit_8_neighbor(self) -> int:
        counter = 0
        for del_x, del_y in product([-1, 0, 1], [-1, 0, 1]):
            loc = (self.x + del_x, self.y + del_y)
            if del_x == del_y == 0:
                continue
            if loc in map_obj:
                counter += map_obj[loc].level >= 1
        return counter

    def update(self) -> None:
        n = self._visit_8_neighbor()
        if self.level == 0:
            if n < 3:
                self.temp_level = 1
            elif n < 4:
                self.temp_level = 2
        if self.level == 1:
            if n < 3:
                self.temp_level = 2
            elif n > 4:
                self.temp_level = 0
        if self.level == 2:
            if n > 4:
                self.temp_level = 0
            elif n > 3:
                self.temp_level = 1

        # 设置边界条件
        if self.temp_level < 0:
            self.temp_level = 0
        if self.temp_level > 3:
            self.temp_level = 3

    def next_state(self) -> None:
        self.level = self.temp_level


visual = {
    0: '\u00a0',
    1: '\u25a1',
    2: '\u25a0',
}

if __name__ == '__main__':
    range_low, range_high = -10, 10
    game_round = 50

    map_obj = {}
    for i in range(range_low, range_high):
        for j in range(range_low, range_high):
            map_obj[(i, j)] = map_tile(i, j, random.choices([0, 1, 2], weights=(60, 20, 20))[0])

    for _ in range(game_round):
        for i in range(range_low, range_high):
            for j in range(range_low, range_high):
                try:
                    print(visual[map_obj[(i, j)].level], end='')
                except Exception:
                    print(visual[0], end='')
            print()

        for tile in map_obj:
            map_obj[tile].update()
            map_obj[tile].next_state()

        time.sleep(0.1)
        clear_output(wait=True)
