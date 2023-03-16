import numpy as np
import matplotlib.pyplot as plt


class LangtonsAnt:
    '''最终结果呈现了一个类似沼泽上破旧的遗迹的效果。
    '''
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = np.zeros((height, width), dtype=int)
        self.ant_pos = (width//2, height//2)
        self.ant_dir = 0

    def step(self):
        x, y = self.ant_pos
        if self.grid[y][x] == 0:
            self.ant_dir = (self.ant_dir - 1) % 4
            self.grid[y][x] = 1
        elif self.grid[y][x] == 1:
            self.ant_dir = (self.ant_dir + 1) % 4
            self.grid[y][x] = 2
        else:
            self.ant_dir = (self.ant_dir + 1) % 4
            self.grid[y][x] = 0

        if self.ant_dir == 0:  # up
            self.ant_pos = (x, y-1)
        elif self.ant_dir == 1:  # right
            self.ant_pos = (x+1, y)
        elif self.ant_dir == 2:  # down
            self.ant_pos = (x, y+1)
        elif self.ant_dir == 3:  # left
            self.ant_pos = (x-1, y)

        if self.ant_pos[0] < 0:
            self.ant_pos = (self.width-1, self.ant_pos[1])
        elif self.ant_pos[0] >= self.width:
            self.ant_pos = (0, self.ant_pos[1])
        elif self.ant_pos[1] < 0:
            self.ant_pos = (self.ant_pos[0], self.height-1)
        elif self.ant_pos[1] >= self.height:
            self.ant_pos = (self.ant_pos[0], 0)

    def run(self, steps):
        for i in range(steps):
            self.step()

    def display(self):
        plt.imshow(self.grid, cmap='Set3')
        plt.show()


ant = LangtonsAnt(100, 100)
ant.run(50000)
ant.display()
