from abc import abstractmethod
from itertools import product
import random
from typing import Optional
import pygame
from pygame.math import Vector2
import numpy as np

cancel = pygame.event.custom_type()


class Tower(pygame.sprite.Sprite):
    def __init__(self, coord: tuple[int, int], *groups) -> None:
        super().__init__(*groups)
        self.coord = coord
        self.pos = Vector2(10 + 20 * self.coord[0], 10 + 20 * self.coord[1])
        self.image: pygame.Surface = pygame.Surface([20, 20])
        self.image.set_colorkey([0, 0, 0])
        self.rect: pygame.Rect = self.image.get_rect(center=self.pos)
        self.render()

    @abstractmethod
    def render(self): ...


class Cannon(Tower):
    def __init__(self, coord: tuple[int, int], *groups) -> None:
        super().__init__(coord, *groups)
        self.target: Optional[Enemy] = None
        self.last_shoot = 0
        self.shoot_interval = 500

    def render(self):
        pygame.draw.circle(self.image, [1, 1, 1], Vector2(10), 10)

    def update(self, *args, **kwargs) -> None:
        delta = kwargs["delta"]
        self.last_shoot += delta
        if self.last_shoot > self.shoot_interval and self.target:
            Bullet(self.pos, self.target, bs)
            self.last_shoot -= self.shoot_interval
        elif not self.target:
            self.last_shoot = 0
        if self.target not in es:
            for enemy in es:
                if self.pos.distance_to(enemy.pos) < 40:
                    self.target = enemy


class Enemy(pygame.sprite.Sprite):
    color = {
        1: [255, 0, 0],
        2: [0, 255, 0],
        3: [0, 0, 255],
        4: [0, 255, 255],
        5: [255, 255, 0],
    }

    def __init__(self, pos: Vector2, tier: int, *groups) -> None:
        super().__init__(*groups)
        self.tier = tier
        self.pos = Vector2(pos)
        self.image: pygame.Surface = pygame.Surface([10, 10])
        self.image.set_colorkey([0, 0, 0])
        self.rect: pygame.Rect = self.image.get_rect(center=self.pos)
        pygame.draw.circle(self.image, Enemy.color[self.tier], [5, 5], 5)

    def update(self, *args, **kwargs) -> None:
        flow_map = kwargs["flow_map"]
        coord = self.pos / 20
        if self.pos.x < 20 and self.pos.y < 20:
            self.kill()
        x, y = coord
        low_x, high_x = x - 0.5, x + 0.5
        low_y, high_y = y - 0.5, y + 0.5
        center_x, center_y = int(high_x), int(high_y)
        move_to = Vector2(0)
        for reference in [
            (low_x, low_y),
            (low_x, high_y),
            (high_x, low_y),
            (high_x, high_y),
        ]:
            x, y = reference
            weight = abs(center_x - x) * abs(center_y - y)
            try:
                ref = flow_map[int(y)][int(x)]
            except:
                ref = Vector2(0)
            if ref == Vector2(0):
                _x = int(x) + 0.5
                _y = int(y) + 0.5
                ref = Vector2(self.pos) - Vector2(_x, _y) * 20
                ref.normalize_ip()
            move_to += ref * weight
        if move_to != Vector2(0):
            move_to.normalize_ip()
        self.pos += move_to * (10 + 5 * self.tier) * (kwargs["delta"] / 1000)
        self.rect.center = self.pos

    def render(self):
        pygame.draw.circle(self.image, Enemy.color[self.tier], [5, 5], 5)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos: Vector2, target: Enemy, *groups) -> None:
        super().__init__(*groups)
        self.remain = 300  # ms
        self.pos = Vector2(pos)
        self.target = target
        self.image: pygame.Surface = pygame.Surface([6, 6])
        self.image.set_colorkey([0, 0, 0])
        self.rect: pygame.Rect = self.image.get_rect(center=self.pos)
        pygame.draw.circle(self.image, [1, 1, 1], [3, 3], 2)

    def update(self, *args, **kwargs) -> None:
        global gold
        delta: int = kwargs["delta"]
        self.remain -= delta
        if es.has(self.target):
            if self.remain <= 0:
                self.kill()
                self.target.tier -= 1
                if self.target.tier < 1:
                    self.target.kill()
                    gold += 1
                else:
                    self.target.render()
                return
            to = self.target.pos - self.pos
            to = to * delta / self.remain
            self.pos += to
            self.rect.center = self.pos
        else:
            self.kill()


class MapController:
    def __init__(self) -> None:
        # 0 for pass, 1 for tower base, 2 for obstacles, 3 for base, 4 for enemy spawn,
        self.map = np.array(
            [
                [3, 1, 0, 0, 0, 0, 1, 0, 0, 0],
                [0, 1, 0, 2, 1, 0, 1, 0, 1, 0],
                [0, 1, 0, 2, 0, 0, 1, 0, 1, 0],
                [0, 2, 0, 2, 0, 1, 2, 0, 1, 0],
                [0, 2, 0, 2, 0, 0, 2, 0, 2, 0],
                [0, 2, 0, 2, 0, 0, 2, 0, 2, 0],
                [0, 1, 0, 2, 1, 0, 2, 0, 2, 0],
                [0, 1, 0, 1, 0, 0, 2, 0, 1, 0],
                [0, 1, 0, 1, 0, 1, 2, 0, 1, 0],
                [0, 0, 0, 1, 0, 0, 0, 0, 1, 4],
            ],
            dtype=np.int8,
        )
        self.map = np.array(
            [
                [3, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 1, 2, 2, 2, 1, 1, 0],
                [0, 1, 0, 1, 0, 0, 0, 0, 1, 0],
                [0, 2, 0, 2, 0, 1, 1, 0, 1, 0],
                [0, 2, 0, 2, 0, 2, 1, 0, 2, 0],
                [0, 2, 0, 1, 0, 4, 1, 0, 2, 0],
                [0, 1, 0, 1, 2, 2, 1, 0, 1, 0],
                [0, 1, 0, 0, 0, 0, 0, 0, 1, 0],
                [0, 1, 1, 1, 2, 2, 2, 1, 1, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            ],
            dtype=np.int8,
        )
        self.map2 = np.array(
            [
                [3, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                [1, 0, 0, 1, 0, 0, 2, 0, 0, 1],
                [0, 0, 2, 0, 0, 2, 0, 0, 1, 0],
                [0, 2, 0, 0, 1, 0, 0, 2, 0, 0],
                [0, 0, 0, 1, 0, 0, 1, 0, 0, 0],
                [0, 0, 2, 0, 0, 2, 0, 0, 2, 0],
                [0, 1, 0, 0, 2, 0, 0, 1, 0, 0],
                [1, 0, 0, 1, 0, 0, 2, 0, 0, 1],
                [0, 0, 1, 0, 0, 1, 0, 0, 2, 4],
                [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            ],
            dtype=np.int8,
        )
        self.map_mask = self.map == 2

        self.lowest = (0, 0)

        self.heat_map = self.gen_heat_map()
        self.flow_map = self.gen_flow_map()

    # easy bfs
    def gen_heat_map(self):
        all_possible = list(product(range(10), range(10)))
        heat_map = np.full_like(self.map, fill_value=127, dtype=np.int8)
        heat_map[self.lowest[0]][self.lowest[1]] = 0
        visited = []
        queue: list[tuple[int, int]] = [self.lowest]
        while queue:
            node = queue.pop(0)
            visited.append(node)
            x, y = node
            for direction in [[0, 1], [0, -1], [1, 0], [-1, 0]]:
                new_x = x + direction[0]
                new_y = y + direction[1]
                if (
                    (new_x, new_y) in all_possible
                    and (new_x, new_y) not in visited
                    and not self.map_mask[new_x][new_y]
                ):
                    heat_map[new_x][new_y] = heat_map[x][y] + 1
                    queue.append((new_x, new_y))
        return heat_map

    # easy trivisal
    def gen_flow_map(self):
        all_possible = list(product(range(10), range(10)))
        flow_map = np.full([10, 10], fill_value=None, dtype=pygame.Vector2)
        for x, y in all_possible:
            lr, ud = 0, 0
            v = self.heat_map[x][y]
            if v == 127:
                flow_map[x][y] = Vector2(0)
                continue
            for ab in (1, -1):
                if (x + ab, y) in all_possible and self.heat_map[x + ab, y] < v:
                    lr += ab
                if (x, y + ab) in all_possible and self.heat_map[x, y + ab] < v:
                    ud += ab
            res = [ud, lr]

            v = Vector2(res)
            if v != Vector2(0):
                v.normalize_ip()
            flow_map[x][y] = v
        return flow_map

    def update_flow_map(self):
        self.map_mask = self.map == 2
        self.heat_map = self.gen_heat_map()
        self.flow_map = self.gen_flow_map()

    def show_flow_map(self):
        flow_map = np.full_like(self.map, "", dtype=np.str_)
        for x, y in product(range(10), range(10)):
            if self.flow_map[x][y] == Vector2(0):
                flow_map[x][y] = "·"
            if self.flow_map[x][y] == Vector2(0, 1):
                flow_map[x][y] = "↓"
            if self.flow_map[x][y] == Vector2(0, -1):
                flow_map[x][y] = "↑"
            if self.flow_map[x][y] == Vector2(1, 0):
                flow_map[x][y] = "→"
            if self.flow_map[x][y] == Vector2(-1, 0):
                flow_map[x][y] = "←"
            if self.flow_map[x][y] == Vector2(1, 1):
                flow_map[x][y] = "↘"
            if self.flow_map[x][y] == Vector2(1, -1):
                flow_map[x][y] = "↗"
            if self.flow_map[x][y] == Vector2(-1, 1):
                flow_map[x][y] = "↙"
            if self.flow_map[x][y] == Vector2(-1, -1):
                flow_map[x][y] = "↖"
        print(flow_map)


if __name__ == "__main__":
    controller = MapController()

    pygame.init()
    scene = pygame.display.set_mode((200, 200))
    pygame.display.set_caption("TD")
    clock = pygame.time.Clock()

    ts = pygame.sprite.Group()
    es = pygame.sprite.Group()
    last_e = 1000
    bs = pygame.sprite.Group()

    obstacles = pygame.Surface([20, 20])
    obstacles.fill([192, 192, 192])
    tower_base = pygame.Surface([20, 20])
    tower_base.fill([240, 240, 240])
    base = pygame.Surface([20, 20])
    base.fill([0, 255, 0])
    enemy_spawn = pygame.Surface([20, 20])
    enemy_spawn.fill([255, 0, 0])

    gold = 20
    speed = 1

    while True:
        delta = clock.tick(60)
        pygame.display.set_caption(f"{gold}")
        scene.fill([255, 255, 255])
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.dict["button"] == 1:
                mouse_pos: tuple[int, int] = event.dict["pos"]
                x, y = mouse_pos
                x = x // 20
                y = y // 20
                if controller.map[y][x] == 1 and gold >= 10:
                    gold -= 10
                    controller.map[y][x] = 2
                    Cannon((x, y), ts)
                    controller.update_flow_map()

        for _ in range(speed):  # 倍速
            last_e += delta
            if last_e > 1000:
                Enemy(
                    Vector2(180) + Vector2(random.random() * 20, random.random() * 20),
                    5,
                    es,
                )
                last_e -= 1000
            ts.update(delta=delta / speed)
            es.update(flow_map=controller.flow_map, delta=delta)
            bs.update(delta=delta / speed)

        for i, r in enumerate(controller.map):
            for j, c in enumerate(r):
                if c == 2:
                    scene.blit(obstacles, [20 * j, 20 * i])
                elif c == 1:
                    scene.blit(tower_base, [20 * j, 20 * i])
                elif c == 3:
                    scene.blit(base, [20 * j, 20 * i])
                elif c == 4:
                    scene.blit(enemy_spawn, [20 * j, 20 * i])

        ts.draw(scene)
        es.draw(scene)
        bs.draw(scene)
        pygame.display.flip()
