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
    '''
    游戏在3*3的9个井字棋的棋盘上进行。
    第一手默认在[1, 1]处的井字棋的棋盘上落子。
    落子的位置决定了下一次落子的棋盘。
    例如：当玩家在棋盘上的[2, 2]处落子后，则下一手必须在[2, 2]处的棋盘上落子，除非出现例外。
    当某个棋盘上达成3连时，该棋盘被封锁并由3连的玩家持有。
    当一个棋盘9个格子被摆满而没有3连出现时，棋盘也会被封锁，并由最后落子的玩家持有。
    例外：当下一回合落子的位置是被封锁的棋盘时，下一回合的落子不再有棋盘限制。
    被封锁的棋盘不允许再落子。
    胜利的条件是持有的棋盘达成3连的玩家获胜。
    
    io模式下操作：
        每次输入两个数字，用空格隔开。数字从零开始数。
        第一个数字表示从左往右数第几列
        第二个数字表示从上往下数第几行
        normal play时，会提示落子的棋盘，数字逻辑同上。输入的数字均需处于[0-2]，例如'1 2'
        free play时，可以在任意空白处落子。输入的数字均需处于[0-8]，例如'6 7'
        输入无效时会提示，在得到有效输入前游戏不会继续。
        
    TODO:
        free play和normal play的逻辑有重构的空间
    '''

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

    def check_winner(self, board):
        '''
        checks for a winner
        1 for player 1 win
        2 for player 2 win
        0 for no winner yet
        -1 for tie
        '''
        board = board.flatten().tolist()

        # first row check
        for i in range(0, 9, 3):
            if board[i:i + 3] == [1] * 3 or board[i:i + 3] == [2] * 3:
                return board[i]

        # now column check
        for i in range(3):
            if board[i::3] == [1] * 3 or board[i::3] == [2] * 3:
                return board[i]

        # now test down slope
        if board[0::4] == [1] * 3 or board[0::4] == [2] * 3:
            return board[0]

        # now test up slope
        if board[2:7:2] == [1] * 3 or board[2:7:2] == [2] * 3:
            return board[2]

        # now test if there are more moves possible.
        if 0 in board:
            return 0

        # now return a draw
        return -1

    @validation
    def normal_play(self, team):
        # 获取当前棋盘落子的位置
        x, y = input().split(' ')
        x, y = int(x), int(y)
        if x < 0 or x > 2 or y < 0 or y > 2:
            raise ValueError('x, y must be [0-2]')

        # 获取落子棋盘的位置
        board_x, board_y = self.on_board
        del_x, del_y = 3 * board_x, 3 * board_y

        # 落子
        if self.board[x+del_x][y+del_y] == 0:
            # 在目标位置落子
            self.board[x+del_x][y+del_y] = team
            # 落子后判断胜负
            res = self.check_winner(self.board[del_x:del_x+3, del_y:del_y+3])
            # 如果平局则最后落子者赢下棋盘
            if res == -1:
                res = team
            elif res > 0:
                # 更新棋盘信息
                self.larger_board[board_x][board_y] = res
                self.board[del_x:del_x+3, del_y:del_y+3] = res
            # 判断下一回合棋盘是否被封锁
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
            res = self.check_winner(self.board[x//3*3:x//3*3+3, y//3*3:y//3*3+3])
            if res == -1:
                res = team
            elif res > 0:
                self.larger_board[x//3][y//3] = res
                self.board[x//3*3:x//3*3+3, y//3*3:y//3*3+3] = res
            if self.larger_board[x//3][y//3] != 0:
                self.free_play_chance = True
            else:
                self.on_board = np.array([x-x//3*3, y-y//3*3])
        else:
            raise ValueError('This place has already been played')

    def run(self):
        player = 1
        while True:
            clear_output(wait=True)
            self.show()
            time.sleep(1)
            if self.free_play_chance:
                print('Free play')
                self.free_play(player)
            else:
                print('Normal play on', self.on_board)
                self.normal_play(player)
            if self.check_winner(self.larger_board) != 0:
                return self.check_winner(self.larger_board)
            # 切换玩家
            player = 3 - player


if __name__ == '__main__':
    ttt().run()
