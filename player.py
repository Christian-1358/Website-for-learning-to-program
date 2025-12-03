import pygame

class Player:
    def __init__(self, x, y):
        self.image = pygame.image.load("assets/images/player.png")
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 5
        self.light_energy = 100

    def move(self, keys):
        if keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_s]:
            self.rect.y += self.speed
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_d]:
            self.rect.x += self.speed

    def use_light(self):
        if self.light_energy > 0:
            self.light_energy -= 0.2
