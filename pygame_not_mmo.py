import pygame
from pygame import Vector2
from statistics import mean
import math

# 准备仿mmo的boss战做机制挑战
# boss1号，共2阶段
# 阶段一：
# boss周围出现4面墙。触碰扣血，会阻挡远程箭矢。
# 同时4个角刷新4个不会动的敌人。Boss每20秒会随机任选两个敌人。该选择在敌人生成时立即生效。
# 每个被选中的敌人将持有一个端点5秒。未持有端点者无敌。同一批被选择的端点间出现连一条线，会对玩家造成伤害。
# 敌人会将手中的端点随机发射给另一个敌人。敌人可以持有复数个端点，但至少有两个敌人持有端点。
# 发射到另一个敌人需要花费约1秒。
# 持有端点的敌人死亡后会立即发射端点。
# 击杀两个敌人后剩余敌人消失，所有端点立即消失。离杀死的敌人相连形成的平行线最近的boss墙会消失。
# 敌人退去后boss将在5秒后重新召唤他们。
# 所有墙存在时，boss会间歇性的打出aoe和随机的子弹。平价3秒一个aoe，1秒一个随机弹。
# 第一面墙破碎后，随机子弹的频率提升至0.8秒。破墙的方向上aoe扩散得更远。boss开始倒计时60秒。时间到时墙恢复。
# 第二面墙破碎后，随机子弹的频率提升至0.6秒。倒计时变为当前的80%或20秒，取较高的值。
# 第三面墙破碎后，随机子弹的频率提升至0.4秒。aoe的频率提升至1.5秒。倒计时变为当前的50%或10秒，取较高的值。
# 如果做到墙完全破碎，则boss会完全失能15秒。
# boss血量降低到50%时赋予所有单位无敌效果，召唤的敌人消失，端点消失，玩家将被击飞至地图边缘。并在1秒后进入阶段二。
# 阶段二：
# 待定。


WIDTH = 400
HEIGHT = 400
FPS = 60.0
SIZE = WIDTH, HEIGHT

# 颜色常量
BACKGROUND_COLOR = 153, 255, 153
BLACK = 0, 0, 0
ALMOST_BLACK = 1, 1, 1
WHITE = 255, 255, 255
RED = 255, 0, 0
YELLOW = 255, 255, 0
ORANGE = 255, 127, 127


class Arrow(pygame.sprite.Sprite):
    def __init__(self, pos: Vector2, vect: Vector2, power: float, *groups) -> None:
        super().__init__(*groups)
        self.pos = Vector2(pos)
        self.vect = Vector2(vect)
        self.pow = power
        self.img_center = Vector2(36, 36)
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
        self.pos += self.vect.normalize()
        self.rect.center = self.pos
        # TODO 弓箭的射程？
        if self.pos.x < -50 or self.pos.x > 450 or self.pos.y < -50 or self.pos.y > 450:
            self.kill()


class Obstacles(pygame.sprite.Sprite):
    def __init__(self, *groups) -> None:
        super().__init__(*groups)
        self.x = 100
        self.image = pygame.Surface([5, HEIGHT])
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect(center=(self.x, 200))
        pygame.draw.line(self.image, ALMOST_BLACK, (3, 0), (3, 400))
        self.mask = pygame.mask.from_surface(self.image)
        self.move_to = 1

    def update(self, game_events):
        if self.move_to == 1 and self.x > 380:
            self.move_to = -1
        elif self.move_to == -1 and self.x < 20:
            self.move_to = 1
        self.x += self.move_to
        self.rect.center = (self.x, 200)


class Obstacles2(pygame.sprite.Sprite):
    def __init__(self, *groups) -> None:
        super().__init__(*groups)
        self.y = 100
        self.image = pygame.Surface([WIDTH, 5])
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect(center=(200, self.y))
        pygame.draw.line(self.image, ALMOST_BLACK, (0, 3), (400, 3))
        self.mask = pygame.mask.from_surface(self.image)
        self.move_to = 1

    def update(self, game_events):
        if self.move_to == 1 and self.y > 380:
            self.move_to = -1
        elif self.move_to == -1 and self.y < 20:
            self.move_to = 1
        self.y += self.move_to
        self.rect.center = (200, self.y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos: Vector2, *groups) -> None:
        super().__init__(*groups)
        self.pos = pos
        self.img_center = Vector2(20, 20)
        self.image = pygame.Surface(self.img_center)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect(center=self.pos)
        pygame.draw.circle(self.image, RED, self.img_center // 2, 10)
        self.mask = pygame.mask.from_surface(self.image)

        self.drawing_bow = False
        self.start_draw = 0
        self.dashed = False
        self.last_dash = 0

        self.hp = 10

    def _player_control(self):
        left = pygame.key.get_pressed()[pygame.K_a]
        up = pygame.key.get_pressed()[pygame.K_w]
        down = pygame.key.get_pressed()[pygame.K_s]
        right = pygame.key.get_pressed()[pygame.K_d]
        speed_boost = 1 if self.drawing_bow else 2
        del_x = right - left
        del_y = down - up
        # 限制玩家不能离开屏幕
        if self.pos.x < 11 and del_x < 0:
            del_x = 0
            self.pos.x = 10
        elif self.pos.x > WIDTH - 11 and del_x > 0:
            del_x = 0
            self.pos.x = WIDTH - 10
        if self.pos.y < 11 and del_y < 0:
            del_y = 0
            self.pos.y = 10
        elif self.pos.y > HEIGHT - 11 and del_y > 0:
            del_y = 0
            self.pos.y = HEIGHT - 10
        speed = Vector2(del_x, del_y)
        if speed.length() != 0:
            speed.normalize_ip()
        return speed_boost * speed

    def update(self, game_events):
        if self.hp <= 0:
            self.kill()
        if pygame.sprite.spritecollide(self, wall, False, pygame.sprite.collide_mask):
            self.hp -= 2
        # TODO 受击后无敌0.5秒
        # 右键拉弓
        if not self.drawing_bow and pygame.mouse.get_pressed(3)[-1]:
            self.drawing_bow = True
            self.start_draw = pygame.time.get_ticks()
        # 松开射箭
        elif self.drawing_bow and not pygame.mouse.get_pressed(3)[-1]:
            drawing_time = pygame.time.get_ticks() - self.start_draw
            self.drawing_bow = False
            x = min(1.0, drawing_time / 1000)
            bow_power = 1 - math.sqrt(1 - x ** 2)  # TODO 弓箭威力算法
            Arrow(
                self.pos,
                pygame.mouse.get_pos() - self.pos,
                bow_power,
                test
            )
        next_move = self._player_control()
        # 空格闪避
        if not self.dashed and pygame.key.get_pressed()[pygame.K_SPACE]:
            next_move *= 40
            self.dashed = True
            self.last_dash = pygame.time.get_ticks()
            pygame.draw.circle(self.image, ORANGE, self.img_center // 2, 10)
        # 闪避充能两秒
        elif self.dashed and pygame.time.get_ticks() - self.last_dash > 2000:
            self.dashed = False
            pygame.draw.circle(self.image, RED, self.img_center // 2, 10)
        self.pos += next_move
        self.rect.center = self.pos


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos: Vector2, *groups) -> None:
        super().__init__(*groups)
        self.pos = pos
        self.img_center = Vector2(20, 20)
        self.image = pygame.Surface(self.img_center)
        self.image.set_colorkey(BLACK)
        pygame.draw.circle(self.image, YELLOW, self.img_center / 2, 10)
        self.rect = self.image.get_rect(center=self.pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.hp = 10

    def update(self, game_events) -> None:
        hits = pygame.sprite.spritecollide(self, test, True, pygame.sprite.collide_mask)
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
Player(Vector2(200, 200), p)
e = pygame.sprite.Group()
Enemy(Vector2(100, 100), e)
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
    p.update(events)
    e.update(events)
    wall.update(events)
    # 绘制sprites
    test.draw(screen)
    p.draw(screen)
    e.draw(screen)
    wall.draw(screen)
    # 更新画布
    pygame.display.flip()
