from typing import Tuple, Literal
import pygame
from pygame import Vector2
from statistics import mean
import math

# 准备仿mmo的boss战做机制挑战
# boss1号，共2阶段
# 阶段一：
# boss周围出现4面墙。触碰扣血，会阻挡远程箭矢。
# 同时4个角刷新4个不会动的add。Boss每10秒会随机任选两个add。该选择在add生成时立即生效。
# 在add击退前，选择最多发生三次。
# add位置样例，add在[0, 1, 2, 3]上。
# 0        1
#
#     Bs
#
# 2        3
# 每个被选中的add将持有一个端点5秒。未持有端点者无敌。同一批被选择的端点间出现连一条线，会对玩家造成伤害。
# add会将手中的端点随机发射给另一个敌人。同一对端点不会互相发射。
# add不会死亡，而是失能。
# 敌人可以持有复数个端点。
# 发射到另一个敌人需要花费约1-1.414秒。
# 持有端点的敌人失能后会立即摧毁持有端点及对应的端点。
# 两个敌人失能后剩余敌人全部失能，所有端点立即消失。离杀死的敌人相连形成的平行线最近的boss墙会消失。
# 所有墙存在时，boss会间歇性的打出aoe和随机的子弹。平价3秒一个aoe，1秒一个随机弹。
# 第一面墙破碎后，随机子弹的频率提升至0.8秒。破墙的方向上aoe扩散得更远。boss开始倒计时60秒。时间到时墙恢复。
# 第二面墙破碎后，随机子弹的频率提升至0.6秒。倒计时变为当前的80%或20秒，取较高的值。
# 第三面墙破碎后，随机子弹的频率提升至0.4秒。aoe的频率提升至1.5秒。倒计时变为当前的50%或10秒，取较高的值。
# 如果做到墙完全破碎，则boss会完全失能15秒。
# boss血量降低到50%时赋予所有单位无敌效果，召唤的敌人消失，端点消失，玩家将被击飞至地图边缘。并在1秒后进入阶段二。
# 阶段二：
# 玩家失去闪避能力。
# boss在四个角，四条边的中点召唤8个不动的敌人。每5秒，boss选择两组相邻且不重复的四个敌人赋予端点。


WIDTH = HEIGHT = 400
FPS = 60.0
SIZE = WIDTH, HEIGHT
VSIZE = Vector2(*SIZE)

# 颜色常量
# BACKGROUND_COLOR = 153, 255, 153
BACKGROUND_COLOR = 255, 255, 255
BLACK = 0, 0, 0
GRAY = 127, 127, 127
ALMOST_BLACK = 1, 1, 1
WHITE = 255, 255, 255
RED = 255, 0, 0
YELLOW = 255, 255, 0
PINK = 255, 127, 127
ORANGE = 255, 127, 0


class Boss(pygame.sprite.Sprite):
    def __init__(self, *groups) -> None:
        super().__init__(*groups)
        self.pos = VSIZE // 2
        self.size = VSIZE // 4
        self.image = pygame.Surface(self.size)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect(center=self.pos)
        pygame.draw.circle(self.image, ORANGE, self.size // 2, WIDTH // 20)
        self.mask = pygame.mask.from_surface(self.image)
        self.wall_status = {"n": True, "e": True, "w": True, "s": True}
        self.walls = pygame.sprite.Group()
        Wall(self.rect.topleft, self.rect.topright, self.walls)
        Wall(self.rect.topleft, self.rect.bottomleft, self.walls)
        Wall(self.rect.topright, self.rect.bottomright, self.walls)
        Wall(self.rect.bottomleft, self.rect.bottomright, self.walls)

        self.last_summon = 0
        self.addons_status_watching_list = {
            1: [0, 2, 4, 6],
            2: [0, 1, 2, 3, 4, 5, 6, 7],
        }
        self.addons = pygame.sprite.Group()

    def update(self, game_events) -> None:
        self.walls.update(game_events)
        self.walls.draw(screen)


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


# TODO 近战弹道
# Combo -> 0：逆时针横扫，1：顺时针横扫，2：直刺。
class Sword(pygame.sprite.Sprite):
    def __init__(
        self, pos: Vector2, combo: Literal[0, 1, 2], duration: int, *groups
    ) -> None:
        super().__init__(*groups)
        self.player_pos = (
            pos  # 不封装Vector2会导致player_pos同步玩家位置，这正是我想要的。
        )
        self.pos = Vector2(pos)
        self.length = WIDTH // 20
        self.image = pygame.Surface(VSIZE // 10)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect(center=self.pos)
        self.mouse_pos_when_trigger = Vector2(pygame.mouse.get_pos())
        self.vect = self.mouse_pos_when_trigger.angle_to(self.pos)
        print(self.vect)
        self.combo = combo
        self.duration = duration
        self.init_time = pygame.time.get_ticks()

    def update(self, game_events):
        time_passed = pygame.time.get_ticks() - self.init_time
        progress = time_passed / self.duration
        if progress >= 1:
            self.kill()
        self.image.fill(BLACK)
        self.rect.center = self.player_pos
        match self.combo:
            case 0:
                pygame.draw.line(self.image, GRAY, VSIZE // 20, self.pos, 8)
            case 1:
                pygame.draw.line(self.image, GRAY, self.pos, Vector2(0, 0), 8)
            case 2:
                pygame.draw.line(self.image, GRAY, self.pos, Vector2(0, 0), 8)


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
        pygame.sprite.spritecollide(self, test, True, pygame.sprite.collide_mask)


class Addon(pygame.sprite.Sprite):
    def __init__(self, pos_id: Literal[0, 1, 2, 3, 4, 5, 6, 7], *groups) -> None:
        super().__init__(*groups)
        self.pos_id = pos_id
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
        self.image = pygame.Surface([40, 40])
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect(center=self.pos)
        pygame.draw.circle(self.image, YELLOW, [20, 20], 20)
        self.mask = pygame.mask.from_surface(self.image)
        self.hp = 4

        self.active = False


class Obstacles(pygame.sprite.Sprite):
    def __init__(self, *groups) -> None:
        super().__init__(*groups)
        self.x = 0
        self.image = pygame.Surface([5, HEIGHT])
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect(center=(self.x, HEIGHT // 2))
        pygame.draw.line(self.image, ALMOST_BLACK, (3, 0), (3, HEIGHT))
        self.mask = pygame.mask.from_surface(self.image)
        self.move_to = 1

    def update(self, game_events):
        if self.move_to == 1 and self.x >= WIDTH:
            self.move_to = -1
        elif self.move_to == -1 and self.x < 0:
            self.move_to = 1
        self.x += self.move_to
        self.rect.center = (self.x, HEIGHT // 2)


class Obstacles2(pygame.sprite.Sprite):
    def __init__(self, *groups) -> None:
        super().__init__(*groups)
        self.y = 0
        self.image = pygame.Surface([WIDTH, 5])
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect(center=(WIDTH // 2, self.y))
        pygame.draw.line(self.image, ALMOST_BLACK, (0, 3), (WIDTH, 3))
        self.mask = pygame.mask.from_surface(self.image)
        self.move_to = 1

    def update(self, game_events):
        if self.move_to == 1 and self.y >= HEIGHT:
            self.move_to = -1
        elif self.move_to == -1 and self.y < 0:
            self.move_to = 1
        self.y += self.move_to
        self.rect.center = (WIDTH // 2, self.y)


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
        self.on_combo = 0

    def _player_control(self):
        left = pygame.key.get_pressed()[pygame.K_a]
        up = pygame.key.get_pressed()[pygame.K_w]
        down = pygame.key.get_pressed()[pygame.K_s]
        right = pygame.key.get_pressed()[pygame.K_d]
        speed_boost = 2
        if self.drawing_bow:
            speed_boost = 1
        elif self.on_melee:
            speed_boost = 0.5
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
            self.kill()
        if pygame.sprite.spritecollide(self, wall, False, pygame.sprite.collide_mask):
            self.render()
            self.hp -= 0
        # TODO 受击后无敌0.5秒?

        # 射击能力
        # 右键拉弓
        if not self.drawing_bow and pygame.mouse.get_pressed(3)[-1]:
            self.drawing_bow = True
            self.start_draw = pygame.time.get_ticks()
        # 松开射箭
        elif self.drawing_bow and not pygame.mouse.get_pressed(3)[-1]:
            drawing_time = pygame.time.get_ticks() - self.start_draw
            self.drawing_bow = False
            x = min(1.0, drawing_time / 1000)
            bow_power = 1 - math.sqrt(1 - x**2)  # TODO 弓箭威力算法
            Arrow(self.pos, bow_power, test)

        # 近战能力
        # TODO 左键近战
        if not self.on_melee and pygame.mouse.get_pressed(3)[0]:
            self.on_melee = True
            Sword(self.pos, self.on_combo, 800, test)

        # 闪避能力：
        next_move = self._player_control()
        # 空格闪避
        if not self.dashed and pygame.key.get_pressed()[pygame.K_SPACE]:
            next_move *= 40
            self.dashed = True
            self.last_dash = pygame.time.get_ticks()
            self.render(PINK)
        # 闪避充能两秒
        elif self.dashed and pygame.time.get_ticks() - self.last_dash > 2000:
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
        hits = pygame.sprite.spritecollide(self, test, True, pygame.sprite.collide_mask)
        if self.count < 100:
            self.pos += self.move_sppeed
            self.count += 1
        else:
            self.move_sppeed = -self.move_sppeed
            self.count = 0
        self.rect.center = self.pos
        for hit in hits:
            self.hp -= hit.pow
            self.hp = round(self.hp, 3)
            print(self.hp)
        if self.hp <= 0:
            # e.add(Enemy(Vector2(100, 100)))
            self.kill()


# Init pygame & Crate screen
pygame.init()

screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption("测试")
clock = pygame.time.Clock()

smooth_fps = [FPS] * 10

test = pygame.sprite.Group()
p = pygame.sprite.GroupSingle()
Player(Vector2(200, 380), p)
e = pygame.sprite.Group()
Enemy(Vector2(100, 100), e)
Boss(e)
wall = pygame.sprite.Group()
Obstacles(wall)
Obstacles2(wall)
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
    test.update(events)
    e.update(events)
    p.update(events)
    wall.update(events)
    # 绘制sprites
    test.draw(screen)
    e.draw(screen)
    p.draw(screen)
    wall.draw(screen)
    # 更新画布
    pygame.display.flip()
