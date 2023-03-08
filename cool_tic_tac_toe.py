# Unfinished!
import time
import numpy as np
from IPython.display import clear_output


def validation(func):
    '''
    A simple decorator used to handle invalid input()
    Unless got valid input(), func will never stop.
    '''
    def warpper(*args, **kwargs):
        while True:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(e)
    return warpper


class ttt:
    def __init__(self):
        self.board = np.zeros([9, 9], np.int32)
        self.larger_board = np.zeros([3, 3], np.int32)
        self.on_board = np.ones(2, np.int32)
        self.free_play_chance = False
    
    def show(self):
        for i in range(9):
            for j in range(9):
                print(self.board[i][j], end=' ')
                if j % 3 == 2:
                    print('   ', end='')
            print()
            if i % 3 == 2:
                print()
    
    def judge(self, grid_33):
        if grid_33.shape != [3, 3]:
            raise ValueError('Code error')

    @validation
    def normal_play(self, team):
        x, y = input().split(' ')
        x, y = int(x), int(y)
        if x < 0 or x > 2 or y < 0 or y > 2:
            raise ValueError('x, y must be [0-2]')
        del_x, del_y = self.on_board * 3
        if self.board[x+del_x][y+del_y] == 0:
            self.board[x+del_x][y+del_y] = team
            if self.larger_board[x][y] != 0:
                self.free_play_chance = True
            else:
                self.on_board = np.array([x, y])
        else:
            raise ValueError('This place has already been played')

    @validation
    def free_play(self, team):
        x, y = input().split(' ')
        x, y = int(x), int(y)
        if x < 0 or x > 9 or y < 0 or y > 9:
            raise ValueError('x, y must be [0-8]')
        if self.board[x][y] == 0:
            self.board[x][y] = team
            if self.larger_board[x//3][y//3] != 0:
                self.free_play_chance = True
            else:
                self.on_board = np.array([x//3, y//3])
        else:
            raise ValueError('This place has already been played')

    def run(self):
        player = 1
        while True:
            clear_output(wait=True)
            self.show()
            time.sleep(1)
            if self.free_play_chance:
                self.free_play(player)
            else:
                self.normal_play(player)
            player = 3 - player

t = ttt()
t.run()
