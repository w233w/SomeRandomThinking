from typing import Tuple, Literal, Self
import pygame
from pygame import Vector2
from statistics import mean
import math
import random


# 准备仿mmo的boss战做机制挑战
# boss1号，共2阶段
# 阶段一：
# boss周围出现4面力场。触碰扣血，会阻挡远程箭矢。
# 同时4个角刷新4个不会动的add。5秒后add启动。Boss每8秒会随机任选两个add。该选择在add启动时立即生效一次。
# 在add全部失能前，选择最多发生三次。
# add位置样例，数字代表add位置。
# 0    1    2
#
# 7   Bos   3
#
# 6    5    4
# 每个被选中的add将持有一个端点5秒。未持有端点者无敌。同一批被选择的端点间出现连一条线，会对玩家造成伤害。
# 同一时间所有add会将手中的端点随机发射给另一个add。同一对端点不会互相发射。
# add不会死亡，而是失能。敌人可以持有复数个端点。发射到另一个敌人需要花费约1秒。
# add全部失能时，所有端点立即消失。若最后两个失能的add相邻则相连形成的平行线最近的boss力场会消失。
# 所有力场存在时，boss会间歇性的打出aoe和随机的子弹。平均3秒一个aoe，0.5秒六个随机弹。add25秒后恢复。
# 任意力场破碎后，单次，在所有破碎力场的方向上持续喷出大量子弹。
# 第一面力场破碎后，随机子弹的频率提升至0.4秒。boss开始倒计时60秒。时间到时力场恢复。add恢复时间-2秒。
# 第二面力场破碎后，随机子弹的频率提升至0.3秒。倒计时变为当前的80%或20秒，取较高的值。add恢复时间-2秒。
# 第三面力场破碎后，随机子弹的频率提升至0.2秒。aoe的频率提升至1.5秒。倒计时变为当前的50%或10秒，取较高的值。add恢复时间-2秒。
# 如果做到力场完全破碎，则boss会完全失能15秒。add直到boss
# boss血量降低到50%时赋予所有单位无敌效果，召唤的敌人消失，端点消失，玩家将被击飞至地图边缘。并在1秒后进入阶段二。
# 阶段二：
# 玩家失去闪避能力。
# boss在四个角，四条边的中点召唤8个不动的敌人。每5秒，boss选择两组相邻且不重复的四个敌人赋予端点。


WIDTH = HEIGHT = 400
FPS = 60.0
SIZE = WIDTH, HEIGHT
VSIZE = Vector2(SIZE)

# 颜色常量
# BACKGROUND_COLOR = 153, 255, 153
BACKGROUND_COLOR = 255, 255, 255
BLACK = 0, 0, 0
GRAY = 127, 127, 127
ALMOST_BLACK = 1, 1, 1
WHITE = 255, 255, 255
RED = 255, 0, 0
BLUE = 0, 0, 255
YELLOW = 255, 255, 0
PINK = 255, 127, 127
ORANGE = 255, 127, 0


class Boss(pygame.sprite.Sprite):
    def __init__(self, *groups) -> None:
        super().__init__(*groups)
        self.pos = VSIZE // 2
        self.size = VSIZE // 2
        self.image = pygame.Surface(self.size)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect(center=self.pos)
        pygame.draw.circle(self.image, ORANGE, self.size // 2, WIDTH // 20)
        self.mask = pygame.mask.from_surface(self.image)
        self.wall_status = {"n": True, "e": True, "w": True, "s": True}
        self.walls = pygame.sprite.Group()
        Wall(self.rect.topleft, self.rect.topright, self.walls, enemy_unit)
        Wall(self.rect.topleft, self.rect.bottomleft, self.walls, enemy_unit)
        Wall(self.rect.topright, self.rect.bottomright, self.walls, enemy_unit)
        Wall(self.rect.bottomleft, self.rect.bottomright, self.walls, enemy_unit)

        self.init_time = pygame.time.get_ticks()

        self.hp = 1000
        self.stage = 1

        self.count_down_started = False
        self.count_down_started_at = 0

        self.bullet_interval = 500
        self.last_bullet = self.init_time
        self.bullet_init_angle = 180
        self.bullet_init_angle_step = 6
        self.bullet_angle_acc = 0.5

        self.shock_wave_interval = 3000
        self.last_shock_wave = self.init_time

        self.last_summon = 0
        self.addons_status_watching_list = {
            1: [0, 2, 4, 6],
            2: [0, 1, 2, 3, 4, 5, 6, 7],
        }

        self.addon_status = {}

        self.addons: pygame.sprite.Group[Addon] = pygame.sprite.Group()
        for addon_pos in self.addons_status_watching_list[self.stage]:
            Addon(addon_pos, self.addons, enemy_unit)

    def update(self, game_events) -> None:
        current_time = pygame.time.get_ticks()

        if hits := pygame.sprite.spritecollide(
            self, player_bullet, True, pygame.sprite.collide_mask
        ):
            for hit in hits:
                self.hp -= hit.pow
        if hits := pygame.sprite.spritecollide(
            self, player_non_bullet, False, pygame.sprite.collide_mask
        ):
            for hit in hits:
                self.hp -= hit.pow

        for add in self.addons:
            self.addon_status[add.pos_id] = add.active
            add.recover_time = 25000 - 2000 * len(self.walls)

        if not any(self.addon_status.values()):
            random.choice(self.walls.sprites()).kill()
            for add in self.addons:
                add.reset()

        if current_time - self.last_bullet > self.bullet_interval:
            self.last_bullet = current_time
            self.bullet_init_angle_step += self.bullet_angle_acc
            self.bullet_init_angle += self.bullet_init_angle_step
            angle = random.random() * 360
            for i in range(6):
                Lightblot(
                    self.pos,
                    Vector2(-1, 0).rotate((angle + i * 60) % 360),
                    enemy_bullet,
                )
        if current_time - self.last_shock_wave > self.shock_wave_interval:
            self.last_shock_wave = current_time
            Shockwave(self.pos, self.size.x / 2, enemy_non_bullet)


# TODO 端点类
class ENode(pygame.sprite.Sprite):
    def __init__(self, *groups) -> None:
        super().__init__(*groups)
        self.partner = None

    def set_partner(self, partner):
        self.partner = partner

    def update(self, game_events) -> None:
        if self.partner is None:
            self.kill()


class LightChain(pygame.sprite.Sprite):
    def __init__(self, *groups) -> None:
        super().__init__(*groups)


class Lightblot(pygame.sprite.Sprite):
    def __init__(self, pos: Vector2, direction: Vector2, *groups) -> None:
        super().__init__(*groups)
        self.pos = Vector2(pos)
        self.direction = direction
        self.image = pygame.Surface([5, 5])
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect(center=self.pos)
        pygame.draw.circle(self.image, ALMOST_BLACK, [2.5, 2.5], 2.5)

    def update(self, game_events):
        self.pos += self.direction.normalize()
        self.rect.center = self.pos
        if self.pos.x < -WIDTH / 2 or self.pos.x > WIDTH * 1.5:
            self.kill()
        if self.pos.y < -WIDTH / 2 or self.pos.y > HEIGHT * 1.5:
            self.kill()


class Shockwave(pygame.sprite.Sprite):
    def __init__(self, pos: pygame.Vector2, radius: float, *groups) -> None:
        super().__init__(*groups)
        self.pos = Vector2(pos)
        self.radius = radius
        self.image = pygame.Surface([2 * self.radius, 2 * self.radius])
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect(center=self.pos)
        self.init_time = pygame.time.get_ticks()
        self.hitted = []

    def update(self, game_events) -> None:
        current_time = pygame.time.get_ticks() - self.init_time
        if current_time > 800:
            self.kill()
            return
        self.image.fill(BLACK)
        r = self.radius * current_time / 800
        pygame.draw.circle(
            self.image,
            BLUE,
            [self.radius, self.radius],
            r,
            max(1, 12 - round(12 * current_time / 800)),
        )
        self.mask = pygame.mask.from_surface(self.image)


class Arrow(pygame.sprite.Sprite):
    def __init__(self, pos: Vector2, power: float, *groups) -> None:
        super().__init__(*groups)
        self.pos = Vector2(pos)
        self.vect = pygame.mouse.get_pos() - self.pos
        self.pow = power
        self.img_center = VSIZE // 10
        self.image = pygame.Surface(self.img_center)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect(center=self.pos)
        pygame.draw.line(
            self.image,
            ALMOST_BLACK,
            self.img_center // 2,
            self.img_center // 2 + self.vect.normalize() * 10,
        )
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, game_events):
        self.pos += self.vect.normalize() * 2
        self.rect.center = self.pos
        # TODO 弓箭的射程？
        if (
            self.pos.x < -WIDTH // 20
            or self.pos.x > WIDTH + WIDTH // 20
            or self.pos.y < -HEIGHT // 20
            or self.pos.y > HEIGHT + HEIGHT // 20
        ):
            self.kill()


# 近战弹道
# Combo -> 0：逆时针横扫，1：顺时针横扫，2：直刺。
class Sword(pygame.sprite.Sprite):
    pow_map = {0: 6 / FPS, 1: 12 / FPS, 2: 24 / FPS}
    duration_map = {0: 400, 1: 400, 2: 300}

    def __init__(self, pos: Vector2, combo: Literal[0, 1, 2], *groups) -> None:
        super().__init__(*groups)
        # 不封装Vector2会导致player_pos同步玩家位置，这正是我想要的。
        self.player_pos = pos
        self.length = WIDTH // 10
        self.image = pygame.Surface(VSIZE // 5)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect(center=self.player_pos)

        self.mouse_pos_when_trigger = Vector2(pygame.mouse.get_pos())
        self.vect = (self.mouse_pos_when_trigger - self.player_pos).normalize()
        self.angle = self.vect.angle_to(Vector2(-1, 0))

        self.combo = combo
        self.init_time = pygame.time.get_ticks()

        self.duration = Sword.duration_map[self.combo]
        self.pow = Sword.pow_map[self.combo]

    def update(self, game_events):
        time_passed = pygame.time.get_ticks() - self.init_time
        progress = time_passed / self.duration
        if progress >= 1:
            self.kill()
        self.image.fill(BLACK)
        self.rect.center = self.player_pos
        match self.combo:
            case 0:
                angle = (self.angle - 60 + 120 * progress) % 360
                pygame.draw.line(
                    self.image,
                    GRAY,
                    VSIZE // 10,
                    VSIZE // 10 + Vector2(-1, 0).rotate(-angle) * self.length,
                    3,
                )
            case 1:
                angle = (self.angle + 60 - 120 * progress) % 360
                pygame.draw.line(
                    self.image,
                    GRAY,
                    VSIZE // 10,
                    VSIZE // 10 + Vector2(-1, 0).rotate(-angle) * self.length,
                    3,
                )
            case 2:
                pygame.draw.line(
                    self.image,
                    GRAY,
                    VSIZE // 10,
                    VSIZE // 10 + self.vect * progress * self.length,
                    3,
                )
        self.mask = pygame.mask.from_surface(self.image)


class Wall(pygame.sprite.Sprite):
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int], *groups) -> None:
        super().__init__(*groups)
        start: Vector2 = Vector2(start)
        end: Vector2 = Vector2(end)
        del_x, del_y = abs(start.x - end.x), abs(start.y - end.y)
        width: int = (((round(del_x) + 5) >> 1) << 1) + 1
        height: int = (((round(del_y) + 5) >> 1) << 1) + 1
        self.image = pygame.Surface([width, height])
        self.image.set_colorkey(BLACK)
        self.center = (start + end) / 2
        self.rect = self.image.get_rect(center=self.center)
        pygame.draw.line(
            self.image,
            ALMOST_BLACK,
            start - Vector2(self.rect.topleft),
            end - Vector2(self.rect.topleft),
        )
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, game_events) -> None:
        pygame.sprite.spritecollide(
            self, player_bullet, True, pygame.sprite.collide_mask
        )


class Addon(pygame.sprite.Sprite):
    def __init__(self, pos_id: Literal[0, 1, 2, 3, 4, 5, 6, 7], *groups) -> None:
        super().__init__(*groups)
        self.pos_id = pos_id
        self.pos = Vector2(0, 0)
        match pos_id:
            case 0, _:
                self.pos = Vector2(0, 0)
            case 1:
                self.pos = Vector2(WIDTH // 2, 0)
            case 2:
                self.pos = Vector2(WIDTH, 0)
            case 3:
                self.pos = Vector2(WIDTH, HEIGHT // 2)
            case 4:
                self.pos = Vector2(WIDTH, HEIGHT)
            case 5:
                self.pos = Vector2(WIDTH // 2, HEIGHT)
            case 6:
                self.pos = Vector2(0, HEIGHT)
            case 7:
                self.pos = Vector2(0, HEIGHT // 2)
        self.img_center = VSIZE // 20
        self.radius = WIDTH // 20
        self.image = pygame.Surface(VSIZE // 10)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect(center=self.pos)

        self.render(YELLOW)
        self.mask = pygame.mask.from_surface(self.image)

        self.hp = self.max_hp = 4

        self.last_time_not_active = pygame.time.get_ticks()
        self.recover_time = 25000
        self.active = True

        self.nodes = pygame.sprite.Group()

    def render(self, color: Tuple[int, int, int] = None):
        if color is not None:
            self.color = color
        pygame.draw.circle(self.image, self.color, self.img_center, self.radius)

    def force_kill(self):
        self.kill()

    def reset(self):
        self.render(YELLOW)
        self.active = True
        self.hp = self.max_hp

    def update(self, game_events):
        # if self.nodes:
        if hits := pygame.sprite.spritecollide(
            self, player_bullet, True, pygame.sprite.collide_mask
        ):
            for hit in hits:
                self.hp -= hit.pow
        if hits := pygame.sprite.spritecollide(
            self, player_non_bullet, False, pygame.sprite.collide_mask
        ):
            for hit in hits:
                self.hp -= hit.pow
        current_time = pygame.time.get_ticks()
        if self.active and self.hp <= 0:
            self.render(GRAY)
            self.active = False
            self.last_time_not_active = current_time
        if (
            not self.active
            and current_time - self.last_time_not_active > self.recover_time
        ):
            self.reset()


class Player(pygame.sprite.Sprite):
    def __init__(self, pos: Vector2, *groups) -> None:
        super().__init__(*groups)
        self.hp = 100
        self.color = RED

        self.radius = WIDTH // 40
        self.diameter = WIDTH // 20
        self.pos = pos
        self.img_center = Vector2(self.diameter, self.diameter)
        self.image = pygame.Surface(self.img_center)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect(center=self.pos)
        pygame.draw.circle(self.image, RED, self.img_center // 2, self.radius)
        self.mask = pygame.mask.from_surface(self.image)
        self.font = pygame.font.SysFont("simhei", self.radius)
        self.render()

        self.drawing_bow = False
        self.start_draw = 0
        self.dashed = False
        self.last_dash = 0
        self.on_melee = False
        self.start_melee = 0
        self.last_melee = 0
        self.on_combo = 0

        self.last_on_hit = pygame.time.get_ticks()

        self.check_melee = pygame.sprite.Group()

    def _player_control(self):
        left = pygame.key.get_pressed()[pygame.K_a]
        up = pygame.key.get_pressed()[pygame.K_w]
        down = pygame.key.get_pressed()[pygame.K_s]
        right = pygame.key.get_pressed()[pygame.K_d]
        speed_boost = 2
        if self.drawing_bow:
            speed_boost = 1
        global_boost = WIDTH / 400
        del_x = right - left
        del_y = down - up
        # 限制玩家不能离开屏幕
        one_pixel_boost = self.radius + 1
        if self.pos.x < one_pixel_boost and del_x < 0:
            del_x = 0
            self.pos.x = self.radius
        elif self.pos.x > WIDTH - one_pixel_boost and del_x > 0:
            del_x = 0
            self.pos.x = WIDTH - self.radius
        if self.pos.y < one_pixel_boost and del_y < 0:
            del_y = 0
            self.pos.y = self.radius
        elif self.pos.y > HEIGHT - one_pixel_boost and del_y > 0:
            del_y = 0
            self.pos.y = HEIGHT - self.radius
        speed = Vector2(del_x, del_y)
        if speed.length() != 0:
            speed.normalize_ip()
        return speed_boost * global_boost * speed

    def render(self, color: Tuple[int, int, int] = None):
        hp_text = self.font.render(str(self.hp), True, ALMOST_BLACK, None)
        text_size = self.font.size(str(self.hp))
        if color is not None:
            self.color = color
        pygame.draw.circle(self.image, self.color, self.img_center // 2, self.radius)
        self.image.blit(
            hp_text, [self.radius - text_size[0] / 2, self.radius - text_size[1] / 2]
        )

    def update(self, game_events):
        if self.hp <= 0:
            Player(Vector2(200, 380), player_unit)
            self.kill()

        current_time = pygame.time.get_ticks()

        # 处理受伤
        # TODO 数值处理
        # TODO 是否需要受击后无敌0.5秒?
        if pygame.sprite.spritecollide(
            self, enemy_unit, False, pygame.sprite.collide_mask
        ):
            self.hp -= 2
            self.render()
            self.last_on_hit = current_time
        if pygame.sprite.spritecollide(
            self, enemy_bullet, True, pygame.sprite.collide_mask
        ):
            self.hp -= 2
            self.render()
            self.last_on_hit = current_time
        if pygame.sprite.spritecollide(
            self, enemy_non_bullet, False, pygame.sprite.collide_mask
        ):
            self.hp -= 2
            self.render()
            self.last_on_hit = current_time

        # 呼吸回血
        if current_time - self.last_on_hit > 6000 and self.hp < 80:
            self.hp += 1
            self.render()

        # 射击能力
        # 右键拉弓
        if not self.drawing_bow and pygame.mouse.get_pressed(3)[-1]:
            self.drawing_bow = True
            self.start_draw = current_time
        # 松开射箭
        elif self.drawing_bow and not pygame.mouse.get_pressed(3)[-1]:
            drawing_time = current_time - self.start_draw
            self.drawing_bow = False
            x = min(1.0, drawing_time / 1000)
            bow_power = 1 - math.sqrt(1 - x**2)  # TODO 弓箭威力算法
            Arrow(self.pos, bow_power + 9999, player_bullet)  # TODO 测试用数据

        # 近战能力
        # TODO 左键近战，未完成的内容：攻击间隔，combo允许间隔
        if not self.on_melee and pygame.mouse.get_pressed(3)[0]:
            self.on_melee = True
            self.start_melee = current_time
            Sword(self.pos, self.on_combo, player_non_bullet, self.check_melee)
        elif self.on_melee and len(self.check_melee) <= 0:
            self.on_melee = False
            self.on_combo += 1
            self.on_combo %= 3

        # 闪避能力：
        next_move = self._player_control()
        # 空格闪避
        if not self.dashed and pygame.key.get_pressed()[pygame.K_SPACE]:
            next_move *= 40
            self.dashed = True
            self.last_dash = current_time
            self.render(PINK)
        # 闪避充能两秒
        elif self.dashed and current_time - self.last_dash > 2000:
            self.dashed = False
            self.render(RED)

        # 移动能力
        self.pos += next_move
        self.rect.center = self.pos


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos: Vector2, *groups) -> None:
        super().__init__(*groups)
        self.pos = pos
        self.size = VSIZE // 20
        self.image = pygame.Surface(self.size)
        self.image.set_colorkey(BLACK)
        pygame.draw.circle(self.image, YELLOW, self.size / 2, 10)
        self.rect = self.image.get_rect(center=self.pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.hp = 10
        self.count = 0
        self.move_sppeed = Vector2(1, 0)

    def update(self, game_events) -> None:
        for hit in pygame.sprite.spritecollide(
            self, player_bullet, True, pygame.sprite.collide_mask
        ):
            self.hp -= hit.pow
            self.hp = round(self.hp, 3)
        for hit in pygame.sprite.spritecollide(
            self, player_non_bullet, False, pygame.sprite.collide_mask
        ):
            self.hp -= hit.pow
            self.hp = round(self.hp, 3)

        if self.count < 100:
            self.pos += self.move_sppeed
            self.count += 1
        else:
            self.move_sppeed = -self.move_sppeed
            self.count = 0
        self.rect.center = self.pos
        if self.hp <= 0:
            Enemy(Vector2(100, 100), enemy_unit)
            self.kill()


# Init pygame & Crate screen
pygame.init()

screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption("测试")
clock = pygame.time.Clock()

smooth_fps = [FPS] * 10

# wall = pygame.sprite.Group()
# Obstacles(wall)
# Obstacles2(wall)

# gruop 设计，由单位来处理子弹信息，是否kill是否受伤等。
# 我方单位，我方子弹类，我方非子弹类，我方非绘制类
# 友方单位，友方子弹类，友方非子弹类，友方非绘制类
# 敌方单位，敌方子弹类，敌方非子弹类，敌方非绘制类
player_unit = pygame.sprite.Group()
player_bullet = pygame.sprite.Group()
player_non_bullet = pygame.sprite.Group()
player_not_draw = pygame.sprite.Group()
friendly_unit = pygame.sprite.Group()
friendly_bullet = pygame.sprite.Group()
friendly_non_bullet = pygame.sprite.Group()
friendly_not_draw = pygame.sprite.Group()
enemy_unit = pygame.sprite.Group()
enemy_bullet = pygame.sprite.Group()
enemy_non_bullet = pygame.sprite.Group()
enemy_not_draw = pygame.sprite.Group()

Player(Vector2(200, 380), player_unit)
Enemy(Vector2(100, 100), enemy_unit)
Boss(enemy_unit)

# 主体
while running := True:
    # 决定游戏刷新率
    clock.tick(FPS)
    delay = 1000 / clock.get_time()
    smooth_fps.append(delay)
    smooth_fps.pop(0)
    real_fps = math.floor(mean(smooth_fps))
    pygame.display.set_caption(f"FPS: {real_fps}")
    # 点×时退出。。
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    # 先铺背景和文字
    screen.fill(pygame.Color(BACKGROUND_COLOR))
    # 更新sprites状态
    player_unit.update(events)
    player_bullet.update(events)
    player_non_bullet.update(events)
    friendly_unit.update(events)
    friendly_bullet.update(events)
    friendly_non_bullet.update(events)
    enemy_unit.update(events)
    enemy_bullet.update(events)
    enemy_non_bullet.update(events)
    # wall.update(events)
    # 绘制sprites
    player_unit.draw(screen)
    player_bullet.draw(screen)
    player_non_bullet.draw(screen)
    friendly_unit.draw(screen)
    friendly_bullet.draw(screen)
    friendly_non_bullet.draw(screen)
    enemy_unit.draw(screen)
    enemy_bullet.draw(screen)
    enemy_non_bullet.draw(screen)
    # wall.draw(screen)
    # 更新画布
    pygame.display.flip()
