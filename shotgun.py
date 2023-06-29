#试图模拟2D上帝视角射击游戏中的散弹枪的弹道。

import matplotlib.pyplot as plt
import math
import numpy as np
from copy import deepcopy
from pygame import Vector2

# init
enemy_pos = Vector2(9, 119)
self_pos = Vector2(0, 0)
num_of_ammo = 5
inter_angle = np.radians(7)
samp = 100

# targeting
dx, dy = enemy_pos-self_pos
start_angle = math.atan2(dy, dx)

# gen bullet
xs, ys = [], []
poses = [[deepcopy(self_pos)] for _ in range(num_of_ammo)]
for i in range(samp):
    for a in range(-num_of_ammo//2 + 1, num_of_ammo//2 + 1):
        del_x = math.cos(start_angle + a * inter_angle)
        del_y = math.sin(start_angle + a * inter_angle)
        delta = Vector2(del_x, del_y)
        poses[a].append(poses[a][-1] + delta)

# draw
plt.figure(figsize=(3, 3))
plt.axis([-150, 150, -150, 150])
plt.plot(*enemy_pos, marker='x', color='red')
for pos in poses:
    xs, ys = [], []
    for j in range(samp):
        xs.append(pos[j][0])
        ys.append(pos[j][1])
    plt.plot(xs, ys, color='black')
plt.show()
