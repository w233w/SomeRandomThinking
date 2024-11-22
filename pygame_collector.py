from random import randint
from typing import Any
import pygame

WORLD_SIZE = 400, 400
WORLD = pygame.Rect([0, 0], WORLD_SIZE)
BEADS = 5000


class P(pygame.sprite.Sprite):
    def __init__(self, *groups) -> None:
        super().__init__(*groups)
        self.radius: int = 10
        self.size: pygame.Vector2 = pygame.Vector2(2 * self.radius)
        self.image: pygame.Surface = pygame.Surface(self.size)
        self.image.set_colorkey([0, 0, 0])
        self.pos: pygame.Vector2 = pygame.Vector2(200)
        self.rect: pygame.Rect = self.image.get_rect(center=self.pos)

        self.render()

        self.score = 0

    def render(self, color=[1, 1, 1]) -> None:
        self.image.fill([0, 0, 0])
        pygame.draw.circle(self.image, color, self.size // 2, self.radius)

    def move(self) -> None:
        w = pygame.key.get_pressed()[pygame.K_w]
        s = pygame.key.get_pressed()[pygame.K_s]
        a = pygame.key.get_pressed()[pygame.K_a]
        d = pygame.key.get_pressed()[pygame.K_d]
        go = pygame.Vector2(0)
        go += w * pygame.Vector2(0, -1)
        go += s * pygame.Vector2(0, 1)
        go += a * pygame.Vector2(-1, 0)
        go += d * pygame.Vector2(1, 0)
        if go != pygame.Vector2(0):
            go.normalize_ip()
        self.pos += go
        self.rect.center = self.pos

    def update(self, *args: Any, **kwargs: Any) -> None:
        self.move()
        det_rad = 60
        self.radius += det_rad
        hit: list[B] = pygame.sprite.spritecollide(
            self, bs, False, pygame.sprite.collide_circle
        )
        self.radius -= det_rad
        for sp in hit:
            sp.on_collect = True
            sp.render([0, 255, 0])

        if self.score == BEADS:
            self.render([0, 255, 0])


class B(pygame.sprite.Sprite):
    def __init__(self, pos: pygame.Vector2, *groups) -> None:
        super().__init__(*groups)
        self.radius: int = 2
        self.size: pygame.Vector2 = pygame.Vector2(2 * self.radius)
        self.image: pygame.Surface = pygame.Surface(self.size)
        self.image.set_colorkey([0, 0, 0])
        self.pos: pygame.Vector2 = pygame.Vector2(pos)
        self.rect: pygame.Rect = self.image.get_rect(center=self.pos)

        self.render()

        self.on_collect = False

    def render(self, color=[255, 0, 0]) -> None:
        self.image.fill([0, 0, 0])
        pygame.draw.circle(self.image, color, self.size // 2, self.radius)

    def update(self, *args: Any, **kwargs: Any) -> None:
        if self.on_collect:
            target: P = pg.sprite
            if pygame.sprite.collide_circle(self, target):
                self.kill()
                target.score += 1
                return
            direction = target.pos - self.pos
            self.pos += direction.normalize() * 1.4
            self.rect.center = self.pos


pygame.init()
screen = pygame.display.set_mode(WORLD_SIZE)
clock = pygame.time.Clock()

pg = pygame.sprite.GroupSingle()
P(pg)
bs = pygame.sprite.Group()
for i in range(BEADS):
    B(pygame.Vector2(randint(0, 400), randint(0, 400)), bs)

p = (0, 0)
while True:
    delta = clock.tick(1000)
    p = (p[0] * p[1] + delta) / (p[1] + 1), p[1] + 1
    pygame.display.set_caption(f"FPS: {1000/p[0]:.2f}")
    screen.fill([255, 255, 255])
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    pg.update()
    bs.update()
    pg.draw(screen)
    bs.draw(screen)

    pygame.display.flip()
