import pygame
import random
from itertools import product

SCREEN_WIDTH = SCREEN_HEIGHT = 400
SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT
SCREEN_VSIZE = pygame.Vector2(SCREEN_SIZE)

FPS = 60

BLACK = 0, 0, 0
ALMOST_BLACK = 1, 1, 1
WHITE = 255, 255, 255
ARC = 0, 128, 128
AQUA = 0, 192, 192


class Blot(pygame.sprite.Sprite):
    def __init__(self, pos, dect, *groups) -> None:
        super().__init__(*groups)
        self.size = pygame.Vector2(5)
        self.dect = dect
        self.pos = pos
        self.pos = SCREEN_VSIZE / 2
        self.image = pygame.Surface(self.size * 2)
        self.image.set_colorkey(BLACK)
        pygame.draw.circle(self.image, ALMOST_BLACK, self.size, self.size.x)
        self.rect = self.image.get_rect(center=self.pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = 50
        self.init_time = pygame.time.get_ticks()

    def update(self, events, delta) -> None:
        if pygame.time.get_ticks() - self.init_time > 4000:
            self.kill()
        self.pos += self.dect * self.speed * delta / 1000
        self.rect.center = self.pos


class WaterBall(pygame.sprite.Sprite):
    def __init__(self, pos, dect, *groups) -> None:
        super().__init__(*groups)
        if dect == pygame.Vector2(0):
            self.size = pygame.Vector2(20)
        else:
            self.size = pygame.Vector2(5)
        self.dect = dect
        self.pos = pos
        self.color = AQUA
        self.image = pygame.Surface(self.size * 2)
        self.image.set_colorkey(BLACK)
        pygame.draw.circle(self.image, self.color, self.size, self.size.x)
        self.rect = self.image.get_rect(center=self.pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = 120
        self.init_time = pygame.time.get_ticks()

    def redraw(self):
        pygame.draw.circle(self.image, self.color, self.size, self.size.x)

    def update(self, events, delta) -> None:
        if self.size == pygame.Vector2(5):
            if pygame.time.get_ticks() - self.init_time > 1000:
                WaterBall(self.pos, pygame.Vector2(0), wb_g)
                self.kill()
        elif self.size == pygame.Vector2(20):
            if pygame.time.get_ticks() - self.init_time > 5000:
                self.kill()
        self.pos += self.dect * self.speed * delta / 1000
        self.rect.center = self.pos


class Chain(pygame.sprite.Sprite):
    def __init__(self, *groups) -> None:
        super().__init__(*groups)
        self.size = SCREEN_SIZE
        self.image = pygame.Surface(self.size)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect(center=SCREEN_VSIZE / 2)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, events, delta) -> None:
        self.image.fill(BLACK)
        sps = b_g.sprites()
        size = len(sps)
        if size <= 1:
            return
        for i, j in product(range(size), range(size)):
            if j <= i:
                continue
            dis = sps[i].pos.distance_to(sps[j].pos)
            if dis > 60 or dis < 10:
                continue
            inter = (sps[j].pos - sps[i].pos) / int(dis)
            dots = (
                [sps[i].pos]
                + [
                    (sps[i].pos + inter * m)
                    + pygame.Vector2(random.randint(-3, 3)).rotate(
                        random.random() * 360
                    )
                    for m in sorted(random.sample(range(int(dis)), k=round(dis / 24)))
                ]
                + [sps[j].pos]
            )
            pygame.draw.lines(self.image, ARC, False, dots)
        self.mask = pygame.mask.from_surface(self.image)


class Center(pygame.sprite.Sprite):
    def __init__(self, *groups) -> None:
        super().__init__(*groups)
        self.size = pygame.Vector2(20)
        self.pos = SCREEN_VSIZE / 2
        self.image = pygame.Surface(self.size)
        self.image.set_colorkey(BLACK)
        self.image.fill(ALMOST_BLACK)
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, events: list[pygame.event.Event], delta) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                dect = pygame.Vector2(*pygame.mouse.get_pos()) - SCREEN_VSIZE / 2
                if dect == pygame.Vector2(0):
                    return
                dect = dect.normalize()
                if event.dict["key"] == pygame.K_1:
                    Blot(SCREEN_VSIZE / 2, dect, b_g)
                elif event.dict["key"] == pygame.K_2:
                    Blot(SCREEN_VSIZE / 2, dect, b_g)
                elif event.dict["key"] == pygame.K_3:
                    Blot(SCREEN_VSIZE / 2, dect.rotate(-10), b_g)
                    Blot(SCREEN_VSIZE / 2, dect.rotate(10), b_g)
                elif event.dict["key"] == pygame.K_4:
                    WaterBall(SCREEN_VSIZE / 2, dect, wb_g)


screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("测试")
clock = pygame.time.Clock()
pygame.init()

p_g = pygame.sprite.GroupSingle()
Center(p_g)
b_g = pygame.sprite.Group()
wb_g = pygame.sprite.Group()
c_g = pygame.sprite.GroupSingle()
Chain(c_g)

while True:
    clock.tick(FPS)
    delta = clock.get_time()
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    screen.fill(WHITE)

    wb_g.update(events, delta)
    p_g.update(events, delta)
    b_g.update(events, delta)
    c_g.update(events, delta)

    light = pygame.sprite.groupcollide(
        wb_g, c_g, False, False, pygame.sprite.collide_mask
    )
    for node in light:
        if node.color == ARC:
            continue
        node.color = ARC
        node.redraw()

    wb_g.draw(screen)
    p_g.draw(screen)
    b_g.draw(screen)
    c_g.draw(screen)

    pygame.display.flip()
