import pygame
from pygame.math import Vector2


WIDTH = 200
HEIGHT = 200
SIZE = WIDTH, HEIGHT
FPS = 60

class Info(pygame.sprite.Sprite):
    def __init__(self, size):
        super().__init__()
        self.font = pygame.font.Font('simhei.ttf',  30)
        #self.image = pygame.Surface(size)
        self.image = pygame.image.load("bullet.png")
        self.image = pygame.transform.scale_by(self.image, 30)
        self.center = Vector2(size)/2
        self.rect = self.image.get_rect(center = self.center)
        #self.image.fill((100, 100, 100))
        #self.text = self.font.render("Cool", False, pygame.Color(255, 255, 255))
        #self.image.blit(self.text, (70, 10))
        self.components = pygame.sprite.Group()
        self.sidebar = DataBar()
        self.components.add(self.sidebar)

        self.mouse_init = self.center
        self.drag = False

    def update(self, event_list):
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            for event in event_list:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouse_init = Vector2(pos)
                    self.drag = True
                if event.type == pygame.MOUSEBUTTONUP:
                    self.mouse_init = self.center
                    self.drag = False
        if self.drag and pygame.mouse.get_pressed()[0] == 1:
            delta = Vector2(pos) - self.mouse_init
            self.mouse_init = Vector2(pos)
            self.center += delta
            self.rect = self.image.get_rect(center = self.center)


class DataBar(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.font = pygame.font.Font('simhei.ttf',  10)
        self.rect = pygame.Rect(0, 0, 60, 60)
        self.image = pygame.Surface((60, 60))
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
        #screen.fill(pygame.color.Color(255, 255, 255))
        event_list = pygame.event.get()
        for event in event_list:
            if event.type == pygame.QUIT:
                running = False
        game.update(event_list)
        game.draw(screen)
        pygame.display.flip()

pygame.quit()
