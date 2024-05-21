import math
import random
import pyvista as pv
import numpy as np
from typing import Tuple, Self, Literal
from collections import namedtuple, defaultdict


_Hex = namedtuple("Hex", ("q", "r", "s"))


def Hex(q: int, r: int, s: int):
    assert q + r + s == 0, "q + r + s must be 0"
    return _Hex(q, r, s)


hex_directions = [
    Hex(0, -1, 1),
    Hex(1, -1, 0),
    Hex(1, 0, -1),
    Hex(0, 1, -1),
    Hex(-1, 1, 0),
    Hex(-1, 0, 1),
]


def hex_direction(direction: Literal[0, 1, 2, 3, 4, 5]):
    return hex_directions[direction]


def hex_add(a: _Hex, b: _Hex):
    return Hex(a.q + b.q, a.r + b.r, a.s + b.s)


def hex_neighbor(hex: _Hex, direction: Literal[0, 1, 2, 3, 4, 5]):
    return hex_add(hex, hex_direction(direction))


class Vector3:
    def __init__(self, x: float, y: float, z: float) -> None:
        self.x: float = x
        self.y: float = y
        self.z: float = z
        self.xyz: Tuple[float, float, float] = (x, y, z)

    def __add__(self, o: Self) -> Self:
        return Vector3(self.x + o.x, self.y + o.y, self.z + o.z)

    def __iter__(self):
        return iter(self.xyz)

    def __getitem__(self, i):
        if i == 0:
            return self.x
        elif i == 1:
            return self.y
        elif i == 3:
            return self.z
        else:
            raise IndexError()

    def __repr__(self):
        return f"<{self.x}, {self.y}, {self.z}>"


class HexCylinder:
    def __init__(self, coord: _Hex, height: int) -> None:
        r = 1
        w = 2 * r
        h = r * math.sqrt(3)
        # 按照cube方法构建的坐标系
        self.coord = coord
        # 将坐标转换成世界坐标。
        center: Vector3 = Vector3(
            (self.coord.r - self.coord.s) * h / 2,
            self.coord.q * w * 3 / 4,
            0,
        )
        self.height: int = height
        self.v_map = []
        # 自上而下将六边形六个点一一列出
        for he in range(self.height + 1):
            self.v_map.extend(
                [
                    center + Vector3(-h / 2, -w / 4, self.height - he),
                    center + Vector3(-h / 2, w / 4, self.height - he),
                    center + Vector3(0, w / 2, self.height - he),
                    center + Vector3(h / 2, w / 4, self.height - he),
                    center + Vector3(h / 2, -w / 4, self.height - he),
                    center + Vector3(0, -w / 2, self.height - he),
                ]
            )

    def get_meshs(self, neighbor_heights: list[int] = [0] * 6):
        if len(neighbor_heights) != 6:
            raise ValueError()
        faces = []
        # 点是自上而下的，顶面自然取前6个值
        top_face = [6, 0, 1, 2, 3, 4, 5]
        # 底面取最后6个值
        buttom_face = [
            6,
            self.height * 6,
            self.height * 6 + 1,
            self.height * 6 + 2,
            self.height * 6 + 3,
            self.height * 6 + 4,
            self.height * 6 + 5,
        ]
        faces.append(top_face)
        faces.append(buttom_face)
        num_faces = 2
        for i in range(6):
            # 计算和邻居的高度差，只在有差的地方绘制面
            delta_height = self.height - neighbor_heights[i]
            # 本身比邻居矮时，这面不存在
            if delta_height <= 0:
                continue
            num_faces += delta_height
            # 每个单位高度画一个方形
            for j in range(delta_height):
                # i用来取六边形上连续的两个点，如i=0时取0和1.
                # j用来取高度
                # 面的前两个点是高点，后两个点是低点
                # 四个点的位置：
                # 1 2
                # 4 3
                a, b = i + j * 6, (i + 1) % 6 + j * 6
                face = [4, a, b, b + 6, a + 6]
                faces.append(face)
        # 从Vector3转成list
        v_map = np.array(list(map(list, self.v_map)))
        # pyvista要求将面的列表合并到一起
        faces = np.concatenate(faces)
        return pv.PolyData(v_map, faces, n_faces=num_faces)


if __name__ == "__main__":
    pl = pv.Plotter()

    x, y = 15, 15

    grids: dict[_Hex, int] = defaultdict(int)

    for i in range(x):
        for j in range(y):
            grids[Hex(i, j, 0 - i - j)] = random.randint(7, 10)

    for i in range(x):
        for j in range(y):
            hexgon = Hex(i, j, 0 - i - j)
            neighbor_heights: list[int] = []
            for x in range(6):
                nei = hex_neighbor(hexgon, x)
                neighbor_heights.append(grids[nei])
            mesh = HexCylinder(hexgon, grids[hexgon]).get_meshs(neighbor_heights)
            pl.add_mesh(
                mesh,
                color="w",
                show_edges=True,
                split_sharp_edges=True,
                pbr=True,
                metallic=1,
                roughness=0.5,
            )

    pl.add_axes()
    pl.set_background("black", top="white")
    pl.show()
