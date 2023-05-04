import pygame
from pygame.math import Vector2


WIDTH = 720
HEIGHT = 480
SIZE = WIDTH, HEIGHT
FPS = 60

class Info(pygame.sprite.Sprite):
    def __init__(self, size):
        super().__init__()
        self.image = pygame.image.load("th.jpg")
        self.center = Vector2(size)/2
        self.rect = self.image.get_rect(center = self.center)
        self.offset = self.image.get_bounding_rect()
        self.offset.update(self.offset.x+size[0], self.offset.y+size[1], self.offset.w-2*size[0], self.offset.h-2*size[1])
        pygame.draw.rect(self.image, (255,0,0), self.offset, 1)
        self.components = pygame.sprite.Group()
        self.sidebar = DataBar()
        self.components.add(self.sidebar)

        self.draging = False

    def update(self, event_list):
        self.components.update()
        self.components.draw(screen)
        mouse_pos = Vector2(pygame.mouse.get_pos())
        if self.rect.collidepoint(mouse_pos):
            for event in event_list:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouse_start_drag = Vector2(mouse_pos)
                    self.draging = True
                if event.type == pygame.MOUSEBUTTONUP:
                    self.draging = False
        if self.draging:
            delta = Vector2(mouse_pos) - self.mouse_start_drag
            self.mouse_start_drag = Vector2(mouse_pos)
            #if self.offset.collidepoint(self.center): 
            self.center += delta
            self.rect = self.image.get_rect(center = self.center)


class DataBar(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.font = pygame.font.Font('simhei.ttf',  10)
        self.rect = pygame.Rect(0, 0, 60, 480)
        self.image = pygame.Surface((60, 480))
        self.image.fill((200, 200, 200))
        self.text = self.font.render("Cool", False, pygame.Color(0, 0, 0))
        self.image.blit(self.text, (10, 10))

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    game = pygame.sprite.GroupSingle(Info(SIZE))
    running = True
    while running:
        clock.tick(FPS)
        screen.fill(pygame.color.Color(255, 255, 255))
        event_list = pygame.event.get()
        for event in event_list:
            if event.type == pygame.QUIT:
                running = False
        game.update(event_list)
        game.draw(screen)
        pygame.display.flip()

pygame.quit()
