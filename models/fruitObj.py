import pygame

class FruitObj:
    def __init__(self, img, sliced_imgs, x, y, speed, letter=None, is_ice=False, is_bomb=False):
        self.img = img
        self.sliced_imgs = sliced_imgs
        self.x = x
        self.y = y
        self.speed = speed
        self.letter = letter
        self.is_ice = is_ice
        self.is_bomb = is_bomb
        self.sliced = False
        self.sliced_time = 0

    def move(self, freeze):
        if not freeze:
            self.y += self.speed

    def draw(self, screen, font):
        if not self.sliced:
            screen.blit(self.img, (self.x, self.y))
            # Dessiner la lettre sur le fruit si elle existe
            if self.letter is not None:
                text_surface = font.render(self.letter, True, (255, 255, 255))  # Couleur blanche
                text_rect = text_surface.get_rect(center=(self.x + self.img.get_width() // 2, self.y + self.img.get_height() // 2))
                screen.blit(text_surface, text_rect)
        else:
            # Décaler les tranches pour augmenter l'écart
            slice_gap = 60  # Écart entre les tranches (ajustez cette valeur selon vos besoins)
            screen.blit(self.sliced_imgs[0], (self.x - slice_gap, self.y))  # Tranche gauche
            screen.blit(self.sliced_imgs[1], (self.x + slice_gap, self.y))  # Tranche droite

    def is_clicked(self, pos):
        return self.x <= pos[0] <= self.x + self.img.get_width() and self.y <= pos[1] <= self.y + self.img.get_height()

    def circle_center(self):
        return self.x + self.img.get_width() // 2, self.y + self.img.get_height() // 2, self.img.get_width() // 2