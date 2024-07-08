import pygame
import quads
import math
import random
from copy import deepcopy
from itertools import product
from statistics import mean
from collections import defaultdict

# free move on large map, render building by z-index.
# only render building captured by camera.

SCREEN_WIDTH = SCREEN_HEIGHT = 400
SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT
MAP_WIDTH = MAP_HEIGHT = 1000
MAP_SIZE = MAP_WIDTH, MAP_HEIGHT

FPS = 60

BLACK = 0, 0, 0
ALMOST_BLACK = 1, 1, 1
COLOR = 29, 31, 211
WHITE = 255, 255, 255
RED = 255, 0, 0
BLUE = 0, 0, 255
YELLOW = 255, 255, 0
GREEN = 0, 255, 0

Qtree = quads.QuadTree(list(pygame.Vector2(MAP_SIZE) // 2), MAP_WIDTH, MAP_HEIGHT)


class Building(pygame.sprite.Sprite):
    def __init__(self, size, color, pos, z_index, *groups) -> None:
        super().__init__(*groups)
        self.image = pygame.Surface(size)
        self.image.set_colorkey(BLACK)
        self.color = color
        self.image.fill(color)
        self.pos = pos
        self.z_index = z_index
        self.rect = self.image.get_rect(center=self.pos)

        important_points = set(
            [
                self.rect.topleft,
                self.rect.topright,
                self.rect.bottomleft,
                self.rect.bottomright,
            ]
        )

        delta_height = self.rect.bottom - self.rect.top
        height_split = int(delta_height // SCREEN_HEIGHT)
        delta_width = self.rect.right - self.rect.left
        width_split = int(delta_width // SCREEN_WIDTH)

        for i, j in product(range(height_split + 1), range(width_split + 1)):
            important_points.add(
                (
                    int(self.rect.left + delta_width * j / (width_split + 1)),
                    int(self.rect.top + delta_height * i / (height_split + 1)),
                )
            )
            important_points.add(
                (
                    int(self.rect.right - delta_width * j / (width_split + 1)),
                    int(self.rect.bottom - delta_height * i / (height_split + 1)),
                )
            )

        for point in important_points:
            if p := Qtree.find(point):
                p.data.append(self)
            else:
                Qtree.insert(point, [self])

    def update(self) -> None:
        if self in drawing_building_by_z[self.z_index]:
            print(self.rect)
        new_pos = self.pos - C.pos + C.size // 2
        self.rect.center = new_pos


class Camera(pygame.sprite.Sprite):
    def __init__(self, *groups) -> None:
        super().__init__(*groups)
        self.size = pygame.Vector2(SCREEN_SIZE)
        self.pos = pygame.Vector2(500, 500)
        self.image = pygame.Surface([20, 20])
        self.image.set_colorkey(BLACK)
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=self.size // 2)

    def update(self) -> None:
        key_pressed = pygame.key.get_pressed()

        left = key_pressed[pygame.K_LEFT] or key_pressed[pygame.K_a]
        up = key_pressed[pygame.K_UP] or key_pressed[pygame.K_w]
        down = key_pressed[pygame.K_DOWN] or key_pressed[pygame.K_s]
        right = key_pressed[pygame.K_RIGHT] or key_pressed[pygame.K_d]

        del_x = right - left
        del_y = down - up

        self.pos += 3 * pygame.Vector2(del_x, del_y)

        if key_pressed[pygame.K_r]:
            self.pos = pygame.Vector2(500, 500)


class Menu(pygame.sprite.Sprite):
    def __init__(self, *groups) -> None:
        super().__init__(*groups)
        self.size = pygame.Vector2(SCREEN_SIZE)
        self.image = pygame.Surface([380, 380])
        self.image.set_colorkey(BLACK)
        self.image.fill(ALMOST_BLACK)
        self.image.set_alpha(80)
        self.rect = self.image.get_rect(center=self.size // 2)

    def update(self) -> None:
        pass


screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("测试")
clock = pygame.time.Clock()
pygame.init()

background = pygame.sprite.Group()
Building([500, 500], BLUE, (250, 250), 1, background)
Building([500, 500], YELLOW, (750, 250), 1, background)
Building([500, 500], RED, (250, 750), 1, background)
Building([500, 500], GREEN, (750, 750), 1, background)
for i in range(100):
    Building(
        [10, 10],
        ALMOST_BLACK,
        (random.randint(10, 990), random.randint(10, 990)),
        2,
        background,
    )
for i in range(100):
    Building(
        [30, 30],
        COLOR,
        (random.randint(30, 970), random.randint(30, 970)),
        3,
        background,
    )

camera = pygame.sprite.GroupSingle()
C = Camera(camera)

smooth_fps = [FPS] * 10

drawing_building_by_z = defaultdict(lambda: pygame.sprite.Group())

pause = False

pause_menu = pygame.sprite.GroupSingle()
Menu(pause_menu)
mimic = None


while True:
    clock.tick(FPS)
    delay = 1000 / clock.get_time()
    smooth_fps.append(delay)
    smooth_fps.pop(0)
    real_fps = math.floor(mean(smooth_fps))

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.dict["key"] == pygame.K_q:
                pause = not pause

    # pause
    if pause:
        if mimic is None:
            mimic = deepcopy(screen)
        screen.fill(WHITE)
        screen.blit(mimic, mimic.get_rect())
        pause_menu.update()
        pause_menu.draw(screen)
        pygame.display.flip()
        continue
    else:
        mimic = None

    screen.fill(WHITE)
    camera.update()
    background.update()

    bb = quads.BoundingBox(
        C.pos.x - SCREEN_WIDTH / 2,
        C.pos.y - SCREEN_HEIGHT / 2,
        C.pos.x + SCREEN_WIDTH / 2,
        C.pos.y + SCREEN_HEIGHT / 2,
    )
    points = Qtree.within_bb(bb)

    for point in points:
        for building in point.data:
            drawing_building_by_z[building.z_index].add(building)

    for z_index in drawing_building_by_z:
        drawing_building_by_z[z_index].draw(screen)
        drawing_building_by_z[z_index].empty()

    camera.draw(screen)

    pygame.display.flip()
