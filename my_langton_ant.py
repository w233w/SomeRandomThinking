# Currently only working on jupyter
from enum import IntEnum
from collections import defaultdict
from IPython.display import clear_output
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import numpy as np


class Color(IntEnum):
    WHITE = 0
    BLACK = 1

    def visual(self):
        v = {
            0: '\u25a1',
            1: '\u25a0',
        }
        return v[self.value]


class Direction(IntEnum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

    def total_Direction():
        return 4


class RL(IntEnum):
    R = 1
    L = -1


class Rule:
    def __init__(self, rule='RL'):
        self.rule = rule

    def ant_rule(self, input_color, input_direction) -> (Color, Direction):
        output_direction = input_direction + RL[self.rule[input_color]]
        output_color = input_color + 1

        output_color %= len(self.rule)
        output_direction %= Direction.total_Direction()
        output_color = Color(output_color)
        output_direction = Direction(output_direction)

        return output_color, output_direction

    def move_rule(self, input_direction):
        if input_direction == Direction.UP:
            return 0, 1
        elif input_direction == Direction.RIGHT:
            return 1, 0
        elif input_direction == Direction.DOWN:
            return 0, -1
        elif input_direction == Direction.LEFT:
            return -1, 0
        else:
            raise ValueError('Unexpect direction')


class ant:
    def __init__(self, x=0, y=0, facing=Direction.LEFT) -> None:
        self.x = x
        self.y = y
        self.loc = (x, y)
        self.facing = facing
        self.rule = Rule()

    def __repr__(self):
        return f'loc : {self.loc}, facing: {self.facing.name}'

    def update(self, tile_color) -> Color:
        new_color, self.facing = self.rule.ant_rule(tile_color, self.facing)
        return new_color

    def next_state(self) -> None:
        del_x, del_y = self.rule.move_rule(self.facing)
        self.x += int(del_x)
        self.y += int(del_y)
        self.loc = (self.x, self.y)


class grid:
    def __init__(self):
        self.ant = ant()
        self.tiles = defaultdict(lambda: Color(0))

    def _update(self) -> None:
        ant_loc = self.ant.loc
        new_color = self.ant.update(self.tiles[ant_loc])
        self.tiles[ant_loc] = new_color
        self.ant.next_state()

    def _draw(self, scale) -> None:
        for i in range(-scale, scale+1):
            for j in range(-scale, scale+1):
                x, y = j, -i
                if (x, y) == self.ant.loc:
                    print('\u25cb', end=' ')
                else:
                    print(self.tiles[(x, y)].visual(), end=' ')
            print()

    def do_draw(self, total_frames=100, interval=0.1, scale=10):
        for _ in range(total_frames):
            self._update()
            print(self.ant)
            self._draw(scale)
            time.sleep(interval)
            clear_output(wait=True)

    def _animate(self, i):
        scale = self.scale
        image = np.full([scale*2, scale*2], np.array([0, 0, 0]))
        for loc, color in self.tiles.items():
            if -scale < loc[0] < scale and -scale < loc[1] < scale:
                image[loc[1]][-loc[0]] = np.array([255, 255, 255])*color
        self.ax1.clear()
        self.ax1.axis('off')
        self.ax1.plot(image)
        self._update()

    def do_animate(self, scale=10):
        '''Do not use, currently not working on jupyter
        '''
        self.fig = plt.figure()
        self.ax1 = self.fig.add_subplot(1, 1, 1)
        self.scale = scale
        a = animation.FuncAnimation(self.fig, self._animate, interval=1000)
        plt.show()


if __name__ == '__main__':
    g = grid()
    g.do_draw()
