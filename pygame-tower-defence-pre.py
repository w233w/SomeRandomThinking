import pygame
from pygame.math import Vector2


WIDTH = 200
HEIGHT = 200
FPS = 60

class Info(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.font = pygame.font.Font('simhei.ttf',  30)
        self.rect = pygame.Rect(20, 20, 180, 180)
        self.image = pygame.Surface((160, 160))
        self.image.fill((100, 100, 100))
        self.text = self.font.render("Cool", False, pygame.Color(255, 255, 255))
        self.image.blit(self.text, (100, 10))
        self.components = pygame.sprite.Group()
        self.sidebar = DataBar()
        self.components.add(self.sidebar)

    def update(self):
        self.components.update()
        self.components.draw(self.image)


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

    game = pygame.sprite.GroupSingle(Info())
    running = True
    while running:
        clock.tick(FPS)
        event_list = pygame.event.get()
        for event in event_list:
            if event.type == pygame.QUIT:
                running = False
        game.update()
        game.draw(screen)
        pygame.display.flip()

pygame.quit()
