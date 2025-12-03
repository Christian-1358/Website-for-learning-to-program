import pygame, random

class Enemy:
    def __init__(self, x, y):
        self.image = pygame.Surface((30, 30))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 2

    def patrol(self):
        self.rect.x += random.choice([-1, 0, 1]) * self.speed
        self.rect.y += random.choice([-1, 0, 1]) * self.speed
