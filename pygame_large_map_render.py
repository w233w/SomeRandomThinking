import pygame
import quads
import math
import random
from itertools import product
from statistics import mean
from collections import defaultdict

SCREEN_WIDTH = SCREEN_HEIGHT = 400
SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT
MAP_WIDTH = MAP_HEIGHT = 1000
MAP_SIZE = MAP_WIDTH, MAP_HEIGHT

FPS = 60
BLACK = 0, 0, 0
ALMOST_BLACK = 1, 1, 1
WHITE = 255, 255, 255
RED = 255, 0, 0
BLUE = 0, 0, 255
YELLOW = 255, 255, 0
GREEN = 0, 255, 0

Qtree = quads.QuadTree(list(pygame.Vector2(MAP_SIZE) // 2), MAP_WIDTH, MAP_HEIGHT)

# 大量敌人，有限大小地图，可探索。敌人每一段时间增强，玩家击败敌人不断获得资源。
# 玩家死亡后才能消费资源。资源可以提供下一局甚至全局能力。


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


class Player(pygame.sprite.Sprite):
    def __init__(self, *groups) -> None:
        super().__init__(*groups)
        self.size = pygame.Vector2(20)
        self.pos = pygame.Vector2(500)
        self.image = pygame.Surface(self.size)
        self.rect = self.image.get_rect(center=self.pos)
        self.camera = Camera()


class Camera(pygame.sprite.Sprite):
    def __init__(self, *groups) -> None:
        super().__init__(*groups)
        self.size = pygame.Vector2(SCREEN_SIZE)
        self.pos = pygame.Vector2(500, 500)
        self.image = pygame.Surface([20, 20])
        self.image.set_colorkey(BLACK)
        self.image.fill(GREEN)
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

        if self.pos.x < self.size[0] / 2:
            self.pos.x = self.size[0] / 2
        elif self.pos.x > MAP_WIDTH - self.size[0] / 2:
            self.pos.x = MAP_WIDTH - self.size[0] / 2

        if self.pos.y < self.size[1] / 2:
            self.pos.y = self.size[1] / 2
        elif self.pos.y > MAP_HEIGHT - self.size[1] / 2:
            self.pos.y = MAP_HEIGHT - self.size[1] / 2


class Menu(pygame.sprite.Sprite):
    def __init__(self, *groups) -> None:
        super().__init__(*groups)
        self.size = pygame.Vector2(SCREEN_SIZE)
        self.image = pygame.Surface([380, 380])
        self.image.set_colorkey(BLACK)
        self.image.fill(ALMOST_BLACK)
        self.image.set_alpha(180)
        self.rect = self.image.get_rect(center=self.size // 2)


class Interactive(pygame.sprite.Sprite):
    def __init__(self, rect: pygame.Rect, command: callable, *groups) -> None:
        super().__init__(*groups)
        self.size = rect.size
        self.image = pygame.Surface(self.size)
        self.image.set_colorkey(BLACK)
        self.rect = rect
        self.command = command
        self.hover = False

    def update(self, events):
        for event in events:
            if event.type == pygame.MOUSEMOTION:
                if not self.hover and self.rect.collidepoint(event.dict["pos"]):
                    self.hover = True
                    pygame.mouse.set_cursor(pygame.Cursor(pygame.SYSTEM_CURSOR_HAND))
                elif self.hover and not self.rect.collidepoint(event.dict["pos"]):
                    self.hover = False
                    pygame.mouse.set_cursor(pygame.Cursor(pygame.SYSTEM_CURSOR_ARROW))
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.dict["pos"]):
                    if event.dict["button"] == 1:
                        self.command()


class Button(Interactive):
    def __init__(
        self, rect: pygame.Rect, text: str, command: callable, *groups
    ) -> None:
        super().__init__(rect, command, *groups)
        self.image.fill(WHITE)
        self.text = text
        self.font = pygame.font.SysFont("simhei", 20)
        text_size = self.font.size(self.text)
        text_render = self.font.render(self.text, True, ALMOST_BLACK, None)
        self.image.blit(
            text_render,
            [self.size[0] / 2 - text_size[0] / 2, self.size[1] / 2 - text_size[1] / 2],
        )


screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("测试")
clock = pygame.time.Clock()
pygame.init()

buildings = pygame.sprite.Group()
for i in range(100):
    Building(
        [10, 10],
        ALMOST_BLACK,
        (random.randint(10, 990), random.randint(10, 990)),
        2,
        buildings,
    )
    Building(
        [10, 10],
        YELLOW,
        (random.randint(30, 970), random.randint(30, 970)),
        3,
        buildings,
    )
    Building(
        [10, 10],
        BLUE,
        (random.randint(30, 970), random.randint(30, 970)),
        3,
        buildings,
    )
    Building(
        [10, 10],
        RED,
        (random.randint(30, 970), random.randint(30, 970)),
        3,
        buildings,
    )

camera = pygame.sprite.GroupSingle()
C = Camera(camera)

smooth_fps = [FPS] * 10

drawing_building_by_z = defaultdict(lambda: pygame.sprite.Group())

pause = False
running = True

pause_menu = pygame.sprite.GroupSingle()
Menu(pause_menu)
mimic = None
menu_buttons = pygame.sprite.Group()


def depause():
    global pause
    pause = False


def stop_running():
    global running
    running = False


Button(pygame.Rect(50, 350, 80, 30), "继续", depause, menu_buttons)
Button(pygame.Rect(160, 350, 80, 30), "保存", print, menu_buttons)
Button(pygame.Rect(270, 350, 80, 30), "结束", stop_running, menu_buttons)

while running:
    clock.tick(FPS)
    delay = 1000 / clock.get_time()
    smooth_fps.append(delay)
    smooth_fps.pop(0)
    real_fps = math.floor(mean(smooth_fps))

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.dict["key"] in [pygame.K_q, pygame.K_ESCAPE]:
                pause = not pause
    # pause
    if pause:
        if mimic is None:
            mimic = screen.copy()
        screen.fill(WHITE)
        screen.blit(mimic, mimic.get_rect())
        pause_menu.update()
        menu_buttons.update(events)
        pause_menu.draw(screen)
        menu_buttons.draw(screen)
        pygame.display.flip()
        continue
    else:
        if mimic is not None:
            pygame.mouse.set_cursor(pygame.Cursor(pygame.SYSTEM_CURSOR_ARROW))
        mimic = None

    screen.fill(WHITE)
    buildings.update()
    camera.update()
    buildings.update()

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

pygame.quit()
