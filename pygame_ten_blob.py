import pygame
import math
import random
from statistics import mean

# 十滴水
# unfinished

MAX_BLOB_RANGE = 4
GRIDS_SIZE = 6

SCREEN_WIDTH = SCREEN_HEIGHT = 50 + 50 * GRIDS_SIZE
SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT

FPS = 60

BLACK = 0, 0, 0
ALMOST_BLACK = 1, 1, 1
WHITE = 255, 255, 255
SKYBLUE = 135, 206, 235
BLUE = 0, 0, 255


class Blob(pygame.sprite.Sprite):
    def __init__(self, pos, fill: int, *groups) -> None:
        super().__init__(*groups)
        self.pos = pygame.Vector2(pos)
        self.r = 20
        self.size = pygame.Vector2(2 * self.r)
        self.image = pygame.Surface(self.size)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect(center=self.pos)

        self.fill = fill
        self.max_fill = MAX_BLOB_RANGE + 1

        self.real_r = 10 + self.fill
        self.render()

    def render(self):
        self.font = pygame.font.SysFont("simhei", self.real_r)
        fill_info = self.font.render(str(self.fill), True, ALMOST_BLACK, None)
        text_size = self.font.size(str(self.fill))
        pygame.draw.circle(self.image, SKYBLUE, self.size // 2, self.real_r)
        self.image.blit(fill_info, [20 - text_size[0] / 2, 20 - text_size[1] / 2])

    def on_click(self, events: list[pygame.Event]):
        global available_click
        if available_click <= 0:
            return
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.dict["button"] == 1:
                if self.pos.distance_to(event.dict["pos"]) <= self.real_r:
                    self.fill += 1
                    available_click -= 1

    def on_split(self):
        ratio = pygame.sprite.collide_circle_ratio(0.2)
        if hits := pygame.sprite.spritecollide(self, split_group, True, ratio):
            self.fill += len(hits)

    def overflow(self):
        for direction in [[1, 0], [-1, 0], [0, 1], [0, -1]]:
            Split(self.pos, direction, split_group)

    def update(self, events: list[pygame.Event]):
        self.on_click(events)
        self.on_split()
        if self.fill >= self.max_fill:
            self.overflow()
            self.kill()
        elif self.real_r < 10 + self.fill:
            self.real_r = 10 + self.fill
            self.render()


class Split(pygame.sprite.Sprite):
    def __init__(self, pos, direction, *groups) -> None:
        super().__init__(*groups)
        self.r = 5
        self.pos = pygame.Vector2(pos)
        self.direction = pygame.Vector2(direction)
        self.size = pygame.Vector2(2 * self.r)
        self.image = pygame.Surface(self.size)
        self.image.set_colorkey(BLACK)
        pygame.draw.circle(self.image, BLUE, self.size // 2, self.r)
        self.rect = self.image.get_rect(center=self.pos)

    def update(self):
        self.pos += self.direction * 2
        self.rect.center = self.pos


class Grids(pygame.sprite.Sprite):
    def __init__(self, *groups) -> None:
        super().__init__(*groups)


screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("测试")
clock = pygame.time.Clock()
smooth_fps = [FPS] * 60
pygame.init()

blob_group = pygame.sprite.Group()
for i in range(GRIDS_SIZE):
    for j in range(GRIDS_SIZE):
        f = random.randint(0, MAX_BLOB_RANGE)
        if f > 0:
            Blob([50 + i * 50, 50 + j * 50], f, blob_group)

split_group = pygame.sprite.Group()
available_click = 10

while True:
    clock.tick(FPS)
    delay = 1000 / clock.get_time()
    smooth_fps.append(delay)
    smooth_fps.pop(0)
    real_fps = math.floor(mean(smooth_fps))
    pygame.display.set_caption(f"FPS: [{real_fps}] Remain: [{available_click}]")

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    screen.fill(WHITE)
    blob_group.update(events)
    split_group.update()

    blob_group.draw(screen)
    split_group.draw(screen)

    pygame.display.flip()
