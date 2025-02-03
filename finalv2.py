import pygame
import random
import math
import sys

pygame.init()

# -------------------------
# CONFIGURATION DE LA FENÊTRE
# -------------------------
screen_w, screen_h = 1280, 720
screen = pygame.display.set_mode((screen_w, screen_h))
pygame.display.set_caption("FRUIT NINJA - Version Améliorée")

# -------------------------
# CHARGEMENT DES ASSETS AVEC GESTION DES ERREURS
# -------------------------
def load_image(path, width=None, height=None):
    """
    Charge une image et la redimensionne si nécessaire.
    En cas d'erreur, affiche un message et quitte le programme.
    """
    try:
        img = pygame.image.load(path).convert_alpha()
        if width and height:
            img = pygame.transform.scale(img, (width, height))
        return img
    except Exception as e:
        print(f"Erreur lors du chargement de l'image {path}: {e}")
        pygame.quit()
        sys.exit()

def load_sound(path):
    """
    Charge un son et gère les erreurs.
    """
    try:
        return pygame.mixer.Sound(path)
    except Exception as e:
        print(f"Erreur lors du chargement du son {path}: {e}")
        return None

# -------------------------
# POLICES & COULEURS
# -------------------------
FONT       = pygame.font.SysFont('Roboto', 50)
SMALL_FONT = pygame.font.SysFont('Roboto', 25)
WHITE = (255,255,255)
BLACK = (0,0,0)
RED   = (255,0,0)
GREEN = (0,255,0)
BROWN = (165,42,42)
GOLD  = (255,215,0)

# -------------------------
# CHARGEMENT DU FOND ET DES ASSETS AUDIO
# -------------------------
bg_img = load_image("images/fruit.jpg", screen_w, screen_h)

# Sons
snd_fruit  = load_sound("son/tranche_fruit.mp3")
snd_ice    = load_sound("son/tranche_glacon.mp3")
snd_bomb   = load_sound("son/tranche_bombe.mp3")
snd_combo  = load_sound("son/combo.mp3")  # son de combo

# Musiques pour menu et jeu
MENU_MUSIC = "son/ambiance.mp3"
GAME_MUSIC = "son/musique_ambiance.mp3"

# -------------------------
# CHAÎNES DE CARACTERES MULTILINGUES (EN/FR)
# -------------------------
LANG = {
    "en": {
        "menu_title":   "Game Menu",
        "play":         "Play",
        "lang":         "Language",
        "diff":         "Difficulty",
        "quit":         "Quit",
        "score":        "Score",
        "bomb_over":    "You hit a bomb! GAME OVER",
        "strike_over":  "You reached 3 strikes! GAME OVER",
        "final_score":  "Final Score",
        "lives":        "Lives",
        "easy":         "Easy",
        "normal":       "Normal",
        "hard":         "Hard",
        "back":         "Back",
        "resume":       "Resume",
        "pause_menu":   "Game Paused",
        "main_menu":    "Main Menu"
    },
    "fr": {
        "menu_title":   "Menu du jeu",
        "play":         "Jouer",
        "lang":         "Langue",
        "diff":         "Difficulté",
        "quit":         "Quitter",
        "score":        "Score",
        "bomb_over":    "Vous avez tranché une bombe ! GAME OVER",
        "strike_over":  "3 fruits manqués ! GAME OVER",
        "final_score":  "Score Final",
        "lives":        "Vies",
        "easy":         "Facile",
        "normal":       "Normal",
        "hard":         "Difficile",
        "back":         "Retour",
        "resume":       "Continuer",
        "pause_menu":   "Jeu en pause",
        "main_menu":    "Menu principal"
    }
}

def draw_text(text, font, color, x, y):
    """Affiche un texte sur l'écran."""
    surf = font.render(text, True, color)
    screen.blit(surf, (x, y))

# -------------------------
# FONCTION DE CHARGEMENT ET REDIMENSIONNEMENT D'IMAGES
# -------------------------
def load_and_resize_image(path, w, h):
    return load_image(path, w, h)

# -------------------------
# CHARGEMENT DES IMAGES DE SLASH ET DES ICONES
# -------------------------
slash_img_small = load_and_resize_image("images/slash.png", 120, 120)
slash_img_big   = load_and_resize_image("images/slash.png", 200, 200)
heart_icon      = load_and_resize_image("images/red_lives.png", 40, 40)

# -------------------------
# FONCTION D'INTERSECTION LIGNE-CERCLE (pour la détection de tranche en glissant la souris)
# -------------------------
def line_circle_intersect(x1, y1, x2, y2, cx, cy, radius):
    """
    Détermine si une ligne entre (x1, y1) et (x2, y2) intersecte un cercle centré en (cx, cy) avec un rayon donné.
    """
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0:
        dist_sq = (cx - x1) ** 2 + (cy - y1) ** 2
        return dist_sq <= radius ** 2
    t = ((cx - x1) * dx + (cy - y1) * dy) / (dx * dx + dy * dy)
    t = max(0, min(1, t))
    closest_x = x1 + t * dx
    closest_y = y1 + t * dy
    dist_sq = (cx - closest_x) ** 2 + (cy - closest_y) ** 2
    return dist_sq <= radius ** 2

# -------------------------
# CHARGEMENT DES IMAGES DES FRUITS, GLACONS ET BOMBS
# -------------------------
new_w, new_h = 100, 100

fruit_imgs = [
    load_and_resize_image("images/kiwi.png",   new_w, new_h),
    load_and_resize_image("images/pomme.png",  new_w, new_h),
    load_and_resize_image("images/orange.png", new_w, new_h)
]
fruit_slices = [
    [
        load_and_resize_image("images/kiwi-split1.png",  new_w, new_h),
        load_and_resize_image("images/kiwi-split2.png",  new_w, new_h)
    ],
    [
        load_and_resize_image("images/pomme-split1.png", new_w, new_h),
        load_and_resize_image("images/pomme-split2.png", new_w, new_h)
    ],
    [
        load_and_resize_image("images/orange-split1.png", new_w, new_h),
        load_and_resize_image("images/orange-split2.png", new_w, new_h)
    ]
]

ice_img  = load_and_resize_image("images/glacon.png", new_w, new_h)
bomb_img = load_and_resize_image("images/bombe.png", new_w, new_h)
bomb_slices = [
    load_and_resize_image("images/bombe-split1.png", new_w, new_h),
    load_and_resize_image("images/bombe-split2.png", new_w, new_h)
]

# -------------------------
# SYSTÈME DE SCORE ET COMBO
# -------------------------
def combo_points(n):
    """
    Renvoie le nombre de points pour n fruits tranchés en un seul coup.
    Selon l'énoncé :
      - 1 fruit : +1 point
      - 3 fruits : +2 points
      - 4 fruits : +3 points
      - Et ainsi de suite (on augmente le bonus d'1 pour chaque fruit supplémentaire au-delà de 4)
    Pour 2 fruits, nous donnons simplement 1 point (aucun bonus spécifique).
    """
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    elif n == 2:
        return 1
    elif n == 3:
        return 2
    elif n == 4:
        return 3
    else:
        return 3 + (n - 4)

# -------------------------
# CLASSE POUR LE SYSTÈME DE COMBO
# -------------------------
class ComboSystem:
    def __init__(self):
        self.current_combo = 0
        self.last_combo_time = 0
        self.display_duration = 1500  # durée d'affichage du combo en ms

    def start_combo(self, n):
        self.current_combo = n
        self.last_combo_time = pygame.time.get_ticks()
        if n > 1 and snd_combo:
            snd_combo.play()

    def update(self):
        if pygame.time.get_ticks() - self.last_combo_time > self.display_duration:
            self.current_combo = 0

    def draw(self):
        if self.current_combo > 1:
            text = f"COMBO x{self.current_combo}!"
            draw_text(text, FONT, GOLD, screen_w // 2 - 100, 220)

# -------------------------
# CLASSE DES OBJETS (FRUITS, GLACONS, BOMBS)
# -------------------------
class FruitObj:
    def __init__(self, image, slices, x, y, speed, letter=None, is_bomb=False, is_ice=False):
        self.image   = image        # image originale
        self.slices  = slices       # images après tranche
        self.x, self.y = x, y
        self.speed   = speed        # vitesse de descente
        self.letter  = letter       # lettre associée (optionnelle)
        self.is_bomb = is_bomb       # vrai si c'est une bombe
        self.is_ice  = is_ice        # vrai si c'est un glaçon
        self.sliced  = False         # état tranché ou non
        self.sliced_time = 0         # temps auquel il a été tranché
        # Décalages pour l'animation de tranche
        self.offL = -40
        self.offR = 40
        self.velL = -3
        self.velR = 3
        self.grav = 1
        self.slice_y = 0

    def draw(self):
        if not self.sliced:
            screen.blit(self.image, (self.x, self.y))
            if self.letter:
                draw_text(self.letter, FONT, WHITE, self.x + new_w // 2 - 15, self.y + new_h // 2 - 25)
        else:
            # Affichage des deux parties après tranche
            screen.blit(self.slices[0], (self.x + self.offL, self.y + self.slice_y))
            screen.blit(self.slices[1], (self.x + self.offR, self.y + self.slice_y))

    def move(self, freeze=False):
        # Si le jeu n'est pas gelé ou si l'objet est déjà tranché
        if not freeze or self.sliced:
            self.y += self.speed
        if self.sliced:
            self.offL += self.velL
            self.offR += self.velR
            self.slice_y += self.grav

    def is_clicked(self, mouse_pos):
        """Détecte si un clic (ou swipe) touche l'objet."""
        main_rect = pygame.Rect(self.x, self.y, new_w, new_h)
        if self.sliced:
            r1 = pygame.Rect(self.x + self.offL, self.y + self.slice_y, new_w, new_h)
            r2 = pygame.Rect(self.x + self.offR, self.y + self.slice_y, new_w, new_h)
            return r1.collidepoint(mouse_pos) or r2.collidepoint(mouse_pos)
        else:
            return main_rect.collidepoint(mouse_pos)

    def circle_center(self):
        """Renvoie le centre et le rayon approximatif pour la détection par cercle."""
        cx = self.x + new_w // 2
        cy = self.y + new_h // 2
        return cx, cy, (new_w // 2 + 5)

# -------------------------
# CLASSE POUR L'EFFET VISUEL DE TRANCHE (slash)
# -------------------------
class SlashFX:
    def __init__(self, x, y, big=False):
        self.x, self.y = x, y
        self.start = pygame.time.get_ticks()
        self.lifetime = 300  # durée de vie de l'effet en ms
        angle = random.randint(0, 360)
        base_img = slash_img_big if big else slash_img_small
        self.image = pygame.transform.rotate(base_img, angle)
        self.alpha = 255

    def draw(self):
        elapsed = pygame.time.get_ticks() - self.start
        # Effet de fondu
        self.alpha = max(0, 255 - (elapsed * 255 // self.lifetime))
        self.image.set_alpha(self.alpha)
        screen.blit(self.image, (self.x - self.image.get_width() // 2,
                                 self.y - self.image.get_height() // 2))

    def expired(self):
        return pygame.time.get_ticks() - self.start > self.lifetime

# -------------------------
# FONCTION DE TRANCHE D'UN OBJET
# -------------------------
def slice_object(obj, slash_effects, sound_on, big_slash=False):
    obj.sliced = True
    obj.sliced_time = pygame.time.get_ticks()
    cx = obj.x + new_w // 2
    cy = obj.y + new_h // 2
    slash_effects.append(SlashFX(cx, cy, big=big_slash))
    # Jouer le son approprié
    if sound_on:
        if obj.is_bomb and snd_bomb:
            snd_bomb.play()
        elif obj.is_ice and snd_ice:
            snd_ice.play()
        elif snd_fruit:
            snd_fruit.play()

# -------------------------
# FONCTIONS DE CRÉATION D'OBJETS (FRUITS, GLACONS, BOMBS)
# -------------------------
def create_fruit(objs):
    # Création d'un fruit à une position aléatoire avec une vitesse aléatoire
    x = random.randint(20, screen_w - new_w - 20)
    spd = random.uniform(1.5, 3.0)
    letter = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    i = random.randint(0, len(fruit_imgs) - 1)
    objs.append(FruitObj(fruit_imgs[i], fruit_slices[i], x, 0, spd, letter))

def create_ice(objs):
    x = random.randint(20, screen_w - new_w - 20)
    spd = random.uniform(1.5, 3.0)
    letter = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    objs.append(FruitObj(ice_img, [ice_img, ice_img], x, 0, spd, letter, is_ice=True))

def create_bomb(objs):
    x = random.randint(20, screen_w - new_w - 20)
    spd = random.uniform(1.5, 3.0)
    objs.append(FruitObj(bomb_img, bomb_slices, x, 0, spd, is_bomb=True))

# -------------------------
# ÉCRAN DE GAME OVER
# -------------------------
def game_over_screen(score, strikes, bombed, lang):
    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()
    duration = 3000  # durée d'affichage en ms
    while True:
        screen.blit(bg_img, (0, 0))
        if bombed:
            draw_text(LANG[lang]["bomb_over"], FONT, RED, 250, screen_h // 2 - 50)
        else:
            draw_text(LANG[lang]["strike_over"], FONT, RED, 250, screen_h // 2 - 50)
        draw_text(f"{LANG[lang]['final_score']}: {score}", FONT, WHITE, 250, screen_h // 2 + 20)
        pygame.display.flip()
        if pygame.time.get_ticks() - start_time > duration:
            break
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        clock.tick(60)

# -------------------------
# MENU DE PAUSE
# -------------------------
def pause_menu(lang):
    clock = pygame.time.Clock()
    while True:
        # Création d'un overlay semi-transparent pour la pause
        overlay = pygame.Surface((screen_w, screen_h))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        draw_text(LANG[lang]["pause_menu"], FONT, RED, screen_w // 2 - 100, 150)

        data = [("resume", 300), ("main_menu", 400), ("quit", 500)]
        btn_rect = {}
        for key, ypos in data:
            bw, bh = 200, 50
            bx = screen_w // 2 - bw // 2
            rect = pygame.Rect(bx, ypos, bw, bh)
            pygame.draw.rect(screen, BLACK, rect)
            label = LANG[lang].get(key, LANG[lang]["quit"])
            txt = SMALL_FONT.render(label, True, GREEN)
            txt_rect = txt.get_rect(center=rect.center)
            screen.blit(txt, txt_rect)
            btn_rect[key] = rect

        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit"
            elif e.type == pygame.MOUSEBUTTONDOWN:
                mp = e.pos
                if btn_rect["resume"].collidepoint(mp):
                    return "resume"
                elif btn_rect["main_menu"].collidepoint(mp):
                    return "menu"
                elif btn_rect["quit"].collidepoint(mp):
                    return "quit"
        clock.tick(60)

# -------------------------
# BOUCLE PRINCIPALE DU JEU
# -------------------------
def game_loop(lang, difficulty):
    # Passage de la musique du menu à la musique du jeu
    pygame.mixer.music.fadeout(500)
    pygame.time.wait(300)
    pygame.mixer.music.load(GAME_MUSIC)
    pygame.mixer.music.play(-1)

    clock = pygame.time.Clock()
    objs = []         # liste des objets (fruits, glaçons, bombes)
    slash_fx = []     # effets visuels de tranche
    score = 0
    strikes = 0     # nombre d'échecs (fruits manqués)

    # Système de combo
    combo_system = ComboSystem()

    # -------------------------
    # PARAMÈTRES DE DIFFICULTÉ
    # -------------------------
    if difficulty == "easy":
        fruit_int, bomb_int, ice_int = (1500, 20000, 10000)  # intervalle en ms
        freeze_duration = 5000  # gel du jeu en ms
    elif difficulty == "hard":
        fruit_int, bomb_int, ice_int = (200, 6000, 13000)
        freeze_duration = 3000
    else:  # normal
        fruit_int, bomb_int, ice_int = (1200, 15000, 8000)
        freeze_duration = 4000

    fruit_t, bomb_t, ice_t = 0, 0, 0
    freeze = False
    freeze_start = 0

    # Délai pour afficher l'animation de bombe tranchée
    bomb_sliced = False
    bomb_sliced_time = 0
    BOMB_DELAY = 700

    # Paramètres audio
    music_on = True
    sound_on = True
    def update_sound():
        vol = 1.0 if sound_on else 0.0
        if snd_fruit: snd_fruit.set_volume(vol)
        if snd_ice: snd_ice.set_volume(vol)
        if snd_bomb: snd_bomb.set_volume(vol)
        if snd_combo: snd_combo.set_volume(vol)
    update_sound()

    # Pour la détection du swipe (drag slicing)
    mouse_down = False
    old_mouse_pos = None

    running = True
    while running:
        screen.blit(bg_img, (0, 0))
        now = pygame.time.get_ticks()

        if bomb_sliced:
            # Si une bombe a été tranchée, on affiche son animation avant de terminer la partie
            if now - bomb_sliced_time >= BOMB_DELAY:
                game_over_screen(score, strikes, True, lang)
                running = False
        else:
            newly_sliced = []  # objets tranchés pendant cette frame

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif e.type == pygame.MOUSEBUTTONDOWN:
                    mp = e.pos
                    # Bouton de pause
                    pause_rect = pygame.Rect(10, 10, 100, 40)
                    if pause_rect.collidepoint(mp):
                        choice = pause_menu(lang)
                        if choice == "resume":
                            pass
                        elif choice == "menu":
                            running = False
                        elif choice == "quit":
                            pygame.quit()
                            sys.exit()
                    else:
                        # Boutons de musique et son
                        music_btn = pygame.Rect(screen_w - 100, 10, 40, 40)
                        sound_btn = pygame.Rect(screen_w - 50, 10, 40, 40)
                        if music_btn.collidepoint(mp):
                            music_on = not music_on
                            pygame.mixer.music.set_volume(1.0 if music_on else 0.0)
                        elif sound_btn.collidepoint(mp):
                            sound_on = not sound_on
                            update_sound()
                        else:
                            # Début d'un swipe
                            mouse_down = True
                            old_mouse_pos = mp
                            # Vérifier également un simple clic
                            for obj in objs:
                                if not obj.sliced and obj.is_clicked(mp):
                                    slice_object(obj, slash_fx, sound_on, big_slash=False)
                                    newly_sliced.append(obj)
                                    if obj.is_bomb:
                                        bomb_sliced = True
                                        bomb_sliced_time = now
                                    elif obj.is_ice:
                                        freeze = True
                                        freeze_start = now
                elif e.type == pygame.MOUSEBUTTONUP:
                    mouse_down = False
                    old_mouse_pos = None
                elif e.type == pygame.MOUSEMOTION:
                    if mouse_down and old_mouse_pos:
                        x1, y1 = old_mouse_pos
                        x2, y2 = e.pos
                        # Vérification d'intersection entre le swipe et les fruits
                        for obj in objs:
                            if not obj.sliced:
                                cx, cy, r = obj.circle_center()
                                if line_circle_intersect(x1, y1, x2, y2, cx, cy, r):
                                    slice_object(obj, slash_fx, sound_on, big_slash=True)
                                    newly_sliced.append(obj)
                                    if obj.is_bomb:
                                        bomb_sliced = True
                                        bomb_sliced_time = now
                                    elif obj.is_ice:
                                        freeze = True
                                        freeze_start = now
                        old_mouse_pos = e.pos
                elif e.type == pygame.KEYDOWN:
                    # Permettre la tranche via la touche associée
                    kp = pygame.key.name(e.key).upper()
                    for obj in objs:
                        if not obj.sliced and obj.letter == kp:
                            slice_object(obj, slash_fx, sound_on, big_slash=False)
                            newly_sliced.append(obj)
                            if obj.is_bomb:
                                bomb_sliced = True
                                bomb_sliced_time = now
                            elif obj.is_ice:
                                freeze = True
                                freeze_start = now

            # Calcul du combo pour les fruits normaux
            normal_fruits = [o for o in newly_sliced if not o.is_bomb and not o.is_ice]
            n = len(normal_fruits)
            if n > 0:
                combo_system.start_combo(n)
                score += combo_points(n)

        # Gestion du gel (quand un glaçon est tranché)
        if freeze and (now - freeze_start >= freeze_duration):
            freeze = False

        # SPAWN DES OBJETS SI LE JEU N'EST PAS GELÉ ET PAS FINI PAR UNE BOMBE
        if not freeze and not bomb_sliced:
            if now - fruit_t > fruit_int:
                create_fruit(objs)
                fruit_t = now
            if now - bomb_t > bomb_int:
                create_bomb(objs)
                bomb_t = now
            if now - ice_t > ice_int:
                create_ice(objs)
                ice_t = now

        # Affichage des boutons de pause, musique et son
        pause_btn = pygame.Rect(10, 10, 100, 40)
        pygame.draw.rect(screen, (128, 128, 128), pause_btn)
        draw_text("Pause", SMALL_FONT, WHITE, pause_btn.x + 10, pause_btn.y + 5)

        music_btn = pygame.Rect(screen_w - 100, 10, 40, 40)
        sound_btn = pygame.Rect(screen_w - 50, 10, 40, 40)
        pygame.draw.rect(screen, (128, 128, 128), music_btn)
        pygame.draw.rect(screen, (128, 128, 128), sound_btn)
        draw_text("M", SMALL_FONT, WHITE, music_btn.x + 10, music_btn.y + 5)
        draw_text("S", SMALL_FONT, WHITE, sound_btn.x + 10, sound_btn.y + 5)

        # Mise à jour et affichage des objets
        to_remove = []
        for obj in objs:
            obj.move(freeze)
            obj.draw()
            # Si un fruit est manqué (et n'est ni glaçon ni bombe), on ajoute une strike
            if obj.y > screen_h and not obj.sliced and not obj.is_bomb and not obj.is_ice:
                strikes += 1
                to_remove.append(obj)
            # Suppression des objets tranchés après environ 1 seconde
            if obj.sliced and (now - obj.sliced_time > 1000):
                to_remove.append(obj)
        for r in to_remove:
            if r in objs:
                objs.remove(r)

        # Affichage et suppression des effets de slash
        expired_fx = []
        for fx in slash_fx:
            if fx.expired():
                expired_fx.append(fx)
            else:
                fx.draw()
        for efx in expired_fx:
            slash_fx.remove(efx)

        # Mise à jour et affichage du système de combo
        combo_system.update()
        combo_system.draw()

        # Fin de partie après 3 strikes
        if not bomb_sliced and strikes >= 3:
            game_over_screen(score, strikes, False, lang)
            running = False

        # Affichage de l'HUD (score et vies)
        draw_text(f"{LANG[lang]['score']}: {score}", FONT, WHITE, 10, 60)
        hearts_left = 3 - strikes
        for i in range(hearts_left):
            screen.blit(heart_icon, (10 + i * (heart_icon.get_width() + 5), 120))

        pygame.display.flip()
        clock.tick(60)

    # À la fin de la partie, repasser à la musique du menu
    pygame.mixer.music.fadeout(500)
    pygame.time.wait(300)
    pygame.mixer.music.load(MENU_MUSIC)
    pygame.mixer.music.play(-1)

# -------------------------
# MENUS : CHOIX DE LANGUE, DIFFICULTÉ, ET MENU PRINCIPAL
# -------------------------
def choose_language(current_lang):
    """Menu pour choisir la langue."""
    clock = pygame.time.Clock()
    while True:
        screen.blit(bg_img, (0, 0))
        draw_text("Choisir la Langue / Choose Language", FONT, RED, 300, 100)
        data = [
            ("English", "en", 300),
            ("Français", "fr", 400),
            (LANG[current_lang]["back"], None, 500)
        ]
        rects = {}
        for label, val, y in data:
            bw, bh = 200, 50
            bx = screen_w // 2 - bw // 2
            r = pygame.Rect(bx, y, bw, bh)
            pygame.draw.rect(screen, BLACK, r)
            t = SMALL_FONT.render(label, True, GREEN)
            t_rect = t.get_rect(center=r.center)
            screen.blit(t, t_rect)
            rects[val] = r
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif e.type == pygame.MOUSEBUTTONDOWN:
                mp = e.pos
                for v, rct in rects.items():
                    if rct.collidepoint(mp):
                        if v is None:
                            return current_lang
                        else:
                            return v
        clock.tick(60)

# -------------------------
# FONCTION CHOISIR LA DIFFICULTÉ (VERSION AMÉLIORÉE)
# -------------------------
def choose_difficulty(lang, curr_diff):
    """Menu pour choisir la difficulté (options désormais centrées)."""
    clock = pygame.time.Clock()
    while True:
        screen.blit(bg_img, (0, 0))
        # Afficher le titre "Difficulté" centré
        diff_text = FONT.render(LANG[lang]["diff"], True, RED)
        diff_rect = diff_text.get_rect(center=(screen_w // 2, 100))
        screen.blit(diff_text, diff_rect)
        # Options de difficulté avec espacement vertical fixe
        options = [("easy", LANG[lang]["easy"]),
                   ("normal", LANG[lang]["normal"]),
                   ("hard", LANG[lang]["hard"]),
                   ("back", LANG[lang]["back"])]
        start_y = 250  # position verticale de départ
        spacing = 100  # espacement entre les options
        rects = {}
        for i, (key, label) in enumerate(options):
            bw, bh = 200, 50
            bx = screen_w // 2 - bw // 2
            y = start_y + i * spacing
            rect = pygame.Rect(bx, y, bw, bh)
            pygame.draw.rect(screen, BLACK, rect)
            text = SMALL_FONT.render(label, True, GREEN)
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)
            rects[key] = rect
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif e.type == pygame.MOUSEBUTTONDOWN:
                pos = e.pos
                for key, rect in rects.items():
                    if rect.collidepoint(pos):
                        if key == "back":
                            return curr_diff
                        else:
                            return key
        clock.tick(60)

def main_menu(lang, diff):
    """Menu principal du jeu."""
    clock = pygame.time.Clock()
    while True:
        screen.blit(bg_img, (0, 0))
        title = LANG[lang]["menu_title"]
        ts = FONT.render(title, True, BROWN)
        tr = ts.get_rect(center=(screen_w // 2, 100))
        screen.blit(ts, tr)

        diff_label = LANG[lang]["diff"] + ": " + LANG[lang][diff]
        ds = SMALL_FONT.render(diff_label, True, RED)
        dr = ds.get_rect(center=(screen_w // 2, 170))
        screen.blit(ds, dr)

        data = [("play", 220), ("lang", 320), ("diff", 420), ("quit", 520)]
        rects = {}
        for k, y in data:
            bw, bh = 200, 50
            bx = screen_w // 2 - bw // 2
            r = pygame.Rect(bx, y, bw, bh)
            pygame.draw.rect(screen, BLACK, r)
            txt_str = LANG[lang][k]
            t = SMALL_FONT.render(txt_str, True, GREEN)
            t_rect = t.get_rect(center=r.center)
            screen.blit(t, t_rect)
            rects[k] = r
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit"
            elif e.type == pygame.MOUSEBUTTONDOWN:
                mp = e.pos
                for key in rects:
                    if rects[key].collidepoint(mp):
                        return key
        clock.tick(60)

def main():
    # Démarrer avec la musique du menu
    pygame.mixer.music.load(MENU_MUSIC)
    pygame.mixer.music.play(-1)

    current_lang = "fr"
    current_diff = "normal"

    while True:
        choice = main_menu(current_lang, current_diff)
        if choice == "quit":
            pygame.quit()
            sys.exit()
        elif choice == "lang":
            current_lang = choose_language(current_lang)
        elif choice == "diff":
            current_diff = choose_difficulty(current_lang, current_diff)
        elif choice == "play":
            game_loop(current_lang, current_diff)

if __name__ == "__main__":
    main()
