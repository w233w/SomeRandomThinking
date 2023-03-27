'''
Unfinished
'''
import pygame
from pygame import Vector2
import numpy as np


class utils:
    @staticmethod
    def check_winner(board):
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

    @staticmethod
    def check_mouse_in_spirte(sprite_pos, sprite_size):
        x, y = pygame.mouse.get_pos()
        x_in = sprite_pos[0] <= x <= sprite_pos[0] + sprite_size
        y_in = sprite_pos[1] <= y <= sprite_pos[1] + sprite_size
        return x_in and y_in


class ChessBoardUnit(pygame.sprite.Sprite):
    def __init__(self, abs_pos, parent):
        super().__init__()
        self.abs_pos = abs_pos
        self.parent = parent
        self.pos = 127 * parent.abs_pos + 41 * abs_pos
        self.status = 0
        self.active = False
        self.image_collection = {
            0: pygame.image.load("heart.png"),
            1: pygame.image.load("heart.png"),
            2: pygame.image.load("heart.png"),
        }
        self.image = self.image_collection[self.status]
        self.rect = self.image.get_rect(center=self.pos)  # 预设41*41

    def update(self):
        if not self.active:
            return
        self.active = self.status == 0
        self.image = self.image_collection[self.status]


class ChessBoard(pygame.sprite.Sprite):
    def __init__(self, abs_pos):
        super().__init__()
        self.abs_pos = abs_pos
        self.pos = 127 * abs_pos
        self.status = 0
        self.unit_status = np.zeros((3, 3), dtype=np.int32)
        self.active = False
        self.image_collection = {
            0: pygame.image.load("heart.png"),
            1: pygame.image.load("heart.png"),
            2: pygame.image.load("heart.png"),
        }
        self.image = self.image_collection[self.status]
        self.rect = self.image.get_rect(center=self.pos)  # 预设127*127
        self.units = pygame.sprite.Group()
        for i in range(3):
            for j in range(3):
                self.units.add(ChessBoardUnit(Vector2(i, j), self))

    def update(self):
        if not self.active:
            return
        self.units.draw(screen)
        self.active = self.status == 0
        self.image = self.image_collection[self.status]


__name__ = None
if __name__ == '__main__':
    # 各类参数
    # 窗口大小
    WIDTH = 400
    HEIGHT = 600
    SIZE = WIDTH, HEIGHT
    # 刷新率
    FPS = 60
    # Init pygame & Create screen
    pygame.init()
    screen = pygame.display.set_mode(SIZE)
    pygame.display.set_caption("测试")
    clock = pygame.time.Clock()
    running = True
    while running:
        # Game loop
        pass
