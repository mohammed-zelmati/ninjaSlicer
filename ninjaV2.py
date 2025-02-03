import pygame
import random

# Initialise Pygame
pygame.init()

# Définir les dimensions de la fenêtre
screen_width = 1280
screen_height = 720
screen = pygame.display.set_mode((screen_width, screen_height))

# Charger et redimensionner l'image de fond
background = pygame.image.load('images/fruit.jpg')
background = pygame.transform.scale(background, (screen_width, screen_height))

# Titre de la fenêtre
pygame.display.set_caption("FRUIT SLICER GAME")

# Définir les nouvelles dimensions pour les images
new_width = 100
new_height = 100

# Couleurs
WHITE, BLACK, RED, GREEN, BLUE = (255, 255, 255), (0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255)
YELLOW, ORANGE, PURPLE, BROWN, PINK = (255, 255, 0), (255, 165, 0), (128, 0, 128), (165, 42, 42), (255, 192, 203)

# Police
FONT = pygame.font.SysFont('Roboto', 50)
SMALL_FONT = pygame.font.SysFont('Roboto', 25)

# Chargement des sons
son_tranche_fruit = pygame.mixer.Sound('son/tranche_fruit.mp3')
son_tranche_glacon = pygame.mixer.Sound('son/tranche_glacon.mp3')
son_tranche_bombe = pygame.mixer.Sound('son/tranche_bombe.mp3')

# Fonction pour charger et redimensionner les images
def load_and_resize_image(file_name, width, height):
    image = pygame.image.load(file_name)
    return pygame.transform.scale(image, (width, height))

# Charger et redimensionner les images des fruits
fruit_images = [
    # load_and_resize_image("images/banane.png", new_width, new_height),
    # load_and_resize_image("images/cerise.png", new_width, new_height),
    # load_and_resize_image("images/fraise.png", new_width, new_height),
    load_and_resize_image("images/kiwi.png", new_width, new_height),
    load_and_resize_image("images/pomme.png", new_width, new_height),
    load_and_resize_image("images/orange.png", new_width, new_height)
]

fruit_slices = [
    # [load_and_resize_image("images/banane-split1.png", new_width, new_height),
    #  load_and_resize_image("images/banane-split2.png", new_width, new_height)],
    # [load_and_resize_image("images/cerise-split1.png", new_width, new_height),
    #  load_and_resize_image("images/cerise-split2.png", new_width, new_height)],
    # [load_and_resize_image("images/fraise-split1.png", new_width, new_height),
    #  load_and_resize_image("images/fraise-split2.png", new_width, new_height)],
    [load_and_resize_image("images/kiwi-split1.png", new_width, new_height),
     load_and_resize_image("images/kiwi-split2.png", new_width, new_height)],
    [load_and_resize_image("images/pomme-split1.png", new_width, new_height),
     load_and_resize_image("images/pomme-split2.png", new_width, new_height)],
    [load_and_resize_image("images/orange-split1.png", new_width, new_height),
     load_and_resize_image("images/orange-split2.png", new_width, new_height)]
]

# Images de la bombe et du glaçon
ice_image = load_and_resize_image("images/glacon.png", new_width, new_height)
bomb_image = load_and_resize_image("images/bombe.png", new_width, new_height)

# Classe pour le Fruit
class Fruit:
    def __init__(self, image, slices, x, y, speed, letter=None):
        self.image = image
        self.slices = slices
        self.x = x
        self.y = y
        self.speed = speed
        self.sliced = False
        self.letter = letter  # Stocker la lettre

    def draw(self):
        if self.sliced:
            screen.blit(self.slices[0], (self.x - 90, self.y)) 
            screen.blit(self.slices[1], (self.x + 90, self.y)) 
        else:
            screen.blit(self.image, (self.x, self.y))

        if self.letter:
            display_text(self.letter, FONT, WHITE, self.x + new_width // 2 - 20, self.y + new_height // 2 - 20)

    def move(self):
        self.y += self.speed

    def is_clicked(self, mouse_pos):
        fruit_rect = pygame.Rect(self.x, self.y, new_width, new_height)
        if self.sliced:
            slice_rect1 = pygame.Rect(self.x - 40, self.y, new_width, new_height)
            slice_rect2 = pygame.Rect(self.x + 40, self.y, new_width, new_height)
            return slice_rect1.collidepoint(mouse_pos) or slice_rect2.collidepoint(mouse_pos)
        else:
            return fruit_rect.collidepoint(mouse_pos)

# Fonction pour créer des objets (fruits, glaçon, bombe) et attribuer des lettres
def create_object(objects):
    x = random.randint(20, screen_width - 20)
    y = 0
    speed = random.uniform(0.8, 1)  # Vitesse entre 0.2 et 0.5 (plus lent)

    obj_type = random.choice(["fruit", "ice", "bomb"])
    letter = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")  # Attribuer une lettre aléatoire

    if obj_type == "fruit":
        index = random.randint(0, len(fruit_images) - 1)
        obj = Fruit(fruit_images[index], fruit_slices[index], x, y, speed, letter)
    elif obj_type == "ice":
        obj = Fruit(ice_image, [ice_image, ice_image], x, y, speed, letter)
    elif obj_type == "bomb":
        obj = Fruit(bomb_image, [bomb_image, bomb_image], x, y, speed, letter)

    objects.append(obj)


# Fonction pour afficher le texte à l'écran
def display_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))
    return pygame.Rect(x, y, img.get_width(), img.get_height())

# Afficher le menu
def afficher_menu():
    menu_running = True
    clock = pygame.time.Clock()
    while menu_running:
        screen.blit(background, (0, 0))  # Toujours redessiner l'arrière-plan

        display_text("Menu du jeu", FONT, BROWN, 540, 50)
       # Définition des rectangles pour les zones cliquables
        play_rect = pygame.Rect(1280 // 2 - 100, 300, 200, 50)
        quit_rect = pygame.Rect(1280 // 2 - 100, 450, 200, 50)

        # Dessiner les rectangles pour les zones cliquables

        pygame.draw.rect(screen, BLACK, play_rect)
        pygame.draw.rect(screen, BLACK, quit_rect)

        # Calculer la largeur et la hauteur du texte et centrer le texte dans les zones
        play_text = "1. Jouer"
        quit_text = "4. Quitter"

        # Affichage du texte centré dans les zones cliquables
        play_text_surface = SMALL_FONT.render(play_text, True, GREEN)
        quit_text_surface = SMALL_FONT.render(quit_text, True, GREEN)

        # Positionner le texte au centre du rectangle
        play_text_rect = play_text_surface.get_rect(center=play_rect.center)
        quit_text_rect = quit_text_surface.get_rect(center=quit_rect.center)

        # Afficher les textes centrés
        screen.blit(play_text_surface, play_text_rect)
        screen.blit(quit_text_surface, quit_text_rect)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return "quit"  # Si l'utilisateur ferme la fenêtre, quitter

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                # Vérifier si l'utilisateur a cliqué sur "Jouer"
                if play_rect.collidepoint(mouse_pos):
                    return "play"  # Lancer le jeu

                # Vérifier si l'utilisateur a cliqué sur "Quitter"
                elif quit_rect.collidepoint(mouse_pos):
                    pygame.quit()  # Quitter le jeu
                    return "quit"
        
        clock.tick(60)  # Limiter les mises à jour pour un rendu fluide

def game_loop():
    running = True
    clock = pygame.time.Clock()
    objects = []
    score = 0
    strikes = 0
    pause_time = 0
    paused = False

    ice_creation_time = 0  # Temps pour contrôler la création des glaçons
    ice_creation_interval = 6000  # 6000 ms = 6 secondes (pour un glaçon chaque 6 secondes)

    bomb_creation_time = 0  # Temps pour contrôler la création des bombes
    bomb_creation_interval = 10000  # 10000 ms = 10 secondes (pour une bombe chaque 10 secondes)
    
    # Temps pour la création des fruits (deux fruits chaque seconde)
    fruit_creation_time = 0  # Temps pour contrôler la création des fruits
    fruit_creation_interval = 500  # 500 ms = 0.5 seconde (pour deux fruits par seconde)

    while running:
        screen.blit(background, (0, 0))  # Toujours redessiner l'arrière-plan

        # Vérifier les événements de la souris (clique) et du clavier (touche)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break  # Sortir immédiatement de la boucle si la fenêtre est fermée

            # Vérifier si une touche du clavier est pressée
            if event.type == pygame.KEYDOWN and not paused:
                key_pressed = pygame.key.name(event.key).upper()  # Récupère la touche appuyée et la convertit en majuscule
                
                # Vérifier pour chaque objet si la lettre correspond à la touche appuyée
                for obj in objects:
                    if obj.letter == key_pressed and not obj.sliced:
                        obj.sliced = True
                        son_tranche_fruit.play()  # Ajouter un son lors du tranchage
                        score += 1  # Ajouter un point pour le fruit tranché
                        break  # Sortir de la boucle dès qu'un fruit est tranché

            # Vérification des clics de souris
            if event.type == pygame.MOUSEBUTTONDOWN and not paused:
                mouse_pos = pygame.mouse.get_pos()

                for obj in objects:
                    if not obj.sliced and obj.is_clicked(mouse_pos):
                        obj.sliced = True
                        son_tranche_fruit.play()  # Ajouter un son lors du tranchage

                        if obj.image == ice_image:
                            paused = True
                            pause_time = pygame.time.get_ticks()  # Enregistrer l'heure actuelle pour la pause
                        elif obj.image == bomb_image:
                            running = False  # Arrêter le jeu si la bombe est touchée
                            display_text("Vous avez frappé une bombe ! Jeu terminé", FONT, (255, 0, 0), screen_width // 2 - 350, screen_height // 2 - 20)
                            pygame.display.flip()  # Afficher le message avant de quitter
                            pygame.time.wait(3000)  # Attendre quelques secondes avant de quitter
                            break  # Quitter la boucle du jeu
                        else:
                            score += 1

                        # Retirer l'objet après un court délai pour afficher les tranches
                        pygame.time.set_timer(pygame.USEREVENT, 500)  # Timer pour la suppression après 500ms
                        break  # Sortir de la boucle après avoir traité un clic

        # Si le jeu est en pause
        if paused:
            if pygame.time.get_ticks() - pause_time >= 3000:  # 3 secondes de pause
                paused = False  # Reprendre le jeu

        if not paused:
            for obj in objects:
                obj.move()
                obj.draw()

                if obj.y > screen_height:
                    strikes += 1
                    objects.remove(obj)

            # Créer deux fruits chaque seconde
            if pygame.time.get_ticks() - fruit_creation_time >= fruit_creation_interval:
                create_object(objects)  # Créer le premier fruit
                create_object(objects)  # Créer le second fruit
                fruit_creation_time = pygame.time.get_ticks()  # Réinitialiser le timer

            # Créer une bombe toutes les 10 secondes
            if pygame.time.get_ticks() - bomb_creation_time >= bomb_creation_interval:
                create_object(objects)  # Créer une bombe
                bomb_creation_time = pygame.time.get_ticks()  # Réinitialiser le timer pour la bombe

            # Créer un glaçon toutes les 6 secondes
            if pygame.time.get_ticks() - ice_creation_time >= ice_creation_interval:
                create_object(objects)  # Créer un glaçon
                ice_creation_time = pygame.time.get_ticks()  # Réinitialiser le timer pour le glaçon

            if strikes >= 3:
                running = False

        # Afficher le score et les strikes avec les bons arguments pour `display_text`
        display_text(f"Score: {score}", FONT, WHITE, 10, 10)
        display_text(f"Strikes: {strikes}", FONT, WHITE, 10, 50)

        # Vérifier la fin du jeu
        if not running:
            if score >= 10:
                display_text("Vous avez gagné !", FONT, (0, 255, 0), screen_width // 2 - 100, screen_height // 2 - 50)
            elif strikes >= 3:
                display_text("Dommage, vous n'avez pas la vitesse * jeu terminé *", FONT, (255, 0, 0), screen_width // 2 - 200, screen_height // 2 - 50)

            pygame.display.flip()
            pygame.time.wait(3000)
            return False
        
        pygame.display.flip()
        clock.tick(60)


def main():
    menu_choice = afficher_menu()
    
    if menu_choice == "play":
        game_loop()  # Lancer le jeu quand "Jouer" est sélectionné
    elif menu_choice == "quit":
        pygame.quit()  # Quitter si "Quitter" est sélectionné


if __name__ == "__main__":
    main()