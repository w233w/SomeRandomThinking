"""
简述一下游戏：
玩家扮演一个疯狂的小朋友，他持有一把巨大的雪球发射机。其他的小朋友为了战胜他只好统一战线啦。
玩家在游戏开始时居中于游戏界面，朝向鼠标所在的位置。按下鼠标即可发出一个雪球。
其他小孩作为"敌人"会不间断的从四面八方想你攻来。在他们移动的同时还会投掷雪球。
玩家打出的雪球可以消去敌人的雪球，否则玩家就会受到伤害。
击败敌人可以得到疯狂点数，在菜单中可以用疯狂点数：回复生命，升级武器，购买技能。
升级就是提高伤害，技能举个例子比如雪球可以根据飞行距离不断变大。
随着游戏进行玩家还会得到精华点数，用于升级全局技能。全局技能菜单可以在主界面找到，这些能力在游戏开始时附加于玩家。
随着玩家逐渐变强，敌人也会变强。比如成年人（更高血量）的加入。
"""
import pygame
import random
from itertools import count

# unfinished

# 各类参数
# 窗口大小
WIDTH = 400
HEIGHT = 400
SIZE = WIDTH, HEIGHT
VSIZE = pygame.Vector2(SIZE)
P_LOC = VSIZE // 2
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


class Enemy(pygame.sprite.Sprite):
    pool = []
    for i in range(401):
        pool.append([0, i])
        pool.append([400, i])
        pool.append([i, 0])
        pool.append([i, 400])
    id_gen = count()

    def __init__(self) -> None:
        super().__init__()
        self.pos = pygame.Vector2(random.sample(Enemy.pool, k=1)[0])
        self.id = next(Enemy.id_gen)
        self.image: pygame.Surface = pygame.Surface((16, 16))
        self.image.set_colorkey(Black)
        self.image.fill(Yellow)
        pygame.draw.circle(self.image, Yellow, (8, 8), 16)
        self.rect = self.image.get_rect(center=self.pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.target = P_LOC
        self.speed = 1
        self.atk = 300 // FPS
        self.distance = self.pos.distance_to(P_LOC)
        self.hp = 200 + 50 * (player.sprite.level - 1)

    def update(self) -> None:
        delta = self.pos - self.target
        if not pygame.sprite.collide_mask(self, player.sprite):
            delta.normalize_ip()
            move = delta * self.speed
            self.pos -= move
            self.rect.center = self.pos
        else:
            player.sprite.hp -= 30
        if pygame.sprite.spritecollide(
            self, bullets, dokill=True, collided=pygame.sprite.collide_mask
        ):
            self.hp -= 100
        if self.hp <= 0:
            player.sprite.exp += 15
            self.kill()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, target: pygame.Vector2) -> None:
        super().__init__()
        self.radius = 3
        self.diameter = 6
        self.pos = pygame.Vector2(P_LOC)
        self.image = pygame.Surface((self.diameter, self.diameter))
        self.image.set_colorkey(Black)
        pygame.draw.circle(
            self.image, AlmostBlack, (self.radius, self.radius), self.radius
        )
        self.rect = self.image.get_rect(center=self.pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.target = pygame.Vector2(target)
        self.delta = (self.pos - self.target).normalize()
        self.speed = 3

    def out_of_bound(self):
        return (
            self.rect.x < -self.diameter or self.rect.x > WIDTH + self.diameter,
            self.rect.y < -self.diameter or self.rect.y > HEIGHT + self.diameter,
        )

    def update(self):
        if any(self.out_of_bound()):
            self.kill()
        move = self.delta * self.speed
        self.pos -= move
        self.rect.center = self.pos


class Weapon:
    def __init__(self, init_time) -> None:
        self.pos = P_LOC
        self.last_active = init_time
        self.atk_interval = 600  # ms
        self.ammo: type = Bullet

    @property
    def available(self):
        return pygame.time.get_ticks() - self.last_active > self.atk_interval

    def action(self):
        if self.available:
            target: Enemy = None
            dis: int = 400
            if len(enemys) > 0:
                for enemy in enemys:
                    d = self.pos.distance_to(enemy.pos)
                    if d < dis:
                        target = enemy
                        dis = d
                bullets.add(self.ammo(target.pos))
                self.last_active = pygame.time.get_ticks()


class Player(pygame.sprite.Sprite):
    def __init__(self) -> None:
        super().__init__()
        self.pos = P_LOC
        self.image = pygame.Surface((20, 20))
        self.image.set_colorkey(Black)
        pygame.draw.circle(self.image, Blue, (10, 10), 10)
        self.rect = self.image.get_rect(center=P_LOC)
        self.mask = pygame.mask.from_surface(self.image)
        self.hp = 10000
        self.level = 1
        self.exp = 0
        self.exp_to_next_level = 100
        self.weapons: list[Weapon] = []
        self.weapons.append(Weapon(pygame.time.get_ticks()))

    def update(self) -> None:
        print(len(self.weapons))
        for weapon in self.weapons:
            weapon.action()
        if self.hp <= 0:
            self.image.fill(Black)
            self.weapons = []
        if self.exp >= self.exp_to_next_level:
            self.weapons.append(Weapon(pygame.time.get_ticks()))
            self.exp -= self.exp_to_next_level
            self.exp_to_next_level *= 2
            self.level += 1


pygame.init()
screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption("测试")
clock = pygame.time.Clock()
Font = pygame.font.SysFont("timesnewroman", 15)

enemys = pygame.sprite.Group()
player = pygame.sprite.GroupSingle(Player())
bullets = pygame.sprite.Group()

spawn_rate = 1000
last_enemy = pygame.time.get_ticks()
while running := True:
    clock.tick(FPS)
    event_list = pygame.event.get()
    for event in event_list:
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    if pygame.time.get_ticks() - last_enemy > spawn_rate:
        enemys.add(Enemy())
        last_enemy = pygame.time.get_ticks()
        if spawn_rate >= 605:
            spawn_rate -= 5
    screen.fill(BackgroundColor)
    player.update()
    enemys.update()
    bullets.update()

    player.draw(screen)
    enemys.draw(screen)
    bullets.draw(screen)

    text = Font.render(str(player.sprite.hp), True, Black, None)
    screen.blit(text, (200, 200))
    pygame.display.flip()
