import numpy as np
from scipy.spatial import KDTree
import pygame
import random
import math


# 两个种群,狼和羊都要生存下去
# 初始比例为4:1
# 遗传算法拟合纳什平衡
# 羊吃到草就能活,丰饶的草（水果）才有力气繁殖.
# 丰饶的食物随机刷新
# 狼比羊跑得快一点,转弯速度也比.
# 场地为圆形山谷,有边界无障碍物.
# Unfinished


class MyKDTree(object):
    """
    Used to find nearest pygame.sprite

    A super short KD-Tree for points...
    so concise that you can copypasta into your homework
    without arousing suspicion.

    This implementation only supports Euclidean distance.

    The points can be any array-like type, e.g:
        lists, tuples, numpy arrays.

    Usage:
    1. Make the KD-Tree:
        `kd_tree = KDTree(points, dim)`
    2. You can then use `get_knn` for k nearest neighbors or
       `get_nearest` for the nearest neighbor

    points are be a list of points: [[0, 1, 2], [12.3, 4.5, 2.3], ...]
    """

    def __init__(self, points, dim, dist_sq_func=None):
        """Makes the KD-Tree for fast lookup.

        Parameters
        ----------
        points : list<point>
            A list of points.
        dim : int
            The dimension of the points.
        dist_sq_func : function(point, point), optional
            A function that returns the squared Euclidean distance
            between the two points.
            If omitted, it uses the default implementation.
        """

        if dist_sq_func is None:
            dist_sq_func = lambda a, b: sum((x - b[i]) ** 2 for i, x in enumerate(a))

        def make(points, i=0):
            if len(points) > 1:
                points.sort(key=lambda x: x[i])
                i = (i + 1) % dim
                m = len(points) >> 1
                return [make(points[:m], i), make(points[m + 1 :], i), points[m]]
            if len(points) == 1:
                return [None, None, points[0]]

        import heapq

        def get_knn(node, point, k, return_dist_sq, heap, i=0, tiebreaker=1):
            if node is not None:
                dist_sq = dist_sq_func(point, node[2])
                dx = node[2][i] - point[i]
                if len(heap) < k:
                    heapq.heappush(heap, (-dist_sq, tiebreaker, node[2]))
                elif dist_sq < -heap[0][0]:
                    heapq.heappushpop(heap, (-dist_sq, tiebreaker, node[2]))
                i = (i + 1) % dim
                # Goes into the left branch, then the right branch if needed
                for b in (dx < 0, dx >= 0)[: 1 + (dx * dx < -heap[0][0])]:
                    get_knn(
                        node[b],
                        point,
                        k,
                        return_dist_sq,
                        heap,
                        i,
                        (tiebreaker << 1) | b,
                    )
            if tiebreaker == 1:
                return [
                    (-h[0], h[2]) if return_dist_sq else h[2] for h in sorted(heap)
                ][::-1]

        self._get_knn = get_knn
        self._root = make(points)

    def get_nearest(self, point, return_dist_sq=True):
        """Returns the nearest neighbor.

        Parameters
        ----------
        point : array-like
            The point.
        return_dist_sq : boolean
            Whether to return the squared Euclidean distance.

        Returns
        -------
        array-like
            The nearest neighbor.
            If the tree is empty, returns `None`.
            If `return_dist_sq` is true, the return will be:
                (dist_sq, point)
            else:
                point
        """
        l = self._get_knn(self._root, point, 1, return_dist_sq, [])
        return l[0] if len(l) else None


class MyObject(pygame.sprite.Sprite):
    def __init__(
        self, pos: pygame.Vector2, color: tuple[int, int, int], *groups
    ) -> None:
        super().__init__(*groups)
        self.image = pygame.Surface((10, 10))
        self.image.set_colorkey((0, 0, 0))
        self.pos = pygame.Vector2(pos)
        self.rect = self.image.get_rect(center=self.pos)
        pygame.draw.circle(self.image, color, (5, 5), 5)
        self.mask = pygame.mask.from_surface(self.image)
        self.init_time = pygame.time.get_ticks()


class Fruit(MyObject):
    def __init__(self, pos: pygame.Vector2, *groups) -> None:
        super().__init__(pos, (255, 192, 203), *groups)

    def update(self) -> None:
        pass


class SheepBody(MyObject):
    def __init__(
        self, pos: pygame.Vector2, color: tuple[int, int, int], *groups
    ) -> None:
        super().__init__(pos, color, *groups)
        self.remaining = 8

    def update(self) -> None:
        if self.remaining < 0:
            self.kill()


class Animal(MyObject):
    def __init__(
        self, pos: pygame.Vector2, color: tuple[int, int, int], *groups
    ) -> None:
        super().__init__(pos, color, *groups)
        self.fullness = 1
        self.max_angle_speed_per_second = np.pi // 2


class Sheep(Animal):
    def __init__(self, pos, *groups) -> None:
        """
        羊可以原地2s吃草,提供一点饱腹度.可以吃丰饶的食物源,提供1点饱腹度和繁殖基础.每20秒消耗一点饱腹,为负数时死亡.二饱腹且有繁殖基础且没有威胁时可以交配.满值3饱腹.
        羊的基因型如下:
            a群聚性:羊会尽可能的贴近同类
            b贪吃:即使有狼在附近也会去找丰饶的食物
            c多迁徙:即使没有狼在附近也会高速移动，食物消耗频率-(3-5)秒
            d后代优先:交配即使有威胁
            e高警戒范围:提高羊的警戒范围
            f多食:饱腹为二且有繁殖基础的情况下,会试图吃到3饱腹.
        """
        super().__init__(pos, (192, 192, 192), *groups)

        self.close_to_other_sheep: bool = random.getrandbits(1)
        self.find_fruit_on_threat: bool = random.getrandbits(1)
        self.keep_running_without_threat: bool = random.getrandbits(1)
        self.breeding_on_threat: bool = random.getrandbits(1)
        self.heigh_threat_detect_range: bool = random.getrandbits(1)
        self.over_eating: bool = random.getrandbits(1)

        self.on_threat = False
        self.threat_detect_range = 60
        self.can_breed = False
        self.living = True

    def update(self, wolfsKDTree, fruitsKDTree) -> None:
        pass


class Wolf(Animal):
    def __init__(self, pos, *groups) -> None:
        """
        狼捕到羊后,羊会变成羊尸.狼可以花8秒吃掉羊,每只羊提供两点饱腹值.每15-20秒消耗一点饱腹值,为负数时死亡.三饱腹度时可以交配.满值4饱腹.
        狼的基因型:
            a囤积食物:只吃半只羊,羊尸留存60秒.狼不会离开食物太远.饱腹0时会优先回去找食物.羊尸会被其它狼吃.
            b抢食:饱腹小于2时优先吃羊尸,若出现争抢.饱腹低的狼有50%概率死亡.
            c共谋:尽可能和其他狼一起狩猎,锁定附近狼的目标附近最近的另一只羊。
            d提速:每个饱腹消耗周期内,且剩余时间大于10秒,且至少有一点饱腹时最多一次,减少5秒饱腹倒计时,使得自身速度+50%.
            e多食:饱腹为三且没有繁殖对象的情况下,会试图吃到4饱腹.
        """
        super().__init__(pos, (1, 1, 1), *groups)
        self.save_food = random.getrandbits(1)
        self.get_food_from_other = random.getrandbits(1)
        self.cooperation = random.getrandbits(1)
        self.over_speed = random.getrandbits(1)
        self.over_eating = random.getrandbits(1)

    def update(self, sheepsKDTree, sheepsbodyKDTree) -> None:
        pass


playground_radius = 400
init_wolf = 500
wolfs = pygame.sprite.Group()
init_sheep = 2000
sheeps = pygame.sprite.Group()
sheeps_dead_body = pygame.sprite.Group()
init_fruit = 500
fruits = pygame.sprite.Group()


def rand_in_r(r):
    random_theta = random.random() * math.pi * 2
    random_r = math.sqrt(random.random()) * r
    x = math.cos(random_theta) * random_r
    y = math.sin(random_theta) * random_r
    return pygame.Vector2(x, y)


def build_KDTree(group: pygame.sprite.Group[MyObject]):
    collection = []
    for sprite in group:
        collection.append(sprite.pos)
    return KDTree(collection)


for _ in range(init_wolf):
    wolfs.add(Wolf(rand_in_r(playground_radius)))

for _ in range(init_sheep):
    sheeps.add(Sheep(rand_in_r(playground_radius)))

for _ in range(init_fruit):
    fruits.add(Fruit(rand_in_r(playground_radius)))


pygame.init()
screen = pygame.display.set_mode((800, 800))
pygame.display.set_caption("test")
clock = pygame.time.Clock()
while running := True:
    clock.tick(60)
