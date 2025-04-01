import numpy as np
import cv2
from collections import defaultdict
from itertools import product
import random

# 100 * 100 conway life game.
# press and hold left mouse button can draw new live cell on canvas, hold shift to make brush larger.

neighbors = list(product(range(-1, 2), range(-1, 2)))
neighbors.remove((0, 0))

# 初始化参数
size = 200  # 图片
grid_size = 100  # 网格大小
assert (size / grid_size).is_integer()
scale = size // grid_size
grid: dict[tuple[int, int], int] = defaultdict(int)
for i in range(2500):
    grid[(random.randint(0, grid_size), random.randint(0, grid_size))] = 1
B = [3]
S = [2, 3]
next_grid: dict[tuple[int, int], int] = defaultdict(int)
img = np.full((size, size, 3), [255, 255, 255], dtype=np.uint8)


def update_grid():
    global grid, next_grid, img
    for i, j in product(range(grid_size), range(grid_size)):
        raw = grid[(i, j)]
        v = 0
        for neighbor in neighbors:
            true_neighbor = i + neighbor[0], j + neighbor[1]
            v += grid[true_neighbor]
        if raw == 0 and v in B:
            next_grid[(i, j)] = 1
        elif raw == 1 and v not in S:
            next_grid[(i, j)] = 0
        else:
            next_grid[(i, j)] = raw
    grid, next_grid = next_grid, grid
    next_grid.clear()


def redraw():
    global img, grid
    for i, j in product(range(grid_size), range(grid_size)):
        if grid[(i, j)] == 0:
            img[i * scale : (i + 1) * scale, j * scale : (j + 1) * scale] = [255] * 3
        else:
            img[i * scale : (i + 1) * scale, j * scale : (j + 1) * scale] = [0] * 3


def mouse_callback(event, x: int, y: int, flag, userdata):
    global mouse_pressed, grid, scale
    _x = x // scale
    _y = y // scale

    if event == cv2.EVENT_LBUTTONDOWN:
        mouse_pressed = True
        grid[(_y, _x)] = 1

    if event == cv2.EVENT_MOUSEMOVE and mouse_pressed:
        grid[(_y, _x)] = 1
        if flag == cv2.EVENT_FLAG_SHIFTKEY | cv2.EVENT_FLAG_LBUTTON:
            for neighbor in neighbors:
                _nx = _x + neighbor[0]
                _ny = _y + neighbor[1]
                grid[(_ny, _nx)] = 1

    if event == cv2.EVENT_LBUTTONUP:
        mouse_pressed = False


mouse_pressed = False

if __name__ == "__main__":
    cv2.namedWindow("test")
    cv2.setMouseCallback("test", mouse_callback)
    while True:
        cv2.imshow("test", img)
        if not mouse_pressed:
            update_grid()
        redraw()
        mykey = cv2.waitKey(1)
        if mykey & 0xFF == ord("q"):
            break
    cv2.destroyAllWindows()
