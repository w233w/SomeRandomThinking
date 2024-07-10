import pygame

# 十滴水
# unfinished

SCREEN_WIDTH = SCREEN_HEIGHT = 400
SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT

FPS = 60

BLACK = 0, 0, 0
ALMOST_BLACK = 1, 1, 1
COLOR = 29, 31, 211
WHITE = 255, 255, 255
RED = 255, 0, 0
LIGHT_RED = 255, 128, 128
BLUE = 0, 0, 255
YELLOW = 255, 255, 0
GREEN = 0, 255, 0


class Blob(pygame.sprite.Sprite):
    def __init__(self, pos, fill: int, *groups) -> None:
        super().__init__(*groups)
        self.pos = pygame.Vector2(pos)
        self.r = 20
        self.size = pygame.Vector2(2 * self.r)
        self.image = pygame.Surface(self.size)
        self.image.set_colorkey(BLACK)

        self.fill = fill
        self.max_fill = 7

    @property
    def real_r(self):
        return 10 + self.fill

    def render(self):
        pygame.draw.circle(self.image, BLUE, self.size // 2, self.real_r)

    def on_click(self, events: list[pygame.Event]):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.dict["key"] == 1:
                pass


class Split(pygame.sprite.Sprite):
    def __init__(self, *groups) -> None:
        super().__init__(*groups)
        self.r = 5
        self.size = pygame.Vector2(2 * self.r)
        self.image = pygame.Surface(self.size)
        self.image.set_colorkey(BLACK)


class Grid(pygame.sprite.Sprite):
    def __init__(self, *groups) -> None:
        super().__init__(*groups)


class Grids(pygame.sprite.Sprite):
    def __init__(self, *groups) -> None:
        super().__init__(*groups)
