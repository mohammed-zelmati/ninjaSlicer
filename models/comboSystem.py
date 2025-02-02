import pygame
class ComboSystem:
    def __init__(self, font, gold_color):
        self.combo = 0
        self.combo_start_time = 0
        self.combo_duration = 2000
        self.font = font
        self.gold_color = gold_color

    def start_combo(self, n):
        self.combo = n
        self.combo_start_time = pygame.time.get_ticks()

    def update(self):
        if pygame.time.get_ticks() - self.combo_start_time > self.combo_duration:
            self.combo = 0

    def draw(self, screen):
        if self.combo > 0:
            screen.blit(self.font.render(f"Combo x{self.combo}", True, self.gold_color), (10, 10))