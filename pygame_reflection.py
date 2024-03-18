import pygame
import random

# 2D光线反射
# 右键发射光线

# 各类参数
# 窗口大小
WIDTH = 400
HEIGHT = 600
SIZE = WIDTH, HEIGHT
CENTER = pygame.Vector2(WIDTH, HEIGHT) / 2
INTERVAL = 50
PLAYER_ZONE_HEIGHT = 100
TARGET_ZONE_HEIGHT = 300
PLAYER_INIT_POSITION = pygame.Vector2(200, 575)

if PLAYER_ZONE_HEIGHT + TARGET_ZONE_HEIGHT + INTERVAL >= HEIGHT:
    raise ValueError("Height over range.")

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


class Player(pygame.sprite.Sprite):
    def __init__(self, pos) -> None:
        super().__init__()
        self.pos = pos
        self.radius = 15
        self.offset = pygame.Vector2(10, 10)
        self.image = pygame.Surface([2 * self.radius, 2 * self.radius])
        self.colorkey = self.image.get_at([0, 0])
        self.image.set_colorkey(self.colorkey)
        self.rect = pygame.draw.circle(
            self.image,
            pygame.Color(255, 0, 0),
            pygame.Vector2(self.radius, self.radius),
            self.radius,
        )

    # 自机控制
    # 返回的值决定了速度

    def _player_control(self):
        left = pygame.key.get_pressed()[pygame.K_a]
        up = pygame.key.get_pressed()[pygame.K_w]
        down = pygame.key.get_pressed()[pygame.K_s]
        right = pygame.key.get_pressed()[pygame.K_d]
        # 按下shift可以加速，目前是三倍速
        shift = 1 + 2 * pygame.key.get_pressed()[pygame.K_LSHIFT]
        del_x = right - left
        del_y = down - up
        border_padding = pygame.Vector2(self.image.get_size()) / 2 + self.offset
        # 限制玩家移动
        if self.pos.x <= border_padding.x and del_x < 0:
            del_x = 0
            self.pos.x = border_padding.x
        elif self.pos.x >= WIDTH - border_padding.x and del_x > 0:
            del_x = 0
            self.pos.x = WIDTH - border_padding.x
        if self.pos.y <= border_padding.y + (HEIGHT - PLAYER_ZONE_HEIGHT) and del_y < 0:
            del_y = 0
            self.pos.y = border_padding.y + (HEIGHT - PLAYER_ZONE_HEIGHT)
        elif self.pos.y >= HEIGHT - border_padding.y and del_y > 0:
            del_y = 0
            self.pos.y = HEIGHT - border_padding.y
        return shift * pygame.Vector2(del_x, del_y)

    def update(self) -> None:
        self.pos += self._player_control()
        self.rect.center = self.pos


def findIntersection(line1: list[pygame.Vector2], line2: list[pygame.Vector2]):
    a, b = line1
    c, d = line2
    n2_x = d.y - c.y
    n2_y = c.x - d.x
    dist_c_n2 = c.x * n2_x + c.y * n2_y
    dist_a_n2 = a.x * n2_x + a.y * n2_y
    dist_b_n2 = b.x * n2_x + b.y * n2_y
    if (dist_a_n2 - dist_c_n2) * (dist_b_n2 - dist_c_n2) >= -1e-15:
        return None
    n1_x = b.y - a.y
    n1_y = a.x - b.x
    dist_c_n1 = a.x * n1_x + a.y * n1_y
    dist_a_n1 = c.x * n1_x + c.y * n1_y
    dist_b_n1 = d.x * n1_x + d.y * n1_y
    if (dist_a_n1 - dist_c_n1) * (dist_b_n1 - dist_c_n1) >= -1e-15:
        return None
    denominator = n1_x * n2_y - n1_y * n2_x
    fraction = (dist_a_n2 - dist_c_n2) / denominator
    return a.x + fraction * n1_y, a.y - fraction * n1_x


class Wall(pygame.sprite.Sprite):
    def __init__(
        self,
        *groups: pygame.sprite.Group,
        p1: pygame.Vector2,
        p2: pygame.Vector2,
        color: pygame.Color,
    ) -> None:
        super().__init__(*groups)
        self.p1 = p1
        self.p2 = p2
        self.color = color

    def vector(self) -> pygame.Vector2:
        vector = self.p1 - self.p2
        return vector.normalize().rotate(90)


test = pygame.sprite.GroupSingle(Player(pygame.Vector2(200, 575)))

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

planes = pygame.sprite.Group()
planes.add(Wall(p1=pygame.Vector2(200, 200), p2=pygame.Vector2(300, 300), color=Blue))
planes.add(Wall(p1=pygame.Vector2(100, 200), p2=pygame.Vector2(200, 300), color=Green))
planes.add(Wall(p1=pygame.Vector2(100, 200), p2=pygame.Vector2(300, 200), color=Yellow))

# 主体
while running := True:
    # 决定游戏刷新率
    clock.tick(FPS)
    # 点×时退出。。
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    # 先铺背景再画sprites
    screen.fill(pygame.Color(BackgroundColor))
    pygame.draw.rect(
        screen,
        Black,
        pygame.Rect(0, HEIGHT - PLAYER_ZONE_HEIGHT, WIDTH, PLAYER_ZONE_HEIGHT),
        10,
    )
    mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
    for plane in planes.sprites():
        pygame.draw.line(screen, plane.color, plane.p1, plane.p2, 3)
        in_vector = (mouse_pos - test.sprite.pos).normalize()
        joint = findIntersection(
            [test.sprite.pos, mouse_pos + in_vector * 600], [plane.p1, plane.p2]
        )
        if joint is not None and pygame.mouse.get_pressed(3)[2]:
            plane_vector = plane.vector()
            out_vector = in_vector - 2.0 * in_vector.dot(plane_vector) * plane_vector
            start = joint
            end = joint + out_vector * 600
            pygame.draw.line(screen, Red, start, end)
            pygame.draw.line(screen, Black, test.sprite.pos, joint)

    # 更新sprites
    # 永远先更新玩家
    test.update()
    # 不会有重叠，所以画不分先后
    test.draw(screen)
    # 更新画布
    pygame.display.flip()
