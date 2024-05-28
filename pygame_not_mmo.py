import pygame
from pygame import Vector2
from statistics import mean
import math
import numpy as np

# 准备仿mmo的boss战做机制挑战

WIDTH = 400
HEIGHT = 400
FPS = 60
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
    def __init__(self, pos: Vector2, vect: Vector2, pow: float, *groups) -> None:
        super().__init__(*groups)
        self.pos = Vector2(pos)
        self.vect = Vector2(vect)
        self.pow = pow
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

    def update(self, events):
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

    def update(self, events):
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

    def update(self, events):
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
        try:
            speed.normalize_ip()
        except:
            pass
        return speed_boost * speed

    def update(self, events):
        if self.hp <= 0:
            self.kill()
        if pygame.sprite.spritecollide(self, wall, False, pygame.sprite.collide_mask):
            self.hp -= 2
        # 右键拉弓
        if not self.drawing_bow and pygame.mouse.get_pressed(3)[-1]:
            self.drawing_bow = True
            self.start_draw = pygame.time.get_ticks()
        # 松开射箭
        elif self.drawing_bow and not pygame.mouse.get_pressed(3)[-1]:
            drawing_time = pygame.time.get_ticks() - self.start_draw
            self.drawing_bow = False
            x = min(1, drawing_time / 1000)
            bow_power = 1 - math.sqrt(1 - x**2)  # TODO 弓箭威力算法
            test.add(
                Arrow(
                    self.pos,
                    pygame.mouse.get_pos() - self.pos,
                    bow_power,
                )
            )
        next_move = self._player_control()
        if not self.dashed and pygame.key.get_pressed()[pygame.K_SPACE]:
            next_move *= 40
            self.dashed = True
            self.last_dash = pygame.time.get_ticks()
            pygame.draw.circle(self.image, ORANGE, self.img_center // 2, 10)
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

    def update(self, events) -> None:
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
p = pygame.sprite.GroupSingle(Player(Vector2(200, 200)))
e = pygame.sprite.Group(Enemy(Vector2(100, 100)))
wall = pygame.sprite.Group(Obstacles(), Obstacles2())
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
