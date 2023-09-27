import pygame
import random

# 网格吸附demo1

# 各类参数
# 窗口大小
WIDTH = 640
HEIGHT = 640
SIZE = WIDTH, HEIGHT
VSIZE = pygame.Vector2(SIZE)
GRIDS_SIZE = 240
EDGES = 5
if EDGES not in [4, 5, 6]:
    raise ValueError("Size can only be 4, 5, or 6.")
INTERVAL = GRIDS_SIZE // EDGES
TOWER_GRID_SIZE = 40
ENEMY_SIZE = 40

# 刷新率
FPS = 60

# 颜色
BackgroundColor = 248, 248, 255
BaseColor = 173, 213, 162
Black = 0, 0, 0
Line = 20, 35, 52
AlmostBlack = 1, 1, 1
White = 255, 255, 255
Red = 255, 0, 0
Blue = 0, 0, 255
Green = 0, 255, 0
Yellow = 255, 255, 0


class FloatText(pygame.sprite.Sprite):
    def __init__(self, pos: pygame.Vector2, font: pygame.font.Font, text: str) -> None:
        super().__init__()
        self.pos = pygame.Vector2(pos)
        self.text = text
        text_size = font.size(text)
        self.image = pygame.Surface(text_size)
        self.image.set_colorkey(Black)
        text_surface = font.render(self.text, False, Line, None)
        self.image.blit(text_surface, [0, 0])
        self.rect = self.image.get_rect(center=self.pos)
        self.init_time = pygame.time.get_ticks()

    def update(self) -> None:
        if pygame.time.get_ticks() - self.init_time >= 1000:
            self.kill()
        self.pos -= pygame.Vector2(0, 1)
        self.rect.center = self.pos


class SmallBullet(pygame.sprite.Sprite):
    def __init__(self, pos: pygame.Vector2, speed: pygame.Vector2) -> None:
        super().__init__()
        self.radius = 3
        self.image = pygame.Surface([2 * self.radius, 2 * self.radius])
        self.image.set_colorkey(Black)
        self.pos = pygame.Vector2(pos)
        self.velocity = speed
        self.shift = self.velocity.rotate(90).normalize() * random.uniform(-3, 3)
        self.pos += self.shift
        self.rect = self.image.get_rect(center=self.pos)
        self.offset = 2 * self.radius
        pygame.draw.circle(self.image, AlmostBlack, [1.5, 1.5], 1.2)

    def update(self):
        self.pos += self.velocity
        self.rect.center = self.pos
        if (
            self.pos.x >= WIDTH + self.offset
            or self.pos.x <= 0 - self.offset
            or self.pos.y >= HEIGHT + self.offset
            or self.pos.y <= 0 - self.offset
        ):
            self.kill()


class BaseTower(pygame.sprite.Sprite):
    def __init__(self, pos: pygame.Vector2) -> None:
        super().__init__()
        self.init_pos = pygame.Vector2(pos)
        self.pos = self.init_pos
        self.shape = pygame.Vector2(TOWER_GRID_SIZE, TOWER_GRID_SIZE)
        self.image = pygame.Surface(self.shape)
        self.image.set_colorkey(Black)
        self.rect = self.image.get_rect(center=self.pos)
        self.on_shop = True
        self.affordable = False
        self.placed = False
        self.grid_pos = None
        self.draging = False
        self.init_time = pygame.time.get_ticks()

    def update(self, event_list: list[pygame.event.Event]) -> None:
        raise RuntimeError("Can't be called here.")

    @property
    def hoving(self) -> bool:
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        return self.rect.collidepoint(mouse_pos)


class TestTower(BaseTower):
    def __init__(self, pos: pygame.Vector2) -> None:
        super().__init__(pos)
        self.color = Yellow
        pygame.draw.circle(self.image, self.color, self.shape / 2, 15)
        self.last_text = self.init_time

    def update(self, event_list: list[pygame.event.Event]):
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        if pygame.time.get_ticks() - self.last_text > 200:
            if self.placed:
                player_bullets.add(SmallBullet(self.pos, pygame.Vector2(13, 0)))
            self.last_text = pygame.time.get_ticks()
        for event in event_list:
            if not self.placed:
                if event.type == pygame.MOUSEBUTTONDOWN and self.hoving:
                    self.draging = True
                elif event.type == pygame.MOUSEBUTTONUP and self.hoving:
                    self.draging = False
                    for grid in grids:
                        if grid.rect.collidepoint(mouse_pos) and grid.available:
                            print("placed tower")
                            self.pos = grid.pos
                            self.rect.center = self.pos
                            self.placed = True
                            self.grid_pos = grid.cord
                            grid.tower = self
                            towers.add(TestTower(self.init_pos))
                            break
                    else:
                        self.pos = self.init_pos
                        self.rect.center = self.pos
        if self.draging:
            self.pos = mouse_pos
            self.rect.center = self.pos


class BaseEnemy(pygame.sprite.Sprite):
    def __init__(self, pos: pygame.Vector2, road: int, side: str) -> None:
        super().__init__()
        self.pos = pygame.Vector2(pos)
        self.road = road
        self.side = side
        match self.side:
            case "up":
                self.base_speed = pygame.Vector2(0, 1)
            case "down":
                self.base_speed = pygame.Vector2(0, -1)
            case "left":
                self.base_speed = pygame.Vector2(1, 0)
            case "right":
                self.base_speed = pygame.Vector2(-1, 0)
        self.speed_modifier = 1
        self.image = pygame.Surface([ENEMY_SIZE, ENEMY_SIZE])
        self.image.set_colorkey(Black)
        self.rect = self.image.get_rect(center=self.pos)
        self.init_time = pygame.time.get_ticks()

    def update(self) -> None:
        raise RuntimeError("Can't be called here.")


class TestEnemy(BaseEnemy):
    def __init__(self, pos: pygame.Vector2, road: int, side: str) -> None:
        super().__init__(pos, road, side)
        pygame.draw.rect(self.image, Red, pygame.Rect(10, 10, 30, 30))

    def update(self) -> None:
        self.pos += self.base_speed * self.speed_modifier
        self.rect.center = self.pos
        if pygame.time.get_ticks() - self.init_time >= 2000:
            self.kill()


class Grids(pygame.sprite.Sprite):
    def __init__(self, size: int, edges: int) -> None:
        super().__init__()
        self.image = pygame.Surface(SIZE)
        self.image.set_colorkey(Black)
        self.size = pygame.Vector2(size)
        self.interval = pygame.Vector2(INTERVAL)
        self.top_left_pos = (VSIZE - pygame.Vector2(size)) / 2
        self.rect = self.image.get_rect(center=pygame.Vector2(SIZE) / 2)
        # for e in range(1, edges):
        for e in range(0, edges + 1):
            pygame.draw.line(
                self.image,
                Line,
                pygame.Vector2(0, self.top_left_pos.y + e * self.interval.y),
                pygame.Vector2(WIDTH, self.top_left_pos.y + e * self.interval.y),
                1,
            )
            pygame.draw.line(
                self.image,
                Line,
                pygame.Vector2(self.top_left_pos.x + e * self.interval.x, 0),
                pygame.Vector2(self.top_left_pos.x + e * self.interval.x, HEIGHT),
                1,
            )
        for i in range(edges**2):
            x, y = i // edges, i % edges
            # if (x, y) in [
            #     (0, 0),
            #     (0, edges - 1),
            #     (edges - 1, 0),
            #     (edges - 1, edges - 1),
            # ]:
            #     continue
            coordinate = (x, y)
            pos = self.top_left_pos + pygame.Vector2(
                INTERVAL * (0.5 + y), INTERVAL * (0.5 + x)
            )
            grids.add(Grid(pos=pos, coordinate=coordinate))


class Grid(pygame.sprite.Sprite):
    def __init__(self, pos: pygame.Vector2, coordinate: tuple) -> None:
        super().__init__()
        self.image = pygame.Surface([INTERVAL, INTERVAL])
        self.image.set_colorkey(Black)
        self.image.fill(BaseColor)
        self.pos = pos
        self.rect = self.image.get_rect(center=self.pos)
        self.cord = coordinate
        self.available = True
        self.tower: BaseTower = None

    def update(self) -> None:
        if self.tower:
            self.available = False


class Info(pygame.sprite.Sprite):
    def __init__(self) -> None:
        super().__init__()
        self.size = (WIDTH - GRIDS_SIZE) / 2, (HEIGHT - GRIDS_SIZE) / 2
        self.image = pygame.Surface(self.size)
        self.image.set_colorkey(Black)
        self.pos = pygame.Vector2(0, HEIGHT - (HEIGHT - GRIDS_SIZE) / 2)
        self.rect = self.image.get_rect(topleft=self.pos)
        self.image.fill([192, 192, 192])


# Init pygame & Crate screen
pygame.init()
screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption("测试")
clock = pygame.time.Clock()
# 状态栏
# setting the pygame font style(1st parameter)
# and size of font(2nd parameter)
Font = pygame.font.SysFont("timesnewroman", 15)

pygame.event.set_allowed([pygame.QUIT, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP])

grids = pygame.sprite.Group()
grid = pygame.sprite.GroupSingle(Grids(GRIDS_SIZE, EDGES))
towers = pygame.sprite.Group(TestTower(pygame.Vector2(100, 100)))
texts = pygame.sprite.Group()
player_bullets = pygame.sprite.Group()
enemy_top = [pygame.sprite.Group() for i in range(EDGES)]
enemy_down = [pygame.sprite.Group() for i in range(EDGES)]
enemy_left = [pygame.sprite.Group() for i in range(EDGES)]
enemy_right = [pygame.sprite.Group() for i in range(EDGES)]
enemy_test = pygame.sprite.Group()
enemy_test.add(TestEnemy(pygame.Vector2(300, 300), 0, "left"))
info_bar = pygame.sprite.GroupSingle(Info())

# 主体
while running := True:
    # 决定游戏刷新率
    clock.tick(FPS)
    # 点×时退出。。
    event_list = pygame.event.get()
    for event in event_list:
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    # 先铺背景再画sprites
    screen.fill(pygame.Color(BackgroundColor))
    # 更新sprites
    # 永远先更新玩家
    grids.update()
    info_bar.update()
    grid.update()
    towers.update(event_list)
    texts.update()
    player_bullets.update()
    enemy_test.update()
    # 不会有重叠，所以画不分先后
    grids.draw(screen)
    info_bar.draw(screen)
    grid.draw(screen)
    towers.draw(screen)
    texts.draw(screen)
    player_bullets.draw(screen)
    enemy_test.draw(screen)
    # 更新画布
    pygame.display.flip()
