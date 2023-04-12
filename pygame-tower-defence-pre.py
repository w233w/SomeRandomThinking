import pygame
from pygame.math import Vector2


WIDTH = 720
HEIGHT = 480
SIZE = WIDTH, HEIGHT
FPS = 60
"""
简述一下游戏设计：
玩家需要在随机生成的地图上建造防御塔抵御一波一波的敌人。
地图分为上下层，代表地面与高低。所有地方均可建造防御塔，除了地面和高地的交界处。
敌人分为空军和地面部队，有多种变体。空军可以无视高地的限制，地面部队只能走地面。
玩家在地面上一定有一个主基地，主基地可以储存资源和产生电力。主基地被破坏则游戏结束。
地图任何地方都会生成资源，玩家可以建造采集机器来获取。资源大概有钢铁，煤炭等。
资源的输送需要建造管道，以节点连线的方式呈现。代码中可以用图搜索来判断是否联通。
主基地需要煤炭资源来产生电力，电力类似资源需要通过电路连接。
部分防御塔需要电力运作，部分防御塔需要资源运作。或是用来增强、升级。
防御塔会被摧毁，但敌人会根据威胁程度选择攻击防御塔或者继续向主基地前进。
建造防御塔也需要资源。
"""

class Info(pygame.sprite.Sprite):
    def __init__(self, size):
        super().__init__()
        self.image = pygame.image.load("th.jpg")
        self.center = Vector2(size)/2
        self.offset_up = 0
        self.offset_left = 0
        self.offset_buttom = 0
        self.offset_right = 0
        self.rect = self.image.get_rect(center = self.center)
        self.components = pygame.sprite.Group()
        self.sidebar = DataBar()
        self.components.add(self.sidebar)

        self.drag = False

    def update(self, event_list):
        self.components.update()
        self.components.draw(screen)
        mouse_pos = Vector2(pygame.mouse.get_pos())
        if self.rect.collidepoint(mouse_pos):
            for event in event_list:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouse_start_drag = Vector2(mouse_pos)
                    self.drag = True
                if event.type == pygame.MOUSEBUTTONUP:
                    self.drag = False
        if self.drag:
            delta = Vector2(mouse_pos) - self.mouse_start_drag
            self.mouse_start_drag = Vector2(mouse_pos)
            self.center += delta
            self.rect = self.image.get_rect(center = self.center)


class DataBar(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.font = pygame.font.Font('simhei.ttf',  10)
        self.rect = pygame.Rect(0, 0, 60, 480)
        self.image = pygame.Surface((60, 480))
        self.image.fill((200, 200, 200))
        self.text = self.font.render("Cool", False, pygame.Color(0, 0, 0))
        self.image.blit(self.text, (10, 10))

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    game = pygame.sprite.GroupSingle(Info(SIZE))
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
