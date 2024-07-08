import pygame
import math
import random
from statistics import mean
from itertools import count
from enum import IntEnum

# 自走棋
# unfinished

SCREEN_WIDTH = SCREEN_HEIGHT = 400
SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT

FPS = 60

BLACK = 0, 0, 0
ALMOST_BLACK = 1, 1, 1
COLOR = 29, 31, 211
WHITE = 255, 255, 255
RED = 255, 0, 0
BLUE = 0, 0, 255
YELLOW = 255, 255, 0
GREEN = 0, 255, 0


class Team(IntEnum):
    Team1 = -1
    Team2 = 1


class Unit(pygame.sprite.Sprite):
    id_gen = count()

    def __init__(self, pos, hp, speed, team, *groups) -> None:
        super().__init__(*groups)
        self.id = next(Unit.id_gen)
        self.size = pygame.Vector2(20)
        self.image = pygame.Surface(self.size)
        self.image.set_colorkey(BLACK)
        self.pos = pygame.Vector2(pos)
        self.rect = self.image.get_rect(center=self.pos)

        pygame.draw.circle(self.image, RED, self.size // 2, self.size[0] // 2)
        self.mask = pygame.mask.from_surface(self.image)

        self.hp = hp
        self.speed = speed
        self.team: Team = team

        self.placed = False
        self.on_drag = False
        self.drag_delta = pygame.Vector2(0)

        self.init_time = 0

    @property
    def oppoment_team(self):
        return Team(-self.team)

    def ready(self):
        self.placed = True
        self.init_time = pygame.time.get_ticks()

    def targeting(self):  # 寻敌
        raise NotImplementedError("Method can't be called here")

    def moving(self):  # 寻敌
        raise NotImplementedError("Method can't be called here")

    def action(self):  # 行动
        raise NotImplementedError("Method can't be called here")

    def update(self, events) -> None:
        if not self.placed:
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if (
                        event.dict["button"] == 1
                        and self.pos.distance_to(event.dict["pos"]) <= 20
                    ):
                        self.on_drag = True
                        self.drag_delta = self.pos - pygame.Vector2(event.dict["pos"])
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.dict["button"] == 1:
                        self.on_drag = False
                        self.drag_delta = pygame.Vector2(0)
            if self.on_drag:
                self.pos = pygame.Vector2(pygame.mouse.get_pos()) + self.drag_delta
                self.rect.center = self.pos
        if self.hp <= 0:
            self.kill()


class Arrow(pygame.sprite.Sprite):
    def __init__(
        self, pos: pygame.Vector2, dist: pygame.Vector2, power: float, *groups
    ) -> None:
        super().__init__(*groups)
        self.pos = pygame.Vector2(pos)
        self.vect = dist - self.pos
        while self.vect.length() == 0:
            self.vect = pygame.Vector2(
                random.randint(-999, 999), random.randint(-999, 999)
            )
        self.pow = power
        self.size = pygame.Vector2(15)
        self.image = pygame.Surface(self.size)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect(center=self.pos)
        pygame.draw.line(
            self.image,
            ALMOST_BLACK,
            self.size // 2,
            self.size // 2 + self.vect.normalize() * 10,
            2,
        )
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, events):
        self.pos += self.vect.normalize() * 4
        self.rect.center = self.pos
        if (
            self.pos.x < -self.size.x
            or self.pos.x > SCREEN_WIDTH + self.size.x
            or self.pos.y < -self.size.y
            or self.pos.y > SCREEN_HEIGHT + self.size.y
        ):
            self.kill()


class Archer(Unit):
    def __init__(self, pos, team, *groups) -> None:
        super().__init__(pos, 20, 2, team, *groups)
        pygame.draw.circle(self.image, YELLOW, self.size // 2, self.size[0] // 2)
        self.target: Unit = None
        self.targeting_range = 200

    def ready(self):
        super().ready()
        self.last_shoot = self.init_time

    def targeting(self):
        if self.target is None:
            target, dis = None, 9999
            for sp in army_groups[self.oppoment_team]:
                if (
                    self.pos.distance_to(sp.pos) < self.targeting_range
                    and self.pos.distance_to(sp.pos) <= dis
                ):
                    target = sp
                    dis = self.pos.distance_to(sp.pos)
            self.target = target

    def moving(self):
        if self.target is None:
            self.pos += pygame.Vector2(0, self.team) * self.speed
            self.rect.center = self.pos

    def action(self):
        if self.target is not None:
            if pygame.time.get_ticks() - self.last_shoot > 1000:
                Arrow(self.pos, self.target.pos, 5, assist_groups[self.team])
                self.last_shoot = pygame.time.get_ticks()

    def update(self, events) -> None:
        super().update(events)
        if self.placed:
            self.targeting()
            self.moving()
            self.action()


class Knight(Unit):
    def __init__(self, pos, team, *groups) -> None:
        super().__init__(pos, 60, 1.2, team, *groups)
        pygame.draw.circle(self.image, BLUE, self.size // 2, self.size[0] // 2)
        self.target: Unit = None
        self.targeting_range = 400

    def targeting(self):
        if self.target is not None:
            if self.target.hp <= 0:
                self.target = None
            if self.pos.distance_to(self.target.pos) > self.targeting_range:
                self.target = None
        elif self.target is None:
            target, dis = None, 9999
            for sp in army_groups[self.oppoment_team]:
                if (
                    self.pos.distance_to(sp.pos) < self.targeting_range
                    and self.pos.distance_to(sp.pos) <= dis
                ):
                    target = sp
                    dis = self.pos.distance_to(sp.pos)
            self.target = target

    def moving(self):
        if self.target is None:
            self.pos += pygame.Vector2(0, self.team) * self.speed
        else:
            self.pos += (self.target.pos - self.pos).normalize() * self.speed
        self.rect.center = self.pos

    def action(self):
        pass

    def update(self, events) -> None:
        super().update(events)
        if self.placed:
            self.targeting()
            self.moving()
            self.action()


class Rider(Unit):
    def __init__(self, pos, team, *groups) -> None:
        super().__init__(pos, 30, 5, team, *groups)


screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("测试")
clock = pygame.time.Clock()
smooth_fps = [FPS] * 10
pygame.init()

army_groups = {Team.Team1: pygame.sprite.Group(), Team.Team2: pygame.sprite.Group()}
assist_groups = {Team.Team1: pygame.sprite.Group(), Team.Team2: pygame.sprite.Group()}
Archer([200, 200], Team.Team1, army_groups[Team.Team1])
Knight([100, 100], Team.Team2, army_groups[Team.Team2])

while True:
    clock.tick(FPS)
    delay = 1000 / clock.get_time()
    smooth_fps.append(delay)
    smooth_fps.pop(0)
    real_fps = math.floor(mean(smooth_fps))
    pygame.display.set_caption(f"FPS: {real_fps}")

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.dict["key"] == pygame.K_q:
                for army in army_groups:
                    for sp in army_groups[army]:
                        sp.ready()

    for army in army_groups:
        army_groups[army].update(events)
    for assist in assist_groups:
        assist_groups[assist].update(events)

    screen.fill(WHITE)

    for army in army_groups:
        army_groups[army].draw(screen)
    for assist in assist_groups:
        assist_groups[assist].draw(screen)

    pygame.display.flip()
