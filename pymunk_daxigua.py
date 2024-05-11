import pygame
from pygame.key import *
from pygame.locals import *
from pygame.color import *

import pymunk
import pymunk.pygame_util

import numpy as np
import random

# 合成大西瓜

# pymunk初始化
space = pymunk.Space()  # 空间
space.gravity = (0.0, 980.0)  # 设置重力

eps = 1e-2

# pygame初始化
pygame.init()
screen = pygame.display.set_mode((300, 500))
clock = pygame.time.Clock()
# 在pygame上创建画板
draw_options = pymunk.pygame_util.DrawOptions(screen)

FPS = 120
balls = pygame.sprite.Group()  # 所有的球
exact = 10  # 一帧计算几次

static_body = space.static_body
static_lines = [
    pymunk.Segment(static_body, (20.0, 480.0), (280.0, 480.0), 3.0),
    pymunk.Segment(static_body, (280.0, 100.0), (280.0, 480.0), 3.0),
    pymunk.Segment(static_body, (20.0, 100.0), (20.0, 480.0), 3.0),
    pymunk.Segment(static_body, (20.0, 100.0), (-20.0, 60.0), 4.0 / 2),
    pymunk.Segment(static_body, (280.0, 100.0), (320.0, 60.0), 4.0 / 2),
]
for line in static_lines:
    line.elasticity = 0.5  # 弹性系数 0-1
    line.friction = 0.9  # 摩擦系数 0-1
    space.add(line)


def add_collision_handler():
    def post_collision_ball_ball(arbiter, space, data):
        space.remove(arbiter.shapes[0])
        space.remove(arbiter.shapes[1])
        pos = pymunk.Vec2d(0, 0)
        old_level: int = -1
        for spirit in balls.sprites():
            if spirit.shape in arbiter.shapes:
                pos += spirit.shape.bb.center()
                old_level = spirit.level
                spirit.kill()
        pos /= 2
        Ball(pos, old_level + 1, space, balls)

    for i in range(1, 7):
        space.add_collision_handler(i, i).post_solve = post_collision_ball_ball


class Ball(pygame.sprite.Sprite):
    colors = {
        1: (255, 0, 0),
        2: (255, 165, 0),
        3: (255, 255, 0),
        4: (0, 255, 0),
        5: (0, 255, 255),
        6: (0, 0, 255),
        7: (200, 0, 255),
    }

    def __init__(
        self,
        pos: tuple[int, int] | pygame.Vector2,
        level: int,
        space: pymunk.Space,
        group: pygame.sprite.Group,
    ) -> None:
        super().__init__()
        self.level = level
        self.radius = 10 + level * 5
        self.mass = 10
        self.image = pygame.Surface((self.radius * 2, self.radius * 2))
        self.image.set_colorkey((0, 0, 0))
        self.rect = pygame.draw.circle(
            self.image,
            Ball.colors[self.level],
            (self.radius, self.radius),
            self.radius,
        )
        inertia = pymunk.moment_for_circle(self.mass, 0, self.radius)
        self.body = pymunk.Body(self.mass, inertia)
        self.body.position = pos
        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.elasticity = 0.5
        self.shape.friction = 0.9
        self.shape.collision_type = level
        self.rect.center = pygame.Vector2(self.shape.bb.center())
        space.add(self.body, self.shape)
        group.add(self)

    def update(self) -> None:
        self.rect.center = np.array(self.shape.bb.center()).astype(np.int32).tolist()


add_collision_handler()
last_ball_gen: int = 0
next_ball_level = random.choices([1, 2, 3], [7, 2, 1])[-1]
while True:
    # 计算下一帧位置
    for x in range(exact):
        space.step(1 / FPS / exact)

    for event in pygame.event.get():
        if event.type == QUIT:
            exit()
        elif event.type == MOUSEBUTTONDOWN:
            if pygame.time.get_ticks() - last_ball_gen > 300:
                x, y = event.dict["pos"]
                x += random.randint(-1, 1) * eps
                Ball((x, 40), next_ball_level, space, balls)
                last_ball_gen = pygame.time.get_ticks()
                next_ball_level = random.choices([1, 2, 3], [7, 2, 1])[-1]

    screen.fill(THECOLORS["white"])  # 清屏
    pygame.draw.lines(
        screen,
        (0, 0, 0),
        False,
        [(-20, 60), (20, 100), (20, 480), (280, 480), (280, 100), (320, 60)],
        6,
    )
    # space.debug_draw(draw_options)  # 画图
    balls.update()
    balls.draw(screen)
    pygame.display.flip()  # 渲染
    clock.tick(FPS)
    pygame.display.set_caption("fps: {}".format(int(clock.get_fps())))
