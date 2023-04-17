"""
简单来说，当鼠标移动到红色区域时，会根据Item.storage参数生成1到2个色块。1 for 绿色, 2 for 蓝绿。
当蓝绿色块存在时，除非鼠标移动到白色区域，蓝绿色块不会消失。特殊的，在蓝色块上点击鼠标不松开的话，即使鼠标移动到蓝色区域蓝绿也不会消失。
"""

import pygame

WIDTH = 400
HEIGHT = 400
SIZE = WIDTH, HEIGHT
FPS = 60

class Utils:
    @staticmethod
    def mouse_event_handler(event_list, event_type, button):
        for event in event_list:
            if event.type == event_type:
                if event.button == button:
                    return True
        return False

class Item(pygame.sprite.Sprite):
    def __init__(self, storage):
        super().__init__()
        self.rect = pygame.Rect(180, 180, 40, 40)
        self.image = pygame.Surface((40, 40))
        self.image.fill((255, 0, 0))
        self.menu = pygame.sprite.GroupSingle()
        self.storage = storage

    def update(self, event_list):
        mouse_pos = pygame.mouse.get_pos()
        self.menu.update(event_list)
        self.menu.draw(screen)
        self.mouse_hover = self.rect.collidepoint(mouse_pos)
        if self.mouse_hover and self.menu.sprite is None:
            self.menu.add(Menu((220, 200), self.storage))
        elif self.menu.sprite is not None:
            if not (self.mouse_hover or self.menu.sprite.alive):
                self.menu.empty()

class Menu(pygame.sprite.Sprite):
    def __init__(self, top_left, has_storage):
        super().__init__()
        self.size = (40, 60)
        self.rect = pygame.Rect(top_left, self.size)
        self.image = pygame.Surface(self.size)
        self.image.fill((0, 255, 0))
        self.has_storage = has_storage
        self.alive = False
        if self.has_storage:
            self.sub_menu = pygame.sprite.GroupSingle()
            sub_pos = top_left[0] + self.size[0], top_left[1]
            self.sub_menu.add(Sub_Menu(sub_pos))

    def update(self, event_list):
        if self.has_storage:
            self.sub_menu.update(event_list)
            self.sub_menu.draw(screen)
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.alive = True
        elif self.has_storage:
            self.alive = self.sub_menu.sprite.alive


class Sub_Menu(pygame.sprite.Sprite):
    def __init__(self, top_left):
        super().__init__()
        self.size = (40, 60)
        self.rect = pygame.Rect(top_left, self.size)
        self.image = pygame.Surface(self.size)
        self.image.fill((0, 0, 255))
        self.alive = False
        self.hold = False

    def update(self, event_list):
        if Utils.mouse_event_handler(event_list, pygame.MOUSEBUTTONUP, 1):
            self.hold = False

        if self.rect.collidepoint(pygame.mouse.get_pos()):
            if Utils.mouse_event_handler(event_list, pygame.MOUSEBUTTONDOWN, 1):
                self.hold = True
            self.alive = True
        else:
            self.alive = self.hold
                
if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    game = pygame.sprite.GroupSingle(Item(True))
    running = True
    while running:
        clock.tick(FPS)
        screen.fill(pygame.color.Color(255, 255, 255))
        event_list = pygame.event.get()
        for event in event_list:
            if event.type == pygame.QUIT:
                running = False
        game.update(event_list)
        game.draw(screen)
        pygame.display.flip()

pygame.quit()
