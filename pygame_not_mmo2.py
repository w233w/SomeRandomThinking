from typing import Tuple, Literal, Self
import pygame
from pygame import Vector2
from statistics import mean
import math
import random

# 准备仿mmo的boss战做机制挑战
# boss1号，共2阶段
# boss共6000hp。
# 阶段一（hp>3000）：
# boss位于矩形一边中点。boss对面场地出现红蓝两个漩涡。
# 漩涡有60每秒的高额接触伤害。
# ┏━━━━━━━━━━┓
# ┃   Boss   ┃
# ┃          ┃
# ┃          ┃
# ┃Red   Blue┃
# ┗━━━━━━━━━━┛
# boss行为1，发射两个add(A)。
# boss行为2，boss身上闪烁红光或者蓝光，3秒延迟后向玩家发射一枚高速直线射弹，
#   射弹初始伤害为0，每次与墙壁反弹后提升5点伤害，最高30点。射弹具有穿透能力。
#   （待定）射弹每次击中墙壁都会重新瞄准玩家反弹。
#   射弹命中与其颜色相同的add后可以破除他的护盾并消失。
#   射弹命中与其颜色不同的add后会发生大爆炸形成震荡波，震荡波会造成40点全场伤害。
#   射弹达到最大伤害后变为超级追踪形态，必定命中玩家
# boss行为3，向前方按循序发射[10，11，12, 11, 10]颗射弹组成的扇形弹幕。
# boss行为4，当全部漩涡失能时，自身失能20秒。
# boss行为5，在自身左右两个召唤add(B)。
# boss行为6，间隔连续使用两次行为5。
# add(A)行为1，短暂延迟后向玩家发射激光束，之后自身死亡。
# add(B)行为1，短暂延迟后与另一个add(B)链接，形成的线会造成伤害。同时向下方匀速移动。
# 漩涡行为1，出场时获得3层无敌盾。
# 漩涡行为2，当场上不存在与自身颜色相同的add(C)时，1秒后召唤与自身颜色一致的add(C)。
# 漩涡行为3，当场上与自身颜色一致的add(C)死亡后，自身无敌盾消除一层。
# 漩涡行为4，收到任意攻击时漩涡完全失能40秒。
# 漩涡行为4，boss失能时自身也失能。
# 漩涡行为4，失能结束后重新出场。
# add(C)行为1，出生时获得高额护盾，缓慢移动，并不断发射6向射弹。
# add(C)行为2，出生5秒后若距离上一次全局该行为发生超过5秒，诱使boss执行boss行为2。
# 阶段二：
# 场地不变。漩涡变大100%。漩涡得到一层无敌盾。
# 漩涡无盾时接触伤害为0，其余时间为秒杀。玩家足够接近漩涡中心时会被传送到漩涡内部。
# 每个漩涡按照自己的颜色，在其内部每5秒生成一个同色add(D)。当任意漩涡内部超过5个add(D)后。
# 新生成的add(D)会出现在漩涡外部。并向boss移动。

WIDTH = HEIGHT = WSIZE = 400
FPS = 60.0
SIZE = WIDTH, HEIGHT
VSIZE = Vector2(SIZE)

# 颜色常量
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

PLAYER_POS_BOARDCAST = pygame.event.custom_type()
RELOAD_DONE_EVENT = pygame.event.custom_type()


class Unit(pygame.sprite.Sprite):
    def __init__(self, pos: pygame.Vector2, size: pygame.Vector2, *groups) -> None:
        super().__init__(*groups)
        self.pos = pygame.Vector2(pos)
        self.size = pygame.Vector2(size)
        self.radius = round(self.size.x // 2)
        self.image = pygame.Surface(self.size)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect(center=self.pos)

        self.init_time = pygame.time.get_ticks()

        self._shield_on = False
        self.shield_remain: int = 0

        self.hp = 0

    @property
    def shield_on(self):
        return self.shield_remain != 0

    # 护盾设计，
    # 护盾值为正数时是常规护盾，数值即为血量
    # 护盾值为负数时是无敌盾，
    def get_shield(self, val: int):
        self.shield_remain = val

    def die_check(self):
        if self.hp <= 0:
            self.kill()

    def update(self, game_events):
        raise NotImplementedError("Can't be called here.")


class SP_Bullet:
    def __init__(self) -> None:
        pass


class Boss(Unit):
    def __init__(self, *groups) -> None:
        super().__init__(pygame.Vector2(WIDTH // 2, 0), VSIZE // 2, *groups)
        pygame.draw.circle(self.image, ORANGE, self.size // 2, self.radius)
        self.mask = pygame.mask.from_surface(self.image)

        self.hp = 20000
        self.phase = 1

        self.action3_started = False
        self.action3_starting = 0
        self.action3_config = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
        self.action3_wave = -1
        self.last_action5 = self.init_time

    def action1(self):
        pass

    def action3(self, current_time):
        if not self.action3_started:
            self.action3_started = True
            self.action3_starting = current_time
        delta_time = current_time - self.action3_starting
        wave = delta_time // 1000
        print(delta_time, wave, self.action3_wave)
        if wave >= len(self.action3_config) - 1:
            self.action3_started = False
        if wave > self.action3_wave:  # 每波间隔
            self.action3_wave = wave
            config = self.action3_config[wave]
            interval = 8
            total = config * 8
            start = -(total / 2)
            for i in range(config):
                Bullet(
                    self.pos,
                    pygame.Vector2(0, 1).rotate(start + (i + 0.5) * interval),
                    10,
                    3,
                    enemy_bullet,
                )

    def action5(self):
        a = Addon_B(self.pos, 20, None, enemy_unit)
        Addon_B(self.pos, 20, a, enemy_unit)

    def update(self, game_events) -> None:
        current_time = pygame.time.get_ticks()

        if hits := pygame.sprite.spritecollide(
            self, player_bullet, True, pygame.sprite.collide_mask
        ):
            for hit in hits:
                self.hp -= hit.power
        if hits := pygame.sprite.spritecollide(
            self, player_non_bullet, False, pygame.sprite.collide_mask
        ):
            for hit in hits:
                self.hp -= hit.power

        self.action3(current_time)

        if current_time - self.last_action5 > 1000:
            self.action5()
            self.last_action5 = current_time


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
        if current_time > 500:
            self.kill()
            return
        self.image.fill(BLACK)
        r = self.radius * current_time / 500
        pygame.draw.circle(
            self.image,
            BLUE,
            [self.radius, self.radius],
            r,
            max(1, 12 - round(12 * current_time / 500)),
        )
        self.mask = pygame.mask.from_surface(self.image)


class Laser(pygame.sprite.Sprite):
    def __init__(self, start, end, power, *groups) -> None:
        super().__init__(*groups)
        self.size = VSIZE
        self.image = pygame.Surface(self.size)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect(center=self.size // 2)
        self.start = pygame.Vector2(start)
        self.end = pygame.Vector2(end)
        self.power = power
        self.width = 1
        self.mask = pygame.mask.Mask(self.size)
        self.init_time = pygame.time.get_ticks()

    def update(self, game_events):
        current_time = pygame.time.get_ticks()
        x = (current_time - self.init_time) / 1000
        if x > 2:
            self.kill()
        self.width = 1 + 3**x
        pygame.draw.line(self.image, RED, self.start, self.end, int(self.width))
        if self.width >= 3:
            self.mask = pygame.mask.from_surface(self.image)
        else:
            self.mask = pygame.mask.Mask(self.size)


class Laser2(pygame.sprite.Sprite):
    def __init__(self, add1: "Addon_B", add2: "Addon_B", power, *groups) -> None:
        super().__init__(*groups)
        self.size = VSIZE
        self.image = pygame.Surface(self.size)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect(center=self.size // 2)
        self.add1 = add1
        self.add2 = add2
        self.power = power
        self.width = 1
        self.mask = pygame.mask.Mask(self.size)
        self.init_time = pygame.time.get_ticks()

    def update(self, game_events):
        self.image.fill(BLACK)
        current_time = pygame.time.get_ticks()
        x = (current_time - self.init_time) / 1000
        self.width = min(1 + 3**x, 10)
        pygame.draw.line(self.image, RED, self.add1.pos, self.add2.pos, int(self.width))
        if self.width >= 3:
            self.mask = pygame.mask.from_surface(self.image)
        else:
            self.mask = pygame.mask.Mask(self.size)


class Addon_A(Unit):
    def __init__(self, pos, size, init_speed, *groups) -> None:
        super().__init__(pos, size, *groups)
        self.hp = 1
        self.init_speed = init_speed
        pygame.draw.circle(self.image, ALMOST_BLACK, self.size // 2, self.radius)

    def update(self, game_events):
        self.die_check()
        if pygame.time.get_ticks() - self.init_time > 1000:
            for event in game_events:
                if event.type == PLAYER_POS_BOARDCAST:
                    Laser(self.pos, event.dict["pos"], 3, enemy_non_bullet)
                    self.kill()


class Addon_B(Unit):
    def __init__(
        self, pos: Vector2, size: Vector2, brother: Self | None, *groups
    ) -> None:
        super().__init__(pos, size, *groups)
        self.hp = 1
        self.get_shield(-1)
        pygame.draw.circle(self.image, ALMOST_BLACK, self.size // 2, self.radius)
        self.brother = brother
        self.shot = False
        self.start_going_dowm = 0
        self.speed = 0
        self.x = 0
        self.laser = None

    def update(self, game_events):
        if self.pos.y > 300:
            if self.laser is not None:
                self.laser.kill()
            self.kill()
        if self.brother is not None and self.pos.x != 0:
            self.speed = pygame.Vector2(-1, 0)
        elif self.brother is None and self.pos.x != WIDTH:
            self.speed = pygame.Vector2(1, 0)
        else:
            if not self.shot and self.brother is not None:
                self.laser = Laser2(self, self.brother, 4, enemy_non_bullet)
                self.shot = True
            self.speed = pygame.Vector2(0, 3)
        self.pos += self.speed
        self.rect.center = self.pos


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, vect, power, speed, *groups) -> None:
        super().__init__(*groups)
        self.pos = pygame.Vector2(pos)
        self.vect = pygame.Vector2(vect).normalize()
        self.power = power
        self.speed = speed
        self.size = pygame.Vector2(WSIZE // 200)
        self.image = pygame.Surface(self.size)
        self.image.set_colorkey(BLACK)
        pygame.draw.circle(self.image, ALMOST_BLACK, self.size // 2, self.size.x // 2)
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, game_events) -> None:
        self.pos += self.vect * self.speed
        self.rect.center = self.pos


class Weapon:
    def __init__(
        self,
        wtype: Literal["gun", "throw"],
        wclass: str,
        ammo: int,
        power: int,
        shoot_interval: int,
        reload_time: int,
        shotgun_bullets: int = 6,
    ) -> None:
        self.wtype = wtype
        self.wclass = wclass
        self.loaded = self.max_load = ammo
        self.power = power
        self.shoot_interval = shoot_interval
        self.reload_time = reload_time
        self.shotgun_bullets = shotgun_bullets

        self.reloading = False
        self.start_reloading = 0
        self.last_shoot = 0

    @property
    def need_reload(self):
        return (not self.reloading) and self.loaded <= 0

    def reload(self, start_time):
        self.reloading = True
        self.start_reloading = start_time

    def check_reload(self, current_time):
        if current_time - self.start_reloading >= self.reload_time:
            pygame.event.post(pygame.Event(RELOAD_DONE_EVENT))
            if self.wclass == "shotgun":
                if self.loaded == self.max_load:
                    self.reloading = False
                    return
                self.loaded += 1
                self.start_reloading = current_time
            else:
                self.reloading = False
                self.loaded = self.max_load

    def stop_reload(self):
        self.reloading = False

    def shoot(self, init_pos: pygame.Vector2, current_time):
        if self.reloading and self.wclass != "shotgun":
            return
        if self.need_reload:
            self.reload(current_time)
        if self.loaded > 0 and current_time - self.last_shoot >= self.shoot_interval:
            mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
            vect = mouse_pos - init_pos
            if self.wclass == "shotgun":
                self.reloading = False
                for _ in range(self.shotgun_bullets):
                    Bullet(
                        init_pos,
                        vect.rotate(random.random() * 15 - 7.5),
                        self.power,
                        5,
                        player_bullet,
                    )
            else:
                Bullet(init_pos, vect, self.power, 5, player_bullet)
            self.loaded -= 1
            self.last_shoot = current_time


class Player(Unit):
    def __init__(self, pos: Vector2, size, *groups) -> None:
        super().__init__(pos, size, *groups)
        self.hp = 100
        self.color = RED

        self.font = pygame.font.SysFont("simhei", self.radius)
        self.render()

        self.mask = pygame.mask.from_surface(self.image)

        self.dashed = False
        self.last_dash = 0

        self.last_on_hit = pygame.time.get_ticks()

        # 武器设计
        # 手枪：移动射击精度高，可移动reload
        # 喷子：同手枪
        # 微冲：移动射击精度低，可移动reolad
        # 步枪：移动射击精度低，不可移动reload
        # 机枪：射击时不能移动，不可移动reload
        # 狙：射击时不能移动，不可移动reload
        self.weapons: dict[int, Weapon] = {
            1: Weapon("gun", "pistol", 9, 40, 400, 1800),
            2: Weapon("gun", "rifle", 25, 60, 100, 2700),
            3: Weapon("gun", "shotgun", 6, 22, 800, 400),
            4: Weapon("gun", "machinegun", 80, 28, 40, 5000),
        }
        self.selected_weapon = 1
        for i in range(self.weapon.loaded):
            Ammo_Hint(i, self, ammo_hint_group)

    @property
    def weapon(self):
        return self.weapons[self.selected_weapon]

    def _player_control(self):
        left = pygame.key.get_pressed()[pygame.K_a]
        up = pygame.key.get_pressed()[pygame.K_w]
        down = pygame.key.get_pressed()[pygame.K_s]
        right = pygame.key.get_pressed()[pygame.K_d]
        speed_boost = 2
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
        pygame.draw.circle(self.image, self.color, self.size // 2, self.radius)
        self.image.blit(
            hp_text, [self.radius - text_size[0] / 2, self.radius - text_size[1] / 2]
        )

    def switch_weapon(self, game_events):
        for event in game_events:
            if event.type == pygame.KEYDOWN:
                if (
                    event.dict["unicode"].isdigit()
                    and int(event.dict["unicode"]) in self.weapons
                ):
                    self.weapon.stop_reload()
                    self.selected_weapon = int(event.dict["unicode"])
                    return True
        return False

    def update(self, game_events):
        if self.hp <= 0:
            ammo_hint_group.empty()
            Player(Vector2(200, 380), self.size, player_unit)
            self.kill()

        current_time = pygame.time.get_ticks()

        for event in game_events:
            if event.type == RELOAD_DONE_EVENT:
                ammo_hint_group.empty()
                for i in range(self.weapon.loaded):
                    Ammo_Hint(i, self, ammo_hint_group)
            if event.type == pygame.KEYDOWN:
                if event.dict["key"] == pygame.K_r:
                    self.weapon.reload(current_time)

        weapon_switched = self.switch_weapon(game_events)

        if weapon_switched:
            ammo_hint_group.empty()
            for i in range(self.weapon.loaded):
                Ammo_Hint(i, self, ammo_hint_group)
        if self.weapon.reloading:
            self.weapon.check_reload(current_time)

        # 处理受伤
        on_hit = False
        if hits := pygame.sprite.spritecollide(
            self, enemy_unit, False, pygame.sprite.collide_mask
        ):
            for hit in hits:
                if hasattr(hit, "power"):
                    self.hp -= hit.power
            on_hit = True
        if hits := pygame.sprite.spritecollide(
            self, enemy_bullet, True, pygame.sprite.collide_mask
        ):
            for hit in hits:
                self.hp -= hit.power
            on_hit = True
        if hits := pygame.sprite.spritecollide(
            self, enemy_non_bullet, False, pygame.sprite.collide_mask
        ):
            for hit in hits:
                self.hp -= hit.power
            on_hit = True
        if on_hit:
            self.render()
            self.last_on_hit = current_time

        # 呼吸回血
        if current_time - self.last_on_hit > 6000 and self.hp < 80:
            self.hp += 1
            self.render()

        # 射击
        if pygame.mouse.get_pressed()[0]:
            self.weapon.shoot(self.pos, current_time)

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
        pygame.event.post(pygame.Event(PLAYER_POS_BOARDCAST, {"pos": self.pos}))


class Ammo_Hint(pygame.sprite.Sprite):
    def __init__(
        self, index, bounding_player: Player, *groups: pygame.sprite.Group
    ) -> None:
        super().__init__(*groups)
        self.image = pygame.image.load("./aa.png")
        self.player = bounding_player
        self.index = index
        self.pos = pygame.Vector2(10, WIDTH - 10 - 6 * index)
        self.rect = self.image.get_rect(center=self.pos)

    def update(self):
        if self.index >= self.player.weapon.loaded:
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
# 我方单位，我方子弹类，我方非子弹类
# 敌方单位，敌方子弹类，敌方非子弹类
# 中立非子弹类
player_unit = pygame.sprite.Group()
player_bullet = pygame.sprite.Group()
player_non_bullet = pygame.sprite.Group()
enemy_unit = pygame.sprite.Group()
enemy_bullet = pygame.sprite.Group()
enemy_non_bullet = pygame.sprite.Group()
neutral_non_bullet = pygame.sprite.Group()

ammo_hint_group = pygame.sprite.Group()

Player(Vector2(200, 380), VSIZE // 20, player_unit)
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
    enemy_unit.update(events)
    enemy_bullet.update(events)
    enemy_non_bullet.update(events)
    ammo_hint_group.update()
    # wall.update(events)
    # 绘制sprites
    player_unit.draw(screen)
    player_bullet.draw(screen)
    player_non_bullet.draw(screen)
    enemy_unit.draw(screen)
    enemy_bullet.draw(screen)
    enemy_non_bullet.draw(screen)
    ammo_hint_group.draw(screen)
    # wall.draw(screen)
    # 更新画布
    pygame.display.flip()
