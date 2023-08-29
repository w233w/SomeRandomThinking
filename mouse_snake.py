import pygame
import math
from pygame import Vector2
from pygame.sprite import Group
from statistics import mean
import random

# 一个用鼠标玩的贪吃蛇

# 窗口数据
# 可修改
WIDTH = 400
HEIGHT = 400
FPS = 120
INIT_BODY_SEG = 20
FRUITS = 3
FRUIT_INCREASE_SEG = 2
DEBUG = True

if WIDTH < 400 or HEIGHT < 400:
    raise RuntimeError("Minium width and height is 400.")
if INIT_BODY_SEG < 2:
    raise RuntimeError("Minium starting body segements is 2")
if FPS < 30:
    raise RuntimeError("Minium FPS is 30")
# 不建议修改
_SIZE = WIDTH, HEIGHT
_MINUS = min(WIDTH, HEIGHT)
_RADIUS = _MINUS // 80
_FONT_SIZE = _MINUS // 15
_FONT_PADDING = 10
_DEBUG_LINE_WIDTH = _MINUS // 200
_SEGEMENT_GAP = (FPS // 6) * (_MINUS // 400)

# 颜色常量
_BACKGROUND_COLOR = pygame.color.Color(153, 255, 153)
_BLACK = 0, 0, 0
_ALMOST_BLACK = 1, 1, 1
_WHITE = 255, 255, 255
_RED = 255, 0, 0
_YELLOW = 255, 255, 0


# 蛇身
class SnakeBody(pygame.sprite.Sprite):
    def __init__(self, pos: Vector2, radius: int, id: int, *group: Group) -> None:
        super().__init__(*group)
        self.index: int = id
        self.init_pos: Vector2 = pos
        self.pos: Vector2 = pos
        self.radius: int = radius
        self.image: pygame.Surface = pygame.surface.Surface(
            (2 * self.radius, 2 * radius)
        )
        self.color_key: pygame.Color = self.image.get_at((0, 0))
        self.image.set_colorkey(self.color_key)
        self.rect: pygame.Rect = self.image.get_rect(center=self.pos)
        self.local_center: Vector2 = Vector2(radius, radius)
        self.next: SnakeBody = None
        self.path: list[Vector2] = [self.pos]

    def append(self):
        if self.next is None:
            self.next = SnakeBody(self.path[0], self.radius, self.index + 1, snake)
        else:
            self.next.append()

    def clear(self, keep_self: bool = False):
        if self.next is not None:
            self.next.clear()
            self.next = None
        if not keep_self:
            global score
            score -= 2
            self.kill()

    def update(self, new_pos: Vector2) -> None:
        pygame.draw.circle(self.image, _ALMOST_BLACK, self.local_center, self.radius)
        self.pos = new_pos
        self.rect.center = self.pos
        self.path.append(Vector2(new_pos))
        if len(self.path) > _SEGEMENT_GAP:
            self.path.pop(0)
        if self.next is not None:
            self.next.update(self.path[0])
        if self.index - 1 and self.pos != self.init_pos:
            if self.pos.distance_to(head.pos) < _RADIUS * 2:
                self.clear(True)


# 蛇头
class SnakeHead(pygame.sprite.Sprite):
    def __init__(self, pos: pygame.Vector2, radius: int, debug: bool = False) -> None:
        super().__init__()
        self.pos: Vector2 = pos
        self.radius: int = radius
        self.padding_multi: int = 8  # leave space to draw helping lines
        self.image: pygame.Surface = pygame.surface.Surface(
            (self.padding_multi * radius, self.padding_multi * radius)
        )
        self.color_key: pygame.Color = self.image.get_at((0, 0))
        self.image.set_colorkey(self.color_key)
        self.rect: pygame.Rect = self.image.get_rect(center=self.pos)
        self.local_center: Vector2 = Vector2(
            self.padding_multi * radius / 2, self.padding_multi * radius / 2
        )
        self.face_to: Vector2 = Vector2(1, 0)  # start with facing right
        self.debug: bool = debug
        self.next: SnakeBody = None
        self.path: list[Vector2] = [Vector2(self.pos)]

    def append(self):
        if self.next is None:
            self.next = SnakeBody(self.path[0], self.radius, 1, snake)
        else:
            self.next.append()

    def clear(self):
        if self.next is not None:
            self.next.clear()
        self.kill()

    def update(self) -> None:
        if self.debug:
            self.image.fill(self.color_key)
            self.image.set_colorkey(self.color_key)
        pygame.draw.circle(self.image, _RED, self.local_center, self.radius)
        mouse_pos = pygame.mouse.get_pos()
        mouse_to = Vector2(mouse_pos) - self.pos
        # Hard coded calcluation, use to judge turning left or right.
        delta_angle = (self.face_to.angle_to(mouse_to) + 360) % 360
        if delta_angle <= 45:
            shift = delta_angle
        elif 45 < delta_angle <= 180:
            shift = 45
        elif 180 < delta_angle <= 315:
            shift = -45
        elif 315 < delta_angle:
            shift = delta_angle - 360
        move_to = self.face_to.rotate(shift)
        # 角速度恒定
        # TODO 角速度也和窗口大小有关
        rotate_speed = (135, -135)[shift <= 0] / FPS
        # 按下鼠标可以加快旋转
        if pygame.mouse.get_pressed(num_buttons=3)[0]:
            rotate_speed *= 2
        real_move_to = self.face_to.rotate(rotate_speed)
        if self.debug:
            pygame.draw.line(
                self.image,
                _ALMOST_BLACK,
                self.local_center,
                self.local_center + mouse_to * 100,
                _DEBUG_LINE_WIDTH,
            )
            pygame.draw.line(
                self.image,
                _YELLOW,
                self.local_center,
                self.local_center + move_to * 100,
                _DEBUG_LINE_WIDTH,
            )
            pygame.draw.line(
                self.image,
                _RED,
                self.local_center,
                self.local_center + self.face_to * 100,
                _DEBUG_LINE_WIDTH,
            )
            pygame.draw.line(
                self.image,
                _WHITE,
                self.local_center,
                self.local_center + real_move_to * 100,
                _DEBUG_LINE_WIDTH,
            )
        # TODO 移动速度也和窗口大小有关
        self.pos += real_move_to * 60 / FPS
        self.rect.center = self.pos
        self.face_to = real_move_to
        self.path.append(Vector2(self.pos))
        if len(self.path) > _SEGEMENT_GAP:
            self.path.pop(0)
        if self.next is not None:
            self.next.update(self.path[0])


class Fruit(pygame.sprite.Sprite):
    def __init__(self, *groups: Group) -> None:
        super().__init__(*groups)
        self.generate_offset = _MINUS * 0.2  # 板边20%不会生成fruit
        self.pos = self.get_random_pos()
        while self.pos.distance_to(Vector2(WIDTH, HEIGHT) / 2) <= _RADIUS * 10:
            self.pos = self.get_random_pos()
        self.radius: int = _RADIUS
        self.image: pygame.Surface = pygame.surface.Surface(
            (2 * self.radius, 2 * self.radius)
        )
        self.color_key: pygame.Color = self.image.get_at((0, 0))
        self.image.set_colorkey(self.color_key)
        self.rect: pygame.Rect = self.image.get_rect(center=self.pos)
        self.local_center: Vector2 = Vector2(self.radius, self.radius)

    def get_random_pos(self):
        return Vector2(
            random.randint(self.generate_offset, WIDTH - self.generate_offset),
            random.randint(self.generate_offset, HEIGHT - self.generate_offset),
        )

    def update(self) -> None:
        pygame.draw.circle(self.image, _YELLOW, self.local_center, self.radius)
        if self.pos.distance_to(head.pos) <= _RADIUS * 2:
            global score
            score += 1
            self.pos = self.get_random_pos()
            while self.pos.distance_to(head.pos) <= _RADIUS * 5:
                self.pos = self.get_random_pos()
            for i in range(FRUIT_INCREASE_SEG):
                head.append()
            self.rect.center = self.pos

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.rect)


# Init pygame & Crate screen
pygame.init()

screen = pygame.display.set_mode(_SIZE)
pygame.display.set_caption("测试")
clock = pygame.time.Clock()
# 状态栏
# setting the pygame font style(1st parameter)
# and size of font(2nd parameter)
try:
    font = pygame.font.SysFont("得意黑斜体", _FONT_SIZE)
except:
    font = pygame.font.SysFont("timesnewroman", _FONT_SIZE)
fps_text_width = font.size("FPS: 999")[0]
score_text_height = font.size("Score: 999")[1]

smooth_fps = [FPS] * 60

snake = pygame.sprite.Group()
head = SnakeHead(Vector2(WIDTH, HEIGHT) / 2, _RADIUS, DEBUG)
snake.add(head)
for i in range(INIT_BODY_SEG):
    head.append()
fruit = pygame.sprite.Group()
for i in range(FRUITS):
    fruit.add(Fruit())
score = 0
# 主体
while running := True:
    # 决定游戏刷新率
    clock.tick(FPS)
    delay = 1000 / clock.get_time()
    smooth_fps.append(delay)
    smooth_fps.pop(0)
    real_fps = math.floor(mean(smooth_fps))
    fps_text = font.render(f"FPS: {real_fps}", False, _BLACK, None)
    score_text = font.render(f"Score: {score}", False, _BLACK, None)
    # 点×时退出。。
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    # 先铺背景和文字
    screen.fill(pygame.Color(_BACKGROUND_COLOR))
    screen.blit(fps_text, (WIDTH - fps_text_width - _FONT_PADDING, _FONT_PADDING))
    screen.blit(score_text, (_FONT_PADDING, _FONT_PADDING))
    # 更新sprites状态
    head.update()
    fruit.update()
    # 绘制sprites
    fruit.draw(screen)
    snake.draw(screen)
    # 更新画布
    pygame.display.flip()
