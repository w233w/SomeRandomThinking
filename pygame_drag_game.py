import pygame
from pygame.math import Vector2
import numpy as np

drop_event = pygame.event.custom_type()


class Grid(pygame.sprite.Sprite):
    def __init__(self, *groups) -> None:
        super().__init__(*groups)
        self.pos = Vector2(50, 50)  # topleft
        self.size = Vector2(201, 201)
        self.grid_size = 4
        self.grid = np.zeros([4, 4])

        self.image = pygame.Surface(self.size)
        self.image.set_colorkey((0, 0, 0))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect(topleft=self.pos)

        for i in range(self.grid_size + 1):
            pygame.draw.line(self.image, [255, 0, 0], (50 * i, 0), (50 * i, 200))
            pygame.draw.line(self.image, [255, 0, 0], (0, 50 * i), (200, 50 * i))

    def on_grid(self, mouse_pos):
        delta_pos = Vector2(mouse_pos) - self.pos
        coord = delta_pos // 50
        return coord

    def update(self, events: list[pygame.Event]) -> None:
        for event in events:
            if event.type == drop_event:
                if self.rect.collidepoint(pygame.mouse.get_pos()):
                    sp: Block = event.dict["sprite"]
                    center = sp.drag_center_coord
                    y = int(center.x)
                    x = int(center.y)
                    shape = sp.shape
                    size = shape.shape
                    x1, x2, y1, y2 = x, size[0] - x, y, size[1] - y
                    target = (Vector2(pygame.mouse.get_pos()) - self.pos) // 50
                    _y = int(target.x)
                    _x = int(target.y)
                    try:
                        mimic = self.grid.copy()
                        mimic[_x - x1 : _x + x2, _y - y1 : _y + y2] += shape
                        if mimic.max() > 1:
                            raise ValueError()
                        else:
                            self.grid = mimic
                        sp.fixed = True
                        sp.render([255, 0, 0])
                        print(self.grid)
                    except:
                        sp.pos = Vector2(sp.o_pos)
                        sp.rect.topleft = sp.pos


class Block(pygame.sprite.Sprite):
    def __init__(self, pos, shape, *groups) -> None:
        super().__init__(*groups)
        self.o_pos = Vector2(pos)
        self.pos = Vector2(self.o_pos)
        self.shape = np.array(shape)
        self.size = Vector2(self.shape.shape[::-1]) * 50
        self.image = pygame.Surface(self.size)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect(topleft=self.pos)

        self.render([0, 255, 0])

        self.on_drag = False
        self.drag_center = None
        self.drag_center_coord = None
        self.fixed = False

    def render(self, color):
        for i in range(self.shape.shape[1]):
            for j in range(self.shape.shape[0]):
                if self.shape[j][i] == 1:
                    pygame.draw.circle(
                        self.image, color, [25 + 50 * i, 25 + 50 * j], 20
                    )

    def update(self, events: list[pygame.Event]) -> None:
        if not self.fixed:
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.dict["button"] == 1:
                        if self.rect.collidepoint(event.dict["pos"]):
                            delta_p = Vector2(event.dict["pos"]) - self.pos
                            coord = delta_p // 50
                            if self.shape[int(coord.y)][int(coord.x)] == 1:
                                self.drag_center_coord = coord
                                self.on_drag = True
                                self.drag_center = Vector2(event.dict["pos"])
                elif self.on_drag and event.type == pygame.MOUSEBUTTONUP:
                    if event.dict["button"] == 1:
                        self.on_drag = False
                        pygame.event.post(pygame.Event(drop_event, {"sprite": self}))
                        self.pos = self.rect.topleft
                elif self.on_drag and event.type == pygame.MOUSEMOTION:
                    delta_p = Vector2(event.dict["pos"] - self.drag_center)
                    new_pos = self.pos + delta_p
                    self.rect.topleft = new_pos


SHAPE = [
    [[1, 0], [1, 1]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1], [1, 1], [0, 1]],
    [[1]],
    [[1, 1, 1], [1, 0, 0]],
]

pygame.init()
scene = pygame.display.set_mode((1200, 400))
clock = pygame.time.Clock()
g1 = pygame.sprite.GroupSingle()
Grid(g1)
g2 = pygame.sprite.Group()
for i, shape in enumerate(SHAPE):
    Block([200 + 200 * i, 200], shape, g2)

while True:
    clock.tick(30)
    scene.fill([255, 255, 255])
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    g1.update(events)
    g2.update(events)
    g1.draw(scene)
    g2.draw(scene)
    pygame.display.flip()
