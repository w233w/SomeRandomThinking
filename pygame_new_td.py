from abc import abstractmethod
import pygame
from pygame.math import Vector2
import numpy as np
from typing import Any, Optional, Self

WORLD_SIZE = Vector2(450, 400)


class Draggable:
    def __init__(self, drag_button_filter: list[int] = [1]) -> None:
        self.on_drag = False
        self.placed = False
        self.drag_button_filter = drag_button_filter

    @abstractmethod
    def is_selected(self, mouse_pos) -> bool: ...
    def on_drag_start(self, event: pygame.Event) -> None: ...
    def on_drag_motion(self, event: pygame.Event) -> None: ...
    def on_drag_update(self) -> None: ...
    def on_drag_end(self, event: pygame.Event) -> None: ...

    def can_drag(self) -> bool:
        return not self.placed

    def draggable_update(self, events: list[pygame.Event]) -> None:
        if not self.can_drag():
            return
        if self.on_drag:
            self.on_drag_update()
        for event in events:
            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.dict["button"] in self.drag_button_filter
            ):
                if self.is_selected(event.dict["pos"]):
                    self.on_drag_start(event)
            elif (
                self.on_drag
                and event.type == pygame.MOUSEBUTTONUP
                and event.dict["button"] in self.drag_button_filter
            ):
                self.on_drag_end(event)
            elif self.on_drag and event.type == pygame.MOUSEMOTION:
                self.on_drag_motion(event)


class Building(pygame.sprite.Sprite):
    def __init__(self, d: int, index: int, color: list[int], hp: int, *groups) -> None:
        super().__init__(*groups)
        self.d = d
        self.color = color
        self.max_hp: int = hp
        self.hp = self.max_hp
        self.radius = self.d // 2
        if index >= 0:
            self.pos: Vector2 = Vector2(425 - self.radius, 80 + 50 * index)
        else:
            self.pos: Vector2 = Vector2(0)
        self.o_pos = self.pos
        self.size = Vector2(self.d)
        self.center = self.size // 2
        self.image: pygame.Surface = pygame.Surface(self.size)
        self.image.set_colorkey([0, 0, 0])
        self.rect: pygame.Rect = self.image.get_rect(topleft=self.pos)

        pygame.draw.circle(self.image, self.color, self.center, self.d / 2)

    @property
    def true_center(self):
        return self.pos + self.center


# Power generator
class PG(Building, Draggable):
    def __init__(self, *groups) -> None:
        Building.__init__(self, 16, 0, [255, 0, 0], 100, *groups)
        Draggable.__init__(self)

        self.drag_delta = Vector2()
        self.drag_center = Vector2()
        self.can_connect: list[Self] = []

        self.can_produce = False

    def is_selected(self, mouse_pos) -> bool:
        return self.rect.collidepoint(mouse_pos)

    def on_drag_start(self, event: pygame.Event) -> None:
        self.drag_delta = self.pos - Vector2(event.dict["pos"])
        self.on_drag = True

    def on_drag_update(self) -> None:
        shadow_wire.empty()
        for sp in self.can_connect:
            Wire(self, sp, shadow_wire)

    def on_drag_motion(self, event: pygame.Event) -> None:
        delta_p = Vector2(event.dict["pos"] + self.drag_delta)
        self.pos = delta_p
        self.rect.topleft = self.pos
        self.look()

    def on_drag_end(self, event: pygame.Event) -> None:
        self.on_drag = False
        if pygame.sprite.spritecollide(
            self, source, False, pygame.sprite.collide_circle
        ):
            self.placed = True
            self.can_produce = True
            PG(*self.groups())
            self.remove(shop_item)
            self.add(building)
            wire.add(shadow_wire)
        else:
            self.pos = Vector2(self.o_pos)
            self.rect.topleft = self.pos
            self.can_connect.clear()
        shadow_wire.empty()

    def look(self):
        self.can_connect = [
            sp for sp in building if self.true_center.distance_to(sp.true_center) < 100
        ]

    def update(self, *args: Any, **kwargs: Any) -> None:
        if not self.placed:
            self.draggable_update(kwargs["events"])


# Power transportation tower
class Tower(Building, Draggable):
    def __init__(self, *groups) -> None:
        Building.__init__(self, 8, 1, [0, 0, 255], 20, *groups)
        Draggable.__init__(self)

        self.drag_delta = Vector2()
        self.drag_center = Vector2()
        self.can_connect: list[Self] = []

    def is_selected(self, mouse_pos) -> bool:
        return self.rect.collidepoint(mouse_pos)

    def on_drag_start(self, event: pygame.Event) -> None:
        self.drag_delta = self.pos - Vector2(event.dict["pos"])
        self.on_drag = True

    def on_drag_update(self) -> None:
        shadow_wire.empty()
        for sp in self.can_connect:
            Wire(self, sp, shadow_wire)

    def on_drag_motion(self, event: pygame.Event) -> None:
        delta_p = Vector2(event.dict["pos"] + self.drag_delta)
        self.pos = delta_p
        self.rect.topleft = self.pos
        self.look()

    def on_drag_end(self, event: pygame.Event) -> None:
        self.on_drag = False
        if self.can_connect:
            self.placed = True
            Tower(*self.groups())
            self.remove(shop_item)
            self.add(building)
            wire.add(shadow_wire)
        else:
            self.pos = Vector2(self.o_pos)
            self.rect.topleft = self.pos
            self.can_connect.clear()
        shadow_wire.empty()

    def look(self):
        self.can_connect = [
            sp for sp in building if self.true_center.distance_to(sp.true_center) < 100
        ]

    def update(self, *args: Any, **kwargs: Any) -> None:
        if not self.placed:
            self.draggable_update(kwargs["events"])


class Cannon(Building, Draggable):
    def __init__(self, *groups) -> None:
        Building.__init__(self, 16, 2, [0, 0, 128], 60, *groups)
        Draggable.__init__(self)

        self.drag_delta = Vector2()
        self.drag_center = Vector2()
        self.can_connect: list[Self] = []
        self.target: Optional[Enemy] = None

        self.last_shot = 0
        self.shot_interval = 300

    def is_selected(self, mouse_pos) -> bool:
        return self.rect.collidepoint(mouse_pos)

    def on_drag_start(self, event: pygame.Event) -> None:
        self.drag_delta = self.pos - Vector2(event.dict["pos"])
        self.on_drag = True

    def on_drag_update(self) -> None:
        shadow_wire.empty()
        for sp in self.can_connect:
            Wire(self, sp, shadow_wire)

    def on_drag_motion(self, event: pygame.Event) -> None:
        delta_p = Vector2(event.dict["pos"] + self.drag_delta)
        self.pos = delta_p
        self.rect.topleft = self.pos
        self.look()

    def on_drag_end(self, event: pygame.Event) -> None:
        self.on_drag = False
        if self.can_connect:
            self.placed = True
            Cannon(*self.groups())
            self.kill()
            self.add(building)
            wire.add(shadow_wire)
        else:
            self.pos = Vector2(self.o_pos)
            self.rect.topleft = self.pos
            self.can_connect.clear()
        shadow_wire.empty()

    def look(self):
        self.can_connect = [
            sp for sp in building if self.true_center.distance_to(sp.true_center) < 100
        ]

    def update(self, *args: Any, **kwargs: Any) -> None:
        if not self.placed:
            self.draggable_update(kwargs["events"])
        if self.placed:
            self.last_shot += kwargs.get("delta", 0)
            if self.placed and self.target:
                pass
            for sp in enemys:
                if self.true_center.distance_to(sp.true_center) < 120:
                    self.target = sp
                    break


class Base(Building):
    def __init__(self, *groups) -> None:
        super().__init__(30, -1, [1, 1, 1], 500, *groups)


class Ammo(pygame.sprite.Sprite):
    def __init__(self, pos, direction, *groups) -> None:
        super().__init__(*groups)
        self.d = 5
        self.color = [1, 1, 1]
        self.radius = self.d // 2
        self.pos = Vector2(pos)
        self.direction = Vector2(direction).normalize()
        self.speed = 400
        self.size = Vector2(self.d)
        self.center = self.size // 2
        self.image: pygame.Surface = pygame.Surface(self.size)
        self.image.set_colorkey([0, 0, 0])
        self.rect: pygame.Rect = self.image.get_rect(topleft=self.pos)

        pygame.draw.circle(self.image, self.color, self.center, self.d / 2)

    def update(self, *args: Any, **kwargs: Any) -> None:
        delta: int = kwargs["delta"]  # ms
        self.pos += self.speed * (delta / 1000) * self.direction
        self.rect.topleft = self.pos


class Source(pygame.sprite.Sprite):
    def __init__(self, pos, *groups) -> None:
        super().__init__(*groups)
        self.pos = Vector2(pos)
        self.d = 40
        self.radius = self.d // 2
        self.size = Vector2(self.d)
        self.image = pygame.Surface(self.size)
        self.image.set_colorkey([0, 0, 0])
        self.rect = self.image.get_rect(topleft=self.pos)

        pygame.draw.circle(self.image, [0, 255, 0], self.size // 2, self.d / 2)


class Wire(pygame.sprite.Sprite):
    def __init__(self, start: Building, end: Building, *groups) -> None:
        super().__init__(*groups)
        self.size = WORLD_SIZE
        self.image = pygame.Surface(self.size)
        self.image.set_colorkey([0, 0, 0])
        self.rect = self.image.get_rect(topleft=Vector2(0, 0))
        pygame.draw.line(
            self.image, [128, 128, 128], start.true_center, end.true_center
        )


class Enemy(pygame.sprite.Sprite):
    def __init__(self, *groups) -> None:
        super().__init__(*groups)

    def init(self, d: int, color: list[int], hp: int, pos: Vector2):
        self.d = d
        self.color = color
        self.max_hp: int = hp
        self.hp = self.max_hp
        self.radius = self.d // 2
        self.pos = pos
        self.size = Vector2(self.d)
        self.center = self.size // 2
        self.image: pygame.Surface = pygame.Surface(self.size)
        self.image.set_colorkey([0, 0, 0])
        self.rect: pygame.Rect = self.image.get_rect(topleft=self.pos)

        pygame.draw.circle(self.image, self.color, self.center, self.d / 2)

    @property
    def true_center(self):
        return self.pos + self.center


pygame.init()
scene = pygame.display.set_mode(WORLD_SIZE)
clock = pygame.time.Clock()

wired_map = set()

shop_item = pygame.sprite.Group()
PG(shop_item)
Tower(shop_item)
Cannon(shop_item)

building = pygame.sprite.Group()
base = pygame.sprite.GroupSingle()
Base(building, base)


source = pygame.sprite.Group()
Source(Vector2(200, 200), source)
Source(Vector2(320, 100), source)
Source(Vector2(50, 150), source)

shadow_wire = pygame.sprite.Group()
wire = pygame.sprite.Group()

enemys = pygame.sprite.Group()

spawn_area = pygame.Rect(360, 360, 40, 40)


while True:
    delta = clock.tick(240)
    scene.fill([255, 255, 255])

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    print(shop_item.sprites())
    shop_item.update(events=events)
    building.update(delta=delta)

    bg_left = pygame.Surface([50, 400])
    bg_left.fill(pygame.colordict.THECOLORS["darkorange"])
    scene.blit(bg_left, [400, 0])

    source.draw(scene)
    shop_item.draw(scene)
    building.draw(scene)
    shadow_wire.draw(scene)
    wire.draw(scene)

    pygame.display.flip()
