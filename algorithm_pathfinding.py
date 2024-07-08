import matplotlib.pyplot as plt
import matplotlib.patches as pth
from collections import namedtuple
from itertools import product
from typing import Tuple
import random

Tile = namedtuple("Tile", ["name", "cost"])

random.seed(123211)


class Map:
    def __init__(self, size: int = 15) -> None:
        pool = [Tile("road", 1), Tile("woods", 3), Tile("mountain", 999)]
        self.map: dict[Tuple[int, int], Tile] = {}
        self.size = size
        for p in product(range(size), range(size)):
            self.map[p] = random.choice(pool)

    def get_possible_move(self, pos: Tuple[int, int], energy: int):
        queue: list[Tuple[int, int]] = [pos]
        hist: dict[Tuple[int, int], int] = {pos: energy}
        directions = ((0, 1), (0, -1), (1, 0), (-1, 0))
        path = []
        # 逻辑
        # 目的：找到所有当前能量值能抵达的位置，体力不允许为负值，但可以是为零。
        # 使用dfs算法，每次探索的限制是：
        #   下一个位置消耗的体力大于等于当前体力；
        #   若下一个位置曾经抵达过；下一个位置的剩余体力若是大于（当前体力-下一个消耗体力）则提前停止探索。
        #   下一个位置必须还在地图中
        while queue:
            target = queue.pop()
            path.append(target)
            for direction in directions:
                next_pos = target[0] + direction[0], target[1] + direction[1]
                if (
                    next_pos in self.map
                    and next_pos not in queue
                    and self.map[next_pos].cost <= hist[target]
                ):
                    hist[next_pos] = hist[target] - self.map[next_pos].cost
                    queue.append(next_pos)
        return hist


class Map2:
    def __init__(self, size: int = 15) -> None:
        pool = [Tile("road", 1), Tile("woods", 3), Tile("mountain", 999)]
        self.map: dict[Tuple[int, int], Tile] = {}
        self.size = size
        for p in product(range(size), range(size)):
            self.map[p] = random.choice(pool)

    def __getitem__(self, pos) -> Tile:
        return self.map[pos]

    def get_possible_move(self, pos: Tuple[int, int], energy: int, plot=False):
        queue: list[Tuple[int, int]] = [pos]
        hist: dict[Tuple[int, int], int] = {pos: energy}
        directions = ((0, 1), (0, -1), (1, 0), (-1, 0))
        if plot:
            fig = plt.figure(figsize=(5, 5))
            ax = fig.add_subplot()
            for i, j in product(range(self.size), range(self.size)):
                if self[i, j].name == "road":
                    ax.add_patch(pth.Rectangle([i, j], 1, 1, color="lightgray"))
                elif self[i, j].name == "woods":
                    ax.add_patch(pth.Rectangle([i, j], 1, 1, color="lightgreen"))
                elif self[i, j].name == "mountain":
                    ax.add_patch(pth.Rectangle([i, j], 1, 1, color="gray"))

        path = []

        # 逻辑
        # 目的：找到所有当前能量值能抵达的位置，体力不允许为负值，但可以是为零。
        # 使用dfs算法，每次探索的限制是：
        #   下一个位置消耗的体力大于等于当前体力；
        #   若曾经分支抵达过下一个位置；下一个位置的剩余体力若是大于（当前体力-下一个消耗体力）则提前停止探索。
        #   下一个位置必须还在地图中
        while queue:
            target = queue.pop()
            path.append(target)
            for direction in directions:
                next_pos = target[0] + direction[0], target[1] + direction[1]
                if (
                    next_pos in self.map
                    and next_pos not in queue
                    and self.map[next_pos].cost <= hist[target]
                ):
                    if plot:
                        ax.add_patch(
                            pth.Circle(
                                (next_pos[0] + 0.5, next_pos[1] + 0.5),
                                0.25,
                                color="red",
                            )
                        )
                    hist[next_pos] = hist[target] - self.map[next_pos].cost
                    queue.append(next_pos)
        if plt:
            ax.add_patch(pth.Circle((pos[0] + 0.5, pos[1] + 0.5), 0.25, color="orange"))
            ax.set_xlim(0, self.size)
            ax.set_ylim(0, self.size)
            plt.show()
        return hist


class Map3:
    def __init__(self, size: int = 15) -> None:
        pool = [Tile("road", 1), Tile("woods", 3), Tile("mountain", 999)]
        self.map: dict[Tuple[int, int], Tile] = {}
        self.size = size
        for p in product(range(size), range(size)):
            self.map[p] = random.choice(pool)

    def __getitem__(self, pos) -> Tile:
        return self.map[pos]

    def get_possible_move(self, pos: Tuple[int, int], energy: int, plot=False):
        queue: list[Tuple[int, int]] = [pos]
        hist: dict[Tuple[int, int], int] = {pos: energy}
        directions = ((0, 1), (0, -1), (1, 0), (-1, 0))

        if plot:
            fig = plt.figure(figsize=(5, 5))
            ax = fig.add_subplot()
            for i, j in product(range(self.size), range(self.size)):
                if self[i, j].name == "road":
                    ax.add_patch(pth.Rectangle([i, j], 1, 1, color="lightgray"))
                elif self[i, j].name == "woods":
                    ax.add_patch(pth.Rectangle([i, j], 1, 1, color="lightgreen"))
                elif self[i, j].name == "mountain":
                    ax.add_patch(pth.Rectangle([i, j], 1, 1, color="gray"))

        # 逻辑
        # 目的：找到所有当前能量值能抵达的位置，体力不允许为负值，但可以是为零。
        # 使用dfs算法，每次探索的限制是：
        #   下一个位置消耗的体力大于等于当前体力；
        #   若曾经分支抵达过下一个位置；下一个位置的剩余体力若是大于（当前体力-下一个消耗体力）则提前停止探索。
        #   下一个位置必须还在地图中
        while queue:
            target = queue.pop()
            for direction in directions:
                next_pos = target[0] + direction[0], target[1] + direction[1]
                if (
                    next_pos in self.map
                    and next_pos not in queue
                    and self.map[next_pos].cost <= hist[target]
                ):
                    if plot:
                        ax.add_patch(
                            pth.Circle(
                                (next_pos[0] + 0.5, next_pos[1] + 0.5),
                                0.25,
                                color="red",
                            )
                        )
                    hist[next_pos] = hist[target] - self.map[next_pos].cost
                    queue.append(next_pos)
        if plt:
            ax.add_patch(pth.Circle((pos[0] + 0.5, pos[1] + 0.5), 0.25, color="orange"))
            ax.set_xlim(0, self.size)
            ax.set_ylim(0, self.size)
            plt.show()
        return hist


available_move = Map3(21).get_possible_move((7, 7), 7, True)
