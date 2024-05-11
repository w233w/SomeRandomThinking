import math
import random
import pyvista as pv

pl = pv.Plotter()

ranges, scaler = 3, 3


def draw(ranges, scaler):
    for i in range(16):
        for j in range(16):
            height = random.randint(1, round(ranges)) * scaler
            r = 1
            mesh = pv.Cylinder(
                radius=1,
                center=(
                    math.sqrt(3) * i * r - math.sqrt(3) * int((j % 2) == 1) * r / 2,
                    j * r * (3 / 2),
                    height / 2,
                ),
                resolution=6,
                direction=(0, 0, 1),
                height=height,
            )
            pl.add_mesh(mesh, show_edges=True, name=f"{i}-{j}")


def change_h(h):
    global ranges
    global scaler
    scaler = h
    draw(ranges, scaler)


def change_r(r):
    global ranges
    global scaler
    ranges = r
    draw(ranges, scaler)


pl.add_slider_widget(
    change_h, [1, 5], title="Height", pointa=[0.6, 0.9], pointb=[0.9, 0.9]
)
pl.add_slider_widget(
    change_r, [2, 6], title="Varity", fmt="%.0f", pointa=[0.1, 0.9], pointb=[0.4, 0.9]
)
pl.add_axes()
pl.show()
