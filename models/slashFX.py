import pygame

class SlashFX:
    def __init__(self, x, y, big=False):
        self.x = x
        self.y = y
        self.start_time = pygame.time.get_ticks()
        self.duration = 200 if not big else 300
        self.big = big
        self.slash_img_small = pygame.image.load("images/slash.png")
        self.slash_img_big = pygame.image.load("images/slash.png")

    def expired(self):
        return pygame.time.get_ticks() - self.start_time > self.duration

    def draw(self, screen):
        if self.big:
            screen.blit(self.slash_img_big, (self.x - 100, self.y - 100))
        else:
            screen.blit(self.slash_img_small, (self.x - 60, self.y - 60))