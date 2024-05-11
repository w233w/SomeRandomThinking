import pygame
import math
import random

# 各类参数
# 窗口大小
WIDTH = 200
HEIGHT = 400
SIZE = WIDTH, HEIGHT
VSIZE = pygame.Vector2(SIZE)

HEX_RADUIS = 20
HEX_WIDTH = 40
HEX_HEIGHT = math.sqrt(3) * HEX_RADUIS // 2
# 刷新率
FPS = 60

# 颜色
BackgroundColor = 222, 222, 222
BaseColor = 173, 213, 162
Black = 0, 0, 0
Line = 20, 35, 52
AlmostBlack = 1, 1, 1
White = 255, 255, 255
Red = 255, 0, 0
Darkred = 128, 0, 0
Blue = 0, 0, 255
Cyan = 0, 255, 255
Lightblue = 135, 206, 235
Lightcyan = 204, 255, 255
Green = 0, 255, 0
Yellow = 255, 255, 0
Golden = 255, 215, 0
Gray = 192, 192, 192


class Hexgon(pygame.sprite.Sprite):
    color_map = {1: Red, 2: Blue, 3: Green, 4: Yellow, 5: Golden, 6: Cyan, 7: Darkred}

    shift = [
        pygame.Vector2(-HEX_RADUIS, 0),
        pygame.Vector2(-HEX_RADUIS / 2, -HEX_HEIGHT),
        pygame.Vector2(HEX_RADUIS / 2, -HEX_HEIGHT),
        pygame.Vector2(HEX_RADUIS, 0),
        pygame.Vector2(HEX_RADUIS / 2, HEX_HEIGHT),
        pygame.Vector2(-HEX_RADUIS / 2, HEX_HEIGHT),
    ]

    def __init__(self, pos: pygame.Vector2, type: int, *groups) -> None:
        super().__init__(*groups)
        self.pos = pos
        self.radius = HEX_RADUIS
        self.image = pygame.Surface([3 * HEX_RADUIS, 3 * HEX_RADUIS])
        self.image.set_colorkey(Black)
        self.center = pygame.Vector2(1.5 * HEX_RADUIS, 1.5 * HEX_RADUIS)
        self.points = list(map(lambda point: self.center + point, Hexgon.shift))
        pygame.draw.polygon(self.image, Hexgon.color_map[type], self.points)
        pygame.draw.lines(self.image, AlmostBlack, True, self.points, 1)
        self.rect = self.image.get_rect(center=self.pos)


class HexController:
    def __init__(self) -> None:
        pass


pygame.init()
screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption("测试")
clock = pygame.time.Clock()
Font = pygame.font.SysFont("timesnewroman", 15)

test = pygame.sprite.Group()

for i in range(int(WIDTH / (1.5 * HEX_WIDTH) + 1)):
    for j in range(int(HEIGHT / (1.5 * HEX_HEIGHT) + 1)):
        test.add(
            Hexgon(
                pygame.Vector2(i * 3 * HEX_RADUIS, j * 2 * HEX_HEIGHT),
                random.randint(1, 7),
            )
        )
        test.add(
            Hexgon(
                pygame.Vector2(
                    (i + 0.5) * 3 * HEX_RADUIS,
                    (j + 0.5) * 2 * HEX_HEIGHT,
                ),
                random.randint(1, 7),
            )
        )

while running := True:
    clock.tick(FPS)
    screen.fill(White)
    event_list = pygame.event.get()
    for event in event_list:
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    test.update()
    test.draw(screen)
    pygame.display.flip()
