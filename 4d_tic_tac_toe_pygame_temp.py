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
    def check_mouse_in_spirte(sprite_center, sprite_size):
        x, y = pygame.mouse.get_pos()
        sprite_x, sprite_y = sprite_center
        half_size = sprite_size / 2
        x_in = sprite_x - half_size <= x <= sprite_x + half_size
        y_in = sprite_y - half_size <= y <= sprite_y + half_size
        return x_in and y_in


class ChessBoardUnit(pygame.sprite.Sprite):
    def __init__(self, abs_pos, parent):
        super().__init__()
        self.abs_pos = abs_pos
        self.parent = parent
        self.status = 0
        self.active = True
        self.image_collection = {
            0: pygame.image.load("none.png"),  # change to empty
            1: pygame.image.load("circle.png"),  # change to X
            2: pygame.image.load("cross.png"),  # change to O
        }
        self.image = self.image_collection[self.status]
        image_size = self.image.get_size()[0]
        self.pos = 136 * parent.abs_pos + 44 * abs_pos + Vector2(image_size/2)
        self.rect = self.image.get_rect(center=self.pos)  # 预设40*40, Unit间隔4

    def update(self):
        if not self.active:
            return
        if utils.check_mouse_in_spirte(self.pos, self.image.get_size()[0]):
            if pygame.mouse.get_pressed()[0] == 1:
                self.status = 1
        self.active = self.status == 0
        self.image = self.image_collection[self.status]


class ChessBoard(pygame.sprite.Sprite):
    def __init__(self, abs_pos, parent):
        super().__init__()
        self.abs_pos = abs_pos
        self.parent = parent
        self.status = 0
        self.unit_status = np.zeros((3, 3), dtype=np.int32)
        self.active = True
        self.image_collection = {
            0: pygame.image.load("board.png"),  # change to 3*3 grid
            1: pygame.image.load("board.png"),  # change to BIG X
            2: pygame.image.load("board.png"),  # change to BIG O
        }
        self.image = self.image_collection[self.status]
        image_size = self.image.get_size()[0]
        self.pos = 136 * abs_pos + Vector2(image_size/2)
        self.rect = self.image.get_rect(center=self.pos)  # 预设128*128，Board间隔8
        self.units = pygame.sprite.Group()
        for i in range(3):
            for j in range(3):
                self.units.add(ChessBoardUnit(Vector2(i, j), self))

    def update(self):
        if not self.active:
            return
        self.units.update()
        self.units.draw(screen)
        self.active = self.status == 0
        self.image = self.image_collection[self.status]


class LargeChessBoard(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.pos = Vector2(200, 200) + Vector2(20, 20)
        self.unit_status = np.zeros((3, 3), dtype=np.int32)
        self.image = pygame.image.load("bomb.png")
        self.rect = self.image.get_rect(center=self.pos)
        self.units = pygame.sprite.Group()
        for i in range(3):
            for j in range(3):
                self.units.add(ChessBoard(Vector2(i, j), self))
        self.winner = -1

    def update(self):
        self.units.update()
        self.units.draw(screen)


if __name__ == '__main__':
    # 各类参数
    # 窗口大小
    WIDTH = 400
    HEIGHT = 400
    SIZE = WIDTH, HEIGHT
    # 刷新率
    FPS = 60
    # Init pygame & Create screen
    pygame.init()
    screen = pygame.display.set_mode(SIZE)
    clock = pygame.time.Clock()

    gameboard = LargeChessBoard()
    gg = pygame.sprite.Group()
    gg.add(gameboard)
    running = True
    while running:
        clock.tick(FPS)
        screen.fill(pygame.Color(255, 255, 255))
        # 点×时退出。。
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        # Game loop
        gg.update()
        # gg.draw(screen)
        pygame.display.flip()
    pygame.quit()
