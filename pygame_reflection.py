import pygame
from typing import Literal

# 2D光线反射
# 右键发射光线

# 各类参数
# 窗口大小
WIDTH = 400
HEIGHT = 600
SIZE = WIDTH, HEIGHT
CENTER = pygame.Vector2(WIDTH, HEIGHT) / 2
PLAYER_ZONE_HEIGHT = 100
TARGET_ZONE_HEIGHT = 300
PLAYER_INIT_POSITION = pygame.Vector2(200, 575)

# 计算余量Epsilon, 越大越不容易出现意外
# 但也会降低精度，极限角度可能不会反射
EPS = -1e6

# 刷新率
FPS = 60

# 颜色
BackgroundColor = pygame.Vector3(255, 229, 204)
Black = pygame.Vector3(0, 0, 0)
White = pygame.Vector3(255, 255, 255)
Red = pygame.Vector3(255, 0, 0)
Blue = pygame.Vector3(0, 0, 255)
Green = pygame.Vector3(0, 255, 00)
Yellow = pygame.Vector3(255, 255, 0)
Gray = pygame.Vector3(128, 128, 128)
Cyan = pygame.Vector3(0, 255, 255)
Brown = pygame.Vector3(147, 101, 31)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, *groups) -> None:
        super().__init__(*groups)
        self.pos: pygame.Vector2 = pos
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
        self.last_shot = pygame.time.get_ticks()

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
        if pygame.mouse.get_pressed(3)[2]:
            mouse_pos = pygame.mouse.get_pos()
            in_vector = (mouse_pos - self.pos).normalize()
            lasers.add(Laser(self.pos, in_vector))
        if (
            pygame.mouse.get_pressed(3)[0]
            and pygame.time.get_ticks() - self.last_shot >= 1000
        ):
            print(123)
            self.last_shot = pygame.time.get_ticks()


class Wall(pygame.sprite.Sprite):
    colors: dict[str, tuple[int, int, int]] = {
        "Steel": Gray,
        "Wood": Brown,
        "Glass": Cyan,
    }

    def __init__(
        self,
        p1: pygame.Vector2,
        p2: pygame.Vector2,
        material: Literal["Steel", "Wood", "Glass"] = "Wood",
        *groups: pygame.sprite.Group,
    ) -> None:
        super().__init__(*groups)
        self.p1 = p1
        self.p2 = p2
        self.color = Wall.colors[material]
        self.material: Literal["Steel", "Wood", "Glass"] = material
        self.image = pygame.Surface(SIZE)
        self.image.set_colorkey(Black)
        self.rect = self.image.get_rect(center=CENTER)
        pygame.draw.line(self.image, self.color, self.p1, self.p2, 2)

    def vector(self) -> pygame.Vector2:
        vector = self.p1 - self.p2
        return vector.normalize().rotate(90)


class Laser(pygame.sprite.Sprite):
    def __init__(
        self,
        start: pygame.Vector2,
        direction: pygame.Vector2,
        level: int = 10,
        *groups,
    ):
        super().__init__(*groups)
        self.start = start
        self.direction = direction
        self.level = level
        self.max_level: int = 10
        self.image = pygame.Surface(SIZE)
        self.image.set_colorkey(BackgroundColor)
        self.image.fill(BackgroundColor)
        self.rect = self.image.get_rect(center=CENTER)

    def find_intersection(
        self,
        line1: tuple[pygame.Vector2, pygame.Vector2],
        line2: tuple[pygame.Vector2, pygame.Vector2],
    ):
        a, b = line1
        c, d = line2
        n2_x = d.y - c.y
        n2_y = c.x - d.x
        dist_c_n2 = c.x * n2_x + c.y * n2_y
        dist_a_n2 = a.x * n2_x + a.y * n2_y
        dist_b_n2 = b.x * n2_x + b.y * n2_y
        if (dist_a_n2 - dist_c_n2) * (dist_b_n2 - dist_c_n2) >= EPS:
            return None
        n1_x = b.y - a.y
        n1_y = a.x - b.x
        dist_c_n1 = a.x * n1_x + a.y * n1_y
        dist_a_n1 = c.x * n1_x + c.y * n1_y
        dist_b_n1 = d.x * n1_x + d.y * n1_y
        if (dist_a_n1 - dist_c_n1) * (dist_b_n1 - dist_c_n1) >= EPS:
            return None
        denominator = n1_x * n2_y - n1_y * n2_x
        fraction = (dist_a_n2 - dist_c_n2) / denominator
        return pygame.Vector2(a.x + fraction * n1_y, a.y - fraction * n1_x)

    def draw(self, start: pygame.Vector2, direction: pygame.Vector2, level: int):
        color = BackgroundColor + ((Red - BackgroundColor) * level / self.max_level)
        # 记录所有击中的面
        hits: dict[Wall, pygame.Vector2] = {}
        for plane in walls.sprites():
            joint = self.find_intersection(
                (start, start + direction * 1000), (plane.p1, plane.p2)
            )
            if joint is not None:
                hits[plane] = joint

        # if hits != {}: # 必定hit, 因为可见区域外包了一层不反射的Wall。
        hits_ordered = sorted(
            hits.items(),
            key=lambda d: d[1].distance_squared_to(start),
        )  # 按hit的距离排列
        for p, joint in hits_ordered:
            if p.material == "Wood":  # 木墙既不反射也不透光
                break
            elif p.material == "Glass" or p.material == "Steel":  # 玻璃/金属墙能反射
                if level > 1:
                    plane_vector = p.vector()
                    out_vector = (
                        direction - 2.0 * direction.dot(plane_vector) * plane_vector
                    )
                    self.draw(joint, out_vector.normalize(), level - 1)
                if p.material == "Steel":  # 金属墙不透光
                    break
        pygame.draw.line(self.image, color, start, joint)

    def update(self):
        self.draw(self.start, self.direction, self.level)
        if not pygame.mouse.get_pressed(3)[2]:
            self.kill()


player = pygame.sprite.GroupSingle(Player(pygame.Vector2(200, 575)))
lasers = pygame.sprite.GroupSingle()
walls = pygame.sprite.Group()
walls.add(
    Wall(p1=pygame.Vector2(200, 200), p2=pygame.Vector2(300, 300), material="Glass")
)
walls.add(
    Wall(p1=pygame.Vector2(100, 200), p2=pygame.Vector2(200, 230), material="Glass")
)
walls.add(
    Wall(p1=pygame.Vector2(100, 200), p2=pygame.Vector2(330, 200), material="Glass")
)
walls.add(Wall(p1=pygame.Vector2(20, 20), p2=pygame.Vector2(380, 20), material="Steel"))

# 构建可视区域外的井字形围墙
walls.add(
    Wall(p1=pygame.Vector2(-10, -5), p2=pygame.Vector2(WIDTH + 10, -5), material="Wood")
)
walls.add(
    Wall(
        p1=pygame.Vector2(-5, -10), p2=pygame.Vector2(-5, HEIGHT + 10), material="Wood"
    )
)
walls.add(
    Wall(
        p1=pygame.Vector2(WIDTH + 5, -10),
        p2=pygame.Vector2(WIDTH + 5, HEIGHT + 10),
        material="Wood",
    )
)
walls.add(
    Wall(
        p1=pygame.Vector2(-10, HEIGHT + 5),
        p2=pygame.Vector2(WIDTH + 10, HEIGHT + 5),
        material="Wood",
    )
)

# 主体
# Init pygame & Crate screen
pygame.init()
screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption("测试")
clock = pygame.time.Clock()
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
    # 更新sprites
    # 永远先更新玩家
    player.update()
    walls.update()
    lasers.update()
    # 不会有重叠，所以画不分先后
    player.draw(screen)
    walls.draw(screen)
    lasers.draw(screen)
    # 更新画布
    pygame.display.flip()
