from typing import Any, Sequence
from cv2 import rotate
import pygame
from pygame import Vector2
from pygame import gfxdraw
from math import pi


class Tank(pygame.sprite.Sprite):
    def __init__(self, *groups) -> None:
        super().__init__(*groups)
        self.image_size = Vector2(60)
        self.image_center = self.image_size / 2
        self.image: pygame.Surface = pygame.Surface([60, 60])
        self.image.set_colorkey([0, 0, 0])
        self.pos = Vector2(200)
        self.rect: pygame.Rect = self.image.get_rect(center=self.pos)
        # base
        self.base_dir = Vector2(0, 1)
        self.base_speed = 0
        self.base_acc = 5
        self.base_halt_acc = 20
        self.base_max_speed = 20
        self.base_angle_speed = 90
        # top
        self.top_dir = Vector2(0)

        self.render()

    def render(self) -> None:
        if self.image is None:
            raise ValueError()
        self.image.fill([0, 0, 0])
        left_points: Sequence = [
            list(self.image_center + self.base_dir.rotate(20) * 20),
            list(self.image_center + self.base_dir.rotate(45) * 20),
            list(self.image_center + self.base_dir.rotate(135) * 20),
            list(self.image_center + self.base_dir.rotate(160) * 20),
        ]
        gfxdraw.aapolygon(self.image, left_points, [255, 0, 0])
        gfxdraw.filled_polygon(self.image, left_points, [255, 0, 0])
        right_points: Sequence = [
            list(self.image_center + self.base_dir.rotate(-20) * 20),
            list(self.image_center + self.base_dir.rotate(-45) * 20),
            list(self.image_center + self.base_dir.rotate(-135) * 20),
            list(self.image_center + self.base_dir.rotate(-160) * 20),
        ]
        gfxdraw.aapolygon(self.image, right_points, [255, 0, 0])
        gfxdraw.filled_polygon(self.image, right_points, [255, 0, 0])

    def move(self, delta: float) -> None:
        moving_forward = pygame.key.get_pressed()[pygame.K_w]
        moving_backward = pygame.key.get_pressed()[pygame.K_s]
        turn_left = pygame.key.get_pressed()[pygame.K_a]
        turn_right = pygame.key.get_pressed()[pygame.K_d]
        if moving_forward:
            self.base_speed += self.base_acc * delta
        if moving_backward:
            self.base_speed -= self.base_acc * delta
        if not moving_forward and not moving_backward:
            if self.base_speed < 0:
                self.base_speed += self.base_halt_acc * delta
                self.base_speed = min(0, self.base_speed)
            elif self.base_speed > 0:
                self.base_speed -= self.base_halt_acc * delta
                self.base_speed = max(0, self.base_speed)
        rotate = 0
        if turn_right:
            rotate += self.base_angle_speed * delta
        if turn_left:
            rotate -= self.base_angle_speed * delta
        self.base_dir = self.base_dir.rotate(rotate).normalize()
        self.pos += self.base_dir * self.base_speed

        self.rect.center = self.pos

    def update(self, *args: Any, **kwargs: Any) -> None:
        self.move(kwargs["delta"] / 1000)
        self.render()


# 开始运行
pygame.init()
screen = pygame.display.set_mode([400, 400])
clock = pygame.time.Clock()
tank = pygame.sprite.GroupSingle(Tank())
while True:
    delta = clock.tick(30)
    screen.fill([255, 255, 255])
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    tank.update(delta=delta)
    tank.draw(screen)
    pygame.display.flip()
