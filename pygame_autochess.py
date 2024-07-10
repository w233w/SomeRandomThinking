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
LIGHT_RED = 255, 128, 128
BLUE = 0, 0, 255
YELLOW = 255, 255, 0
GREEN = 0, 255, 0


class Team(IntEnum):
    Team1 = -1
    Team2 = 1


class Unit(pygame.sprite.Sprite):
    id_gen = count()

    def __init__(self, pos, hp, speed, color, team, *groups) -> None:
        super().__init__(*groups)
        self.id = next(Unit.id_gen)
        self.r = 10
        self.size = pygame.Vector2(2 * self.r)
        self.image = pygame.Surface(self.size)
        self.image.set_colorkey(BLACK)
        self.pos = pygame.Vector2(pos)
        self.rect = self.image.get_rect(center=self.pos)

        self.hp = self.max_hp = hp
        self.speed = speed
        self.team: Team = team

        self.placed = False
        self.on_drag = False
        self.drag_delta = pygame.Vector2(0)

        self.init_time = 0

        self.render(color)

    @property
    def oppoment_team(self):
        return Team(-self.team)

    @property
    def die(self):
        return self.hp <= 0

    def render(self, color):
        self.image.fill(BLACK)
        pygame.draw.circle(self.image, color, self.size // 2, self.size[0] // 2)
        self.mask = pygame.mask.from_surface(self.image)
        pygame.draw.circle(
            self.image,
            RED if self.team == 1 else ALMOST_BLACK,
            self.size // 2,
            self.size[0] // 2,
            1,
        )

    def ready(self):
        self.placed = True
        self.init_time = pygame.time.get_ticks()

    def on_hit(self):  # 受击判定
        if hits := pygame.sprite.spritecollide(
            self, assist_groups[self.oppoment_team], True, pygame.sprite.collide_mask
        ):
            for hit in hits:
                self.hp -= hit.pow

    def targeting(self):  # 寻敌
        raise NotImplementedError("Method can't be called here")

    def moving(self):  # 移动
        raise NotImplementedError("Method can't be called here")

    def action(self):  # 行动
        raise NotImplementedError("Method can't be called here")

    def update(self, events) -> None:
        if not self.placed:
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if (
                        event.dict["button"] == 1
                        and self.pos.distance_to(event.dict["pos"]) <= self.r
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
        if self.die:
            self.kill()
        if self.placed:
            self.on_hit()
            self.targeting()
            self.moving()
            self.action()


class Arrow(pygame.sprite.Sprite):
    def __init__(
        self, pos: pygame.Vector2, dest: pygame.Vector2, power: float, *groups
    ) -> None:
        super().__init__(*groups)
        self.pos = pygame.Vector2(pos)
        self.vect = dest - self.pos
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


class Damage_spot(pygame.sprite.Sprite):
    def __init__(self, pos, pow, *groups) -> None:
        super().__init__(*groups)
        self.pos = pygame.Vector2(pos)
        self.pow = pow
        self.image = pygame.Surface([1, 1])
        self.image.set_colorkey(BLACK)
        self.image.fill(ALMOST_BLACK)
        self.mask = pygame.mask.from_surface(self.image)
        self.image.fill(BLACK)
        self.rect = self.image.get_rect(center=self.pos)
        self.init_time = pygame.time.get_ticks()

    def update(self, events) -> None:
        if pygame.time.get_ticks() - self.init_time > 100:
            self.kill()


class Archer(Unit):
    def __init__(self, pos, team, *groups) -> None:
        super().__init__(pos, 20, 1.5, YELLOW, team, *groups)
        self.target: Unit = None
        self.targeting_range = 400
        self.shoot_interval = 1000

    def ready(self):
        super().ready()
        self.last_shoot = self.init_time

    def targeting(self):
        target, dis = None, float("inf")
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
            if pygame.time.get_ticks() - self.last_shoot > self.shoot_interval:
                Arrow(self.pos, self.target.pos, 15, assist_groups[self.team])
                self.last_shoot = pygame.time.get_ticks()


class Knight(Unit):
    def __init__(self, pos, team, *groups) -> None:
        super().__init__(pos, 60, 1.2, BLUE, team, *groups)
        self.target: Unit = None
        self.targeting_range = 200
        self.hit_interval = 400
        self.last_hit = 0

    def ready(self):
        super().ready()
        self.last_hit = self.init_time

    def targeting(self):
        if self.target is not None:
            if self.target.hp <= 0:
                self.target = None
            elif self.pos.distance_to(self.target.pos) > self.targeting_range:
                self.target = None
        else:
            target, dis = None, float("inf")
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
            delta_pos = self.target.pos - self.pos
            if delta_pos.length() < self.r * 2:
                return
            self.pos += delta_pos.normalize() * self.speed
        self.rect.center = self.pos

    def action(self):
        if self.target is not None:
            if (
                pygame.time.get_ticks() - self.last_hit > self.hit_interval
                and self.pos.distance_to(self.target.pos) <= 2 * self.r
            ):
                Damage_spot(self.target.pos, 10, assist_groups[self.team])
                self.last_hit = pygame.time.get_ticks()


class Rider(Unit):
    def __init__(self, pos, team, *groups) -> None:
        super().__init__(pos, 35, 2, RED, team, *groups)
        self.target: Unit = None
        self.face_to = pygame.Vector2(0, self.team)
        self.max_turning_angle = 150
        self.angle_speed = self.max_turning_angle / FPS
        self.max_speed = 3.5
        self.charging = True
        self.last_charging = 0
        self.acc = 1.5 / FPS

    def ready(self):
        super().ready()
        self.last_charging = self.init_time
        self.last_hit = self.init_time

    def targeting(self):
        if self.target is not None:
            if self.target.die:
                self.target = None
        else:
            target, dis = None, -1
            for sp in army_groups[self.oppoment_team]:
                if self.pos.distance_to(sp.pos) >= dis:
                    target = sp
                    dis = self.pos.distance_to(sp.pos)
            self.target = target

    def moving(self):
        self.image.fill(BLACK)
        pygame.draw.circle(self.image, RED, self.size // 2, self.size[0] // 2)
        if self.target is not None:
            if (
                not self.charging
                and pygame.time.get_ticks() - self.last_charging > 4000
            ):
                self.targeting()
                self.charging = True
                self.last_charging = pygame.time.get_ticks()
            if self.charging and pygame.time.get_ticks() - self.last_charging > 3000:
                self.charging = False
                self.speed = 2
            if self.charging:
                self.speed = min(self.speed + self.acc, self.max_speed)

            dist = self.target.pos - self.pos
            delta_angle = (self.face_to.angle_to(dist) + 360) % 360
            shift = delta_angle
            if self.max_turning_angle < delta_angle <= 180:
                shift = self.max_turning_angle
            elif 180 < delta_angle <= 360 - self.max_turning_angle:
                shift = -self.max_turning_angle
            elif 360 - self.max_turning_angle < delta_angle:
                shift = delta_angle - 360
            rotate_speed = (self.angle_speed, -self.angle_speed)[shift <= 0]
            move_to = self.face_to.rotate(rotate_speed)

            # edge detect
            to_edge_x = min(abs(self.pos.x), abs(self.pos.x - SCREEN_WIDTH))
            to_edge_y = min(abs(self.pos.y), abs(self.pos.y - SCREEN_HEIGHT))
            if to_edge_x < SCREEN_WIDTH // 10 or to_edge_y < SCREEN_HEIGHT // 10:
                self.charging = False
                self.speed = 2
            real_move_to = move_to.normalize()
            self.pos += real_move_to * self.speed
            self.face_to = real_move_to
        else:
            self.pos += self.face_to * self.speed
        pygame.draw.line(
            self.image,
            ALMOST_BLACK,
            self.size // 2,
            self.size // 2 + self.face_to * 100,
        )
        self.rect.center = self.pos

    def action(self):
        if hits := pygame.sprite.spritecollide(
            self, army_groups[self.oppoment_team], False, pygame.sprite.collide_mask
        ):
            for sp in hits:
                Damage_spot(
                    sp.pos,
                    2 if self.speed > 3 else 1,
                    assist_groups[self.team],
                )


class LightRider(Rider):
    def __init__(self, pos, team, *groups) -> None:
        super().__init__(pos, team, *groups)
        self.render(LIGHT_RED)
        self.hp = 25
        self.max_speed = 4
        self.acc = 1.8 / FPS
        self.max_turning_angle = 180


screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("测试")
clock = pygame.time.Clock()
smooth_fps = [FPS] * 10
pygame.init()

army_groups = {Team.Team1: pygame.sprite.Group(), Team.Team2: pygame.sprite.Group()}
assist_groups = {Team.Team1: pygame.sprite.Group(), Team.Team2: pygame.sprite.Group()}
for i in range(7):
    Archer([50 + i * 50, 300], Team.Team1, army_groups[Team.Team1])
for i in range(6):
    Archer([75 + i * 50, 330], Team.Team1, army_groups[Team.Team1])
for i in range(3):
    Knight([100 + 100 * i, 250], Team.Team1, army_groups[Team.Team1])

Knight([200, 100], Team.Team2, army_groups[Team.Team2])
Knight([250, 100], Team.Team2, army_groups[Team.Team2])
Knight([230, 100], Team.Team2, army_groups[Team.Team2])
Rider([50, 50], Team.Team2, army_groups[Team.Team2])
Rider([100, 50], Team.Team2, army_groups[Team.Team2])
Rider([150, 50], Team.Team2, army_groups[Team.Team2])
Rider([200, 50], Team.Team2, army_groups[Team.Team2])
Rider([250, 50], Team.Team2, army_groups[Team.Team2])
Rider([300, 50], Team.Team2, army_groups[Team.Team2])
Rider([350, 50], Team.Team2, army_groups[Team.Team2])

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
