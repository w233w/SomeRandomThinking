import pygame
import math
import numpy as np
from statistics import mean

SCREEN_WIDTH = SCREEN_HEIGHT = 400
SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT

FPS = 60

BLACK = 0, 0, 0
ALMOST_BLACK = 1, 1, 1
WHITE = 255, 255, 255
ORANGE = 255, 128, 0
YELLOW = 255, 255, 0

c = False


class Atom(pygame.sprite.Sprite):
    def __init__(self, pos, *groups) -> None:
        super().__init__(*groups)
        self.pos = pygame.Vector2(pos)
        self.radius = 10
        self.size = pygame.Vector2(2 * self.radius)
        self.image = pygame.Surface(self.size)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect(center=self.pos)
        self.selected = False
        self.vect = pygame.Vector2(*np.random.randn(2)).normalize()
        self.speed = np.random.random() + 1
        self.render(ORANGE)

    def render(self, color):
        pygame.draw.circle(self.image, color, self.size // 2, self.radius)

    def on_select(self, events: list[pygame.Event]):
        global c
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.dict["button"] == 1:
                if c:
                    return
                elif self.pos.distance_to(event.dict["pos"]) <= self.radius:
                    self.selected = True
                    self.render(YELLOW)
                    c = True
            elif self.selected and event.type == pygame.MOUSEBUTTONUP:
                if event.dict["button"] == 1:
                    self.on_release(event.dict["pos"])
                elif event.dict["button"] == 2:
                    self.selected = False
                    self.render(ORANGE)
                c = False

    def on_hit(self):
        if pygame.sprite.spritecollide(
            self, neutron_group, True, pygame.sprite.collide_circle
        ):
            self.kill()
            num = np.random.choice([1, 2], p=[0.8, 0.2])
            for _ in range(num):
                Neutron(
                    self.pos,
                    pygame.Vector2(*np.random.randn(2)).normalize(),
                    neutron_group,
                )

    def on_release(self, mouse_pos):
        direction = pygame.Vector2(mouse_pos) - self.pos
        self.kill()
        Neutron(self.pos, direction, neutron_group)

    def bounce(self):
        if self.pos.x <= self.radius or self.pos.x >= SCREEN_WIDTH - self.radius:
            self.vect.x = -self.vect.x
        if self.pos.y <= self.radius or self.pos.y >= SCREEN_HEIGHT - self.radius:
            self.vect.y = -self.vect.y

    def update(self, events):
        self.on_hit()
        self.on_select(events)
        self.bounce()
        self.pos += self.vect * self.speed
        self.rect.center = self.pos


class Neutron(pygame.sprite.Sprite):
    def __init__(self, pos, init_vect, *groups) -> None:
        super().__init__(*groups)
        self.pos = pygame.Vector2(pos)
        self.vect = pygame.Vector2(init_vect).normalize()
        self.radius = 5
        self.size = pygame.Vector2(2 * self.radius)
        self.image = pygame.Surface(self.size)
        self.image.set_colorkey(BLACK)
        pygame.draw.circle(self.image, ALMOST_BLACK, self.size // 2, self.radius)
        self.rect = self.image.get_rect(center=self.pos)
        self.bounce_remain = 2

    def bounce(self):
        if A := (self.pos.x <= self.radius or self.pos.x >= SCREEN_WIDTH - self.radius):
            self.vect.x = -self.vect.x
        if B := (
            self.pos.y <= self.radius or self.pos.y >= SCREEN_HEIGHT - self.radius
        ):
            self.vect.y = -self.vect.y
        if any([A, B]):
            self.bounce_remain -= 1

    def out_of_bound_check(self):
        if (
            self.pos.x < -self.radius
            or self.pos.x > SCREEN_WIDTH + self.radius
            or self.pos.y < -self.radius
            or self.pos.y > SCREEN_HEIGHT + self.radius
        ):
            self.kill()

    def update(self) -> None:
        if self.bounce_remain > 0:
            self.bounce()
        else:
            self.out_of_bound_check()
        self.pos += self.vect * 2
        self.rect.center = self.pos


screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("测试")
clock = pygame.time.Clock()
smooth_fps = [FPS] * 60
pygame.init()

atom_group = pygame.sprite.Group()
for i in range(20):
    Atom(np.random.randint(100, 301, 2).tolist(), atom_group)

neutron_group = pygame.sprite.Group()

while True:
    clock.tick(FPS)
    delay = 1000 / clock.get_time()
    smooth_fps.append(delay)
    smooth_fps.pop(0)
    real_fps = math.floor(mean(smooth_fps))
    pygame.display.set_caption(f"FPS: [{real_fps}]")

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.dict["key"] == pygame.K_q:
                if FPS == 60:
                    FPS = 20
                elif FPS == 20:
                    FPS = 60

    screen.fill(WHITE)
    atom_group.update(events)
    neutron_group.update()

    atom_group.draw(screen)
    neutron_group.draw(screen)

    pygame.display.flip()
