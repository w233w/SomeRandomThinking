from itertools import product
from typing import Self
import random
import pygame


class MapTile:
    def __init__(self, x, y, level=0) -> None:
        self.x = x
        self.y = y
        self.loc = (x, y)
        self.level = level
        self.temp_level = level

    def __repr__(self) -> str:
        return f"<{self.loc}|{self.level}>"

    def _visit_8_neighbor(self, map: dict[tuple[int, int], Self]) -> int:
        counter = 0

        for del_x, del_y in product([-1, 0, 1], [-1, 0, 1]):
            loc = (self.x + del_x, self.y + del_y)
            # Not counting self
            if del_x == del_y == 0:
                continue
            if loc in map:
                counter += map.get(loc, 0).level >= 1

        return counter

    def update(self, map: dict[tuple[int, int], Self]) -> None:
        """Game rules"""
        n = self._visit_8_neighbor(map)

        if self.level == 0:
            if 1 < n <= 3:
                self.temp_level = 1
        if self.level == 1:
            if 1 < n <= 3:
                self.temp_level = 2
            else:
                self.temp_level = 0
        if self.level == 2:
            if n == 0 or n > 3:
                self.temp_level = 1

    def next_state(self) -> None:
        self.level = self.temp_level


class MapController:
    def __init__(self) -> None:
        self.map: dict[tuple[int, int], MapTile] = {}
        for i in range(-60, 60):
            for j in range(-60, 60):
                if -10 <= i <= 10 and -10 <= j <= 10:
                    self.map[(i, j)] = MapTile(i, j, random.randint(0, 2))
                else:
                    self.map[(i, j)] = MapTile(i, j, 0)

    def next(self) -> None:
        for tile in self.map:
            self.map[tile].update(self.map)
        for tile in self.map:
            self.map[tile].next_state()

    def draw(self, screen):
        for sprite in tiles.sprites():
            sprite.kill()
        for tile in self.map:
            tiles.add(Tile(self.map[tile]))
        tiles.draw(screen)


class Tile(pygame.sprite.Sprite):
    color: dict[int, pygame.Color] = {
        0: pygame.Color(255, 255, 255),
        1: pygame.Color(128, 0, 0),
        2: pygame.Color(255, 0, 0),
    }

    def __init__(self, map_tile: MapTile) -> None:
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.level = map_tile.level
        self.color = Tile.color[self.level]
        self.image.fill(self.color)
        self.coord = map_tile.loc
        self.pos = pygame.Vector2(self.coord) * 10 + pygame.Vector2(300, 300)
        self.rect = self.image.get_rect(center=self.pos)


# Init pygame & Crate screen
pygame.init()
screen = pygame.display.set_mode((600, 600))
pygame.display.set_caption("测试")
clock = pygame.time.Clock()
FPS = 60

pygame.event.set_allowed([pygame.QUIT, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP])

tiles = pygame.sprite.Group()

GC = MapController()
next_iter = 0

while running := True:
    # 决定游戏刷新率
    clock.tick(FPS)
    # 点×时退出。。
    event_list = pygame.event.get()
    for event in event_list:
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    screen.fill(pygame.Color((255, 255, 255)))
    GC.draw(screen)
    if pygame.time.get_ticks() - next_iter >= 1000 / FPS:
        GC.next()
        next_iter = pygame.time.get_ticks()
    pygame.display.flip()
