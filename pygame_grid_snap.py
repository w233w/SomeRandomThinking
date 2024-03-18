import pygame
import numpy as np
from copy import deepcopy

# 网格吸附demo1

# 各类参数
# 窗口大小
WIDTH = 400
HEIGHT = 600
SIZE = WIDTH, HEIGHT
INTERVAL = 50
BEAD_RADIUS = 20

# 刷新率
FPS = 60

# 颜色
BackgroundColor = 255, 229, 204
Black = 0, 0, 0
White = 255, 255, 255
Red = 255, 0, 0
Blue = 0, 0, 255
Green = 0, 255, 0
Yellow = 255, 255, 0


# template for a '+' shape:      template for a 'L' shape：
# [0, 0, 1, 0, 0]                [0, 1, 0]
# [0, 0, 1, 0, 0]                [0, 1, 0]
# [1, 1, 1, 1, 1]                [0, 1, 1]
# [0, 0, 1, 0, 0]
# [0, 0, 1, 0, 0]
# shape must be square, rotate will base on center of the shape
class Board(pygame.sprite.Sprite):
    def __init__(self, template: list[list[int]], pos) -> None:
        super().__init__()
        if len(template) != len(template[0]):
            raise ValueError("Shape must be square")
        shape_size = len(template)
        self.semi_radius = shape_size // 2
        image_size = shape_size * INTERVAL
        self.image = pygame.Surface(pygame.Vector2(image_size, image_size))
        self.image.set_colorkey(Black)
        self.init_pos = pos
        self.pos = pos
        self.rect = self.image.get_rect(center=self.pos)
        self.container = np.array(template)
        for i in range(len(template)):
            for j in range(len(template[0])):
                if template[i][j] == 1:
                    pygame.draw.circle(
                        self.image,
                        Green,
                        pygame.Vector2(INTERVAL * (0.5 + j), INTERVAL * (0.5 + i)),
                        BEAD_RADIUS,
                    )

    def set_pos(self, pos: pygame.Vector2):
        self.pos = pos
        self.rect.center = self.pos

    def rotate(self):
        self.image = pygame.transform.rotate(self.image, 90)

    def update(self, mouse_pos):
        if pygame.mouse.get_pressed(3)[0] and self.rect.collidepoint(mouse_pos):
            self.add(on_drag)
        if on_drag in self.groups():
            self.set_pos(mouse_pos)


class Grid(pygame.sprite.Sprite):
    def __init__(self, size: int, edges: int) -> None:
        super().__init__()
        self.image = pygame.Surface((size + 1, size + 1))
        self.image.fill(Yellow)
        self.rect = pygame.Rect(50, 50, size + 1, size + 1)
        self.edges = edges
        self.grid_size = size / edges
        for i in range(edges + 1):
            pygame.draw.line(
                self.image,
                Black,
                (i * self.grid_size, 0),
                (i * self.grid_size, size),
                5,
            )
            pygame.draw.line(
                self.image,
                Black,
                (0, i * self.grid_size),
                (size, i * self.grid_size),
                5,
            )
        self.container = np.zeros((edges, edges), dtype=np.int16)

    def update(self, mouse_pos):
        if (
            on_drag.sprite is not None
            and not pygame.mouse.get_pressed(3)[0]
            and self.rect.collidepoint(mouse_pos)
        ):
            delta_pos = mouse_pos - pygame.Vector2(50, 50)
            x = int(delta_pos.x // self.grid_size)
            y = int(delta_pos.y // self.grid_size)

            if self.add(on_drag.sprite.container, self.container, y, x):
                new_pos = pygame.Vector2(
                    50 + (0.5 + x) * self.grid_size, 50 + (0.5 + y) * self.grid_size
                )
                on_drag.sprite.set_pos(new_pos)
                on_drag.sprite.image.set_alpha(50)
                on_drag.empty()
            else:
                on_drag.sprite.set_pos(on_drag.sprite.init_pos)
                on_drag.empty()
        elif (
            on_drag.sprite is not None
            and not pygame.mouse.get_pressed(3)[0]
            and not self.rect.collidepoint(mouse_pos)
        ):
            on_drag.sprite.set_pos(on_drag.sprite.init_pos)
            on_drag.empty()

    def isRectContain(self, rect1, rect2):
        rect1_x, rect1_y, rect1_height, rect1_width = rect1
        rect2_x, rect2_y, rect2_height, rect2_width = rect2
        return (
            rect1_y >= rect2_y
            and rect1_y + rect1_width <= rect2_y + rect2_width
            and rect1_x >= rect2_x
            and rect1_x + rect1_height <= rect2_x + rect2_height
        )

    def add(
        self, small: np.ndarray, giant: np.ndarray, target_row: int, target_col: int
    ):
        m_small = np.array(small)
        m_big = np.array(giant)
        m_small_shape = m_small.shape
        m_small_radius = m_small_shape[0] // 2
        m_small_up, m_small_down, m_small_left, m_small_right = 0, 0, 0, 0
        for i in range(m_small_radius):
            x = m_small_radius - (i + 1)
            if 1 in m_small[x]:
                m_small_up = i + 1
            if 1 in m_small[-x - 1]:
                m_small_down = i + 1
            if 1 in m_small[:, x]:
                m_small_left = i + 1
            if 1 in m_small[:, -x - 1]:
                m_small_right = i + 1
        small_rect = (
            target_row - m_small_up,
            target_col - m_small_left,
            m_small_up + m_small_down + 1,
            m_small_left + m_small_right + 1,
        )
        big_rect = 0, 0, self.edges, self.edges
        if not self.isRectContain(small_rect, big_rect):
            return False
        s = m_small[
            m_small_radius - m_small_up : m_small_radius + 1 + m_small_down,
            m_small_radius - m_small_left : m_small_radius + 1 + m_small_right,
        ]
        m_big[
            small_rect[0] : small_rect[0] + small_rect[2],
            small_rect[1] : small_rect[1] + small_rect[3],
        ] += s
        print(m_big)
        if 2 in m_big:
            return False
        return True


# Init pygame & Crate screen
pygame.init()
screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption("测试")
clock = pygame.time.Clock()
# 状态栏
# setting the pygame font style(1st parameter)
# and size of font(2nd parameter)
try:
    Font = pygame.font.SysFont("得意黑斜体", 30)
except:
    Font = pygame.font.SysFont("timesnewroman", 30)

test = pygame.sprite.Group(Grid(300, 6))

on_drag = pygame.sprite.GroupSingle()

template = [
    [0, 0, 1, 0, 0],
    [0, 0, 1, 0, 0],
    [0, 0, 1, 0, 0],
    [0, 0, 1, 1, 1],
    [0, 0, 0, 0, 0],
]

board = pygame.sprite.Group(Board(template, pygame.Vector2(200, 500)))

# 主体
while running := True:
    # 决定游戏刷新率
    clock.tick(FPS)
    # 点×时退出。。
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
    # 先铺背景再画sprites
    screen.fill(pygame.Color(BackgroundColor))
    # 更新sprites
    # 永远先更新玩家
    test.update(mouse_pos)
    board.update(mouse_pos)
    # 不会有重叠，所以画不分先后
    test.draw(screen)
    board.draw(screen)
    # 更新画布
    pygame.display.flip()
