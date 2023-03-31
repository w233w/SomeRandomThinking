'''
Unfinished
TODO:
    1. Game logic to force player play on specific board
       or anyplace if on special case               ------- Done
    2. Visual effect to let player know where they can play next
    3. Simple UI let player able to click (re)start ------- Half Done, Black start screen now.
    4. Simple UI let player click info buttom to read the game rule --Maybe put the rule on start screen
    5. Simple UI let player can see who will play next
    6. Too many magical number, clear the code.
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

    @staticmethod
    def stage_update(game_info, groupsingle):
        if groupsingle.sprite is None:
            groupsingle.add(UI(Vector2(WIDTH/2, HEIGHT/2)))
            state_code = -2
            print('init on ui')
        elif isinstance(groupsingle.sprite, UI):
            if game_info['state_code'] == -2:
                groupsingle.add(LargeChessBoard(Vector2(WIDTH/2, HEIGHT/2)))
                print('change to board')
                game_info['state_code'] = 0
        elif isinstance(groupsingle.sprite, LargeChessBoard):
            if game_info['state_code'] != 0:
                groupsingle.add(UI(Vector2(WIDTH/2, HEIGHT/2)))
                print('change to ui')
                game_info['state_code'] = 0

    @staticmethod
    def mouse_event_handler(event_list, event_type, button):
        for event in event_list:
            if event.type == event_type:
                if event.button == button:
                    return True
        return False
            

class ChessBoardUnit(pygame.sprite.Sprite):
    def __init__(self, abs_pos, parent):
        super().__init__()
        self.abs_pos = abs_pos
        self.parent = parent
        self.status = 0
        self.active = True
        self.image_collection = {
            0: pygame.image.load("none.png"),  # change to empty
            1: pygame.image.load("circle.png"),  # change to O
            2: pygame.image.load("cross.png"),  # change to X
        }
        self.image = self.image_collection[self.status]
        image_size = self.image.get_size()[0]
        self.pos = 136 * parent.abs_pos + 44 * abs_pos + Vector2(image_size/2)
        self.rect = self.image.get_rect(center=self.pos)  # 预设40*40, Unit间隔4

    def update(self, game_info, event_list):
        if not self.active:
            return
        if self.parent.playable:
            if utils.check_mouse_in_spirte(self.pos, self.image.get_size()[0]):
                if utils.mouse_event_handler(event_list, pygame.MOUSEBUTTONDOWN, 1):
                    game_info['player'] = 3 - game_info['player']
                    self.status = game_info['player']
                    self.parent.unit_status[int(self.abs_pos.x)][int(self.abs_pos.y)] = self.status
                    self.parent.parent.next_board = self.abs_pos
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
        self.playable = True
        self.image_collection = {
            0: pygame.image.load("board.png"),  # change to 3*3 grid
            1: pygame.image.load("big-circle.png"),  # change to BIG O
            2: pygame.image.load("big-cross.png"),  # change to BIG X
            -1: pygame.image.load("gray.png")
        }
        self.image = self.image_collection[self.status]
        image_size = self.image.get_size()[0]
        self.pos = 136 * abs_pos + Vector2(image_size/2)
        self.rect = self.image.get_rect(center=self.pos)  # 预设128*128，Board间隔8
        self.units = pygame.sprite.Group()
        for i in range(3):
            for j in range(3):
                self.units.add(ChessBoardUnit(Vector2(i, j), self))

    def update(self, game_info, event_list):
        if not self.active:
            return
        if self.parent.rule == 'strict':
            if self.abs_pos != self.parent.next_board:
                self.playable = False
            else:
                self.playable = True
        else:
            self.playable = True
        self.units.update(game_info, event_list)
        self.units.draw(screen)
        winner = utils.check_winner(self.unit_status)
        self.status = winner
        self.parent.unit_status[int(self.abs_pos.x)][int(self.abs_pos.y)] = winner
        self.active = self.status == 0
        self.image = self.image_collection[self.status]


class LargeChessBoard(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.pos = pos
        self.unit_status = np.zeros((3, 3), dtype=np.int32)
        self.image = pygame.image.load("bomb.png")
        self.rect = self.image.get_rect(center=self.pos)
        self.units = pygame.sprite.Group()
        for i in range(3):
            for j in range(3):
                self.units.add(ChessBoard(Vector2(i, j), self))
        self.rule = 'strict'
        self.next_board = Vector2(1, 1)

    def update(self, game_info, event_list):
        if self.unit_status[int(self.next_board.x)][int(self.next_board.y)] != 0:
            self.rule = 'free'
        else:
            self.rule = 'strict'
        self.units.update(game_info, event_list)
        game_info['state_code'] = utils.check_winner(self.unit_status)
        self.units.draw(screen)


class UI(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.pos = pos
        self.image = pygame.image.load("bomb.png")
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, game_info, event_list):
        if utils.mouse_event_handler(event_list, pygame.MOUSEBUTTONDOWN, 1):
            game_info['state_code'] = -2


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

    game = pygame.sprite.GroupSingle()
    # state code explain:
    # -2 for not in game (on start screen)
    # -1 for tie
    # 0 for game not end yet
    # 1 for player one win
    # 2 for player two win
    game_info = {'state_code': 0, 'player': 1}
    running = True
    while running:
        clock.tick(FPS)
        utils.stage_update(game_info, game)
        screen.fill(pygame.Color(255, 255, 255))
        # 点×时退出。。
        event_list = pygame.event.get()
        for event in event_list:
            if event.type == pygame.QUIT:
                running = False
        # Game loop
        game.update(game_info, event_list)
        # game.draw(screen)
        pygame.display.flip()

pygame.quit()
