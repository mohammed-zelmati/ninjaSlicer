import pygame
import random
from models.comboSystem import ComboSystem
from models.slashFX import SlashFX
from models.fruitObj import FruitObj
from models.menu import MainMenu, ChooseLanguage, ChooseDifficulty

class Game:
    def __init__(self):
        pygame.init()
        self.screen_w, self.screen_h = 1280, 720
        self.screen = pygame.display.set_mode((self.screen_w, self.screen_h))
        pygame.display.set_caption("FRUIT SLICER GAME")
        self.bg_img = pygame.image.load("images/fruit.jpg")
        self.bg_img = pygame.transform.scale(self.bg_img, (self.screen_w, self.screen_h))
        self.FONT = pygame.font.SysFont('Roboto', 50)
        self.SMALL_FONT = pygame.font.SysFont('Roboto', 25)
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BROWN = (165, 42, 42)
        self.GOLD = (255, 215, 0)
        self.snd_fruit = pygame.mixer.Sound("son/tranche_fruit.mp3")
        self.snd_ice = pygame.mixer.Sound("son/tranche_glacon.mp3")
        self.snd_bomb = pygame.mixer.Sound("son/tranche_bombe.mp3")
        self.snd_combo = pygame.mixer.Sound("son/combo.mp3")
        self.MENU_MUSIC = "son/ambiance.mp3"
        self.GAME_MUSIC = "son/musique_ambiance.mp3"
        self.LANG = {
            "en": {
                "menu_title": "Game Menu", "play": "Play", "lang": "Language", "diff": "Difficulty", "quit": "Quit",
                "score": "Score", "bomb_over": "You hit a bomb! GAME OVER", "strike_over": "You reached 3 strikes! GAME OVER",
                "final_score": "Final Score", "lives": "Lives", "easy": "Easy", "normal": "Normal", "hard": "Hard",
                "back": "Back", "resume": "Resume", "pause_menu": "Game Paused", "main_menu": "Main Menu"
            },
            "fr": {
                "menu_title": "Menu du jeu", "play": "Jouer", "lang": "Langue", "diff": "Difficulté", "quit": "Quitter",
                "score": "Score", "bomb_over": "Vous avez frappé une bombe! GAME OVER", "strike_over": "Vous avez atteint 3 strikes! GAME OVER",
                "final_score": "Score Final", "lives": "Vies", "easy": "Facile", "normal": "Moyen", "hard": "Difficile",
                "back": "Retour", "resume": "Continuer", "pause_menu": "Jeu en pause", "main_menu": "Menu principal"
            }
        }
        self.current_lang = "fr"
        self.current_diff = "normal"
        self.main_menu = MainMenu(self)
        self.choose_language = ChooseLanguage(self)
        self.choose_difficulty = ChooseDifficulty(self)

         # Initialisation des images
        self.fruit_imgs = [
            self.load_and_resize_image("images/kiwi.png", 100, 100),
            self.load_and_resize_image("images/pomme.png", 100, 100),
            self.load_and_resize_image("images/orange.png", 100, 100)
        ]
        self.fruit_slices = [
            [
                self.load_and_resize_image("images/kiwi-split1.png", 100, 100),
                self.load_and_resize_image("images/kiwi-split2.png", 100, 100)
            ],
            [
                self.load_and_resize_image("images/pomme-split1.png", 100, 100),
                self.load_and_resize_image("images/pomme-split2.png", 100, 100)
            ],
            [
                self.load_and_resize_image("images/orange-split1.png", 100, 100),
                self.load_and_resize_image("images/orange-split2.png", 100, 100)
            ]
        ]
        self.ice_img = self.load_and_resize_image("images/glacon.png", 100, 100)
        self.bomb_img = self.load_and_resize_image("images/bombe.png", 100, 100)
        self.bomb_slices = [
            self.load_and_resize_image("images/bombe-split1.png", 100, 100),
            self.load_and_resize_image("images/bombe-split2.png", 100, 100)
        ]
        self.heart_icon = self.load_and_resize_image("images/red_lives.png", 40, 40)
        self.slash_img_small = self.load_and_resize_image("images/slash.png", 120, 120)
        self.slash_img_big = self.load_and_resize_image("images/slash.png", 200, 200)

    def draw_text(self, text, font, color, x, y):
        surf = font.render(text, True, color)
        self.screen.blit(surf, (x, y))

    def load_and_resize_image(self, path, w, h):
        img = pygame.image.load(path)
        return pygame.transform.scale(img, (w, h))

    def line_circle_intersect(self, x1, y1, x2, y2, cx, cy, radius):
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

    def combo_points(self, n):
        if n <= 0: return 0
        if n == 1: return 1
        elif n == 2: return 5
        elif n == 3: return 20
        elif n == 4: return 30
        else: return 50

    def slice_object(self, obj, slash_effects, sound_on, big_slash=False):
        obj.sliced = True
        obj.sliced_time = pygame.time.get_ticks()
        cx = obj.x + 100 // 2
        cy = obj.y + 100 // 2
        slash_effects.append(SlashFX(cx, cy, big=big_slash))
        if sound_on:
            if obj.is_bomb: self.snd_bomb.play()
            elif obj.is_ice: self.snd_ice.play()
            else: self.snd_fruit.play()

    def create_fruit(self, objs):
        x = random.randint(20, self.screen_w - 100 - 20)
        spd = random.uniform(1.0, 2.0)
        letter = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        i = random.randint(0, len(self.fruit_imgs) - 1)
        objs.append(FruitObj(self.fruit_imgs[i], self.fruit_slices[i], x, 0, spd, letter))

    def create_ice(self, objs):
        x = random.randint(20, self.screen_w - 100 - 20)
        spd = random.uniform(1.0, 2.0)
        letter = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        objs.append(FruitObj(self.ice_img, [self.ice_img, self.ice_img], x, 0, spd, letter, is_ice=True))

    def create_bomb(self, objs):
        x = random.randint(20, self.screen_w - 100 - 20)
        spd = random.uniform(1.0, 2.0)
        objs.append(FruitObj(self.bomb_img, self.bomb_slices, x, 0, spd, is_bomb=True))

    def game_over_screen(self, score, strikes, bombed, lang):
        clock = pygame.time.Clock()
        st = pygame.time.get_ticks()
        dur = 3000
        while True:
            self.screen.blit(self.bg_img, (0, 0))
            if bombed:
                self.draw_text(self.LANG[lang]["bomb_over"], self.FONT, self.RED, 250, self.screen_h // 2 - 50)
            else:
                self.draw_text(self.LANG[lang]["strike_over"], self.FONT, self.RED, 250, self.screen_h // 2 - 50)
            self.draw_text(f"{self.LANG[lang]['final_score']}: {score}", self.FONT, self.WHITE, 250, self.screen_h // 2 + 20)
            pygame.display.flip()
            if pygame.time.get_ticks() - st > dur: break
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    return
            clock.tick(60)
        return

    def pause_menu(self, lang):
        clock = pygame.time.Clock()
        while True:
            overlay = pygame.Surface((self.screen_w, self.screen_h))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))

            self.draw_text(self.LANG[lang]["pause_menu"], self.FONT, self.RED, self.screen_w // 2 - 100, 150)

            data = [("resume", 300), ("main_menu", 400), ("quit", 500)]
            btn_rect = {}
            for key, ypos in data:
                bw, bh = 200, 50
                bx = self.screen_w // 2 - bw // 2
                rect = pygame.Rect(bx, ypos, bw, bh)
                pygame.draw.rect(self.screen, self.BLACK, rect)
                label = self.LANG[lang].get(key, self.LANG[lang]["quit"])
                txt = self.SMALL_FONT.render(label, True, self.GREEN)
                txt_rect = txt.get_rect(center=rect.center)
                self.screen.blit(txt, txt_rect)
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

    def game_loop(self, lang, difficulty):
        # Fade out menu music & start game music
        pygame.mixer.music.fadeout(500)
        pygame.time.wait(300)
        pygame.mixer.music.load(self.GAME_MUSIC)
        pygame.mixer.music.play(-1)

        clock = pygame.time.Clock()
        objs = []
        slash_fx = []
        score = 0
        strikes = 0

        # COMBO system
        combo_system = ComboSystem(self.FONT, self.GOLD)  # Passer self.FONT et self.GOLD

        # Difficulty -> spawn intervals & freeze times
        if difficulty == "easy":
            fruit_int, bomb_int, ice_int = (1500, 20000, 10000)
            freeze_duration = 5000
        elif difficulty == "hard":
            fruit_int, bomb_int, ice_int = (200, 6000, 13000)
            freeze_duration = 3000
        else:  # normal
            fruit_int, bomb_int, ice_int = (1200, 15000, 8000)
            freeze_duration = 4000

        fruit_t, bomb_t, ice_t = 0, 0, 0
        freeze = False
        freeze_start = 0

        # bomb slicing short delay
        bomb_sliced = False
        bomb_sliced_time = 0
        BOMB_DELAY = 700

        music_on = True
        sound_on = True

        def update_sound():
            vol = 1.0 if sound_on else 0.0
            self.snd_fruit.set_volume(vol)
            self.snd_ice.set_volume(vol)
            self.snd_bomb.set_volume(vol)
            self.snd_combo.set_volume(vol)

        update_sound()

        # For drag slicing
        mouse_down = False
        old_mouse_pos = None

        running = True
        while running:
            self.screen.blit(self.bg_img, (0, 0))
            now = pygame.time.get_ticks()

            if bomb_sliced:
                # show splitted bomb for ~700ms
                if now - bomb_sliced_time >= BOMB_DELAY:
                    self.game_over_screen(score, strikes, True, lang)
                    running = False
            else:
                newly_sliced = []  # gather all objects sliced this frame

                for e in pygame.event.get():
                    if e.type == pygame.QUIT:
                        running = False
                    elif e.type == pygame.MOUSEBUTTONDOWN:
                        mp = e.pos
                        # Check pause/music toggles
                        pause_rect = pygame.Rect(10, 10, 100, 40)
                        if pause_rect.collidepoint(mp):
                            choice = self.pause_menu(lang)
                            if choice == "resume":
                                pass
                            elif choice == "menu":
                                running = False
                            elif choice == "quit":
                                pygame.quit()
                                return
                        else:
                            music_btn = pygame.Rect(self.screen_w - 100, 10, 40, 40)
                            sound_btn = pygame.Rect(self.screen_w - 50, 10, 40, 40)
                            if music_btn.collidepoint(mp):
                                music_on = not music_on
                                pygame.mixer.music.set_volume(1.0 if music_on else 0.0)
                            elif sound_btn.collidepoint(mp):
                                sound_on = not sound_on
                                update_sound()
                            else:
                                # Start a drag
                                mouse_down = True
                                old_mouse_pos = mp
                                # Also check single-click bounding box
                                for obj in objs:
                                    if not obj.sliced and obj.is_clicked(mp):
                                        self.slice_object(obj, slash_fx, sound_on, big_slash=False)
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
                            # line vs circle
                            for obj in objs:
                                if not obj.sliced:
                                    cx, cy, r = obj.circle_center()
                                    if self.line_circle_intersect(x1, y1, x2, y2, cx, cy, r):
                                        self.slice_object(obj, slash_fx, sound_on, big_slash=True)
                                        newly_sliced.append(obj)
                                        if obj.is_bomb:
                                            bomb_sliced = True
                                            bomb_sliced_time = now
                                        elif obj.is_ice:
                                            freeze = True
                                            freeze_start = now
                            old_mouse_pos = e.pos
                    elif e.type == pygame.KEYDOWN:
                        kp = pygame.key.name(e.key).upper()
                        for obj in objs:
                            if not obj.sliced and obj.letter == kp:
                                self.slice_object(obj, slash_fx, sound_on, big_slash=False)
                                newly_sliced.append(obj)
                                if obj.is_bomb:
                                    bomb_sliced = True
                                    bomb_sliced_time = now
                                elif obj.is_ice:
                                    freeze = True
                                    freeze_start = now

                # compute combos for normal fruits
                normal_fruits = [o for o in newly_sliced if not o.is_bomb and not o.is_ice]
                n = len(normal_fruits)
                if n > 0:
                    combo_system.start_combo(n)
                    score += self.combo_points(n)

            # freeze logic
            if freeze and (now - freeze_start >= freeze_duration):
                freeze = False

            # spawn if not freeze/bomb
            if not freeze and not bomb_sliced:
                if now - fruit_t > fruit_int:
                    self.create_fruit(objs)
                    fruit_t = now
                if now - bomb_t > bomb_int:
                    self.create_bomb(objs)
                    bomb_t = now
                if now - ice_t > ice_int:
                    self.create_ice(objs)
                    ice_t = now

            # pause/music/sound
            pause_btn = pygame.Rect(10, 10, 100, 40)
            pygame.draw.rect(self.screen, (128, 128, 128), pause_btn)
            self.draw_text("Pause", self.SMALL_FONT, self.WHITE, pause_btn.x + 10, pause_btn.y + 5)

            music_btn = pygame.Rect(self.screen_w - 100, 10, 40, 40)
            sound_btn = pygame.Rect(self.screen_w - 50, 10, 40, 40)
            pygame.draw.rect(self.screen, (128, 128, 128), music_btn)
            pygame.draw.rect(self.screen, (128, 128, 128), sound_btn)
            self.draw_text("M", self.SMALL_FONT, self.WHITE, music_btn.x + 10, music_btn.y + 5)
            self.draw_text("S", self.SMALL_FONT, self.WHITE, sound_btn.x + 10, sound_btn.y + 5)

            # update / draw objects
            to_remove = []
            for obj in objs:
                obj.move(freeze)
                obj.draw(self.screen, self.SMALL_FONT)  # Passer la police pour dessiner la lettre
                # missed => strike (not ice/bomb)
                if obj.y > self.screen_h and not obj.sliced and (not obj.is_bomb) and (not obj.is_ice):
                    strikes += 1
                    to_remove.append(obj)
                # remove sliced after ~1s
                if obj.sliced and (now - obj.sliced_time > 1000):
                    to_remove.append(obj)
            for r in to_remove:
                if r in objs: objs.remove(r)

            # slash effects
            expired_fx = []
            for fx in slash_fx:
                if fx.expired(): expired_fx.append(fx)
                else: fx.draw(self.screen)
            for efx in expired_fx:
                slash_fx.remove(efx)

            # combo system update/draw
            combo_system.update()
            combo_system.draw(self.screen)

            # 3 strikes => game over
            if not bomb_sliced and strikes >= 3:
                self.game_over_screen(score, strikes, False, lang)
                running = False

            # HUD
            self.draw_text(f"{self.LANG[lang]['score']}: {score}", self.FONT, self.WHITE, 10, 60)
            hearts_left = 3 - strikes
            for i in range(hearts_left):
                self.screen.blit(self.heart_icon, (10 + i * (self.heart_icon.get_width() + 5), 120))

            pygame.display.flip()
            clock.tick(60)

        # cleanup
        pygame.mixer.music.fadeout(500)
        pygame.time.wait(300)
        pygame.mixer.music.load(self.MENU_MUSIC)
        pygame.mixer.music.play(-1)
        
    def main(self):
        pygame.mixer.music.load(self.MENU_MUSIC)
        pygame.mixer.music.play(-1)

        while True:
            choice = self.main_menu.show()
            if choice == "quit":
                pygame.quit()
                break
            elif choice == "lang":
                self.current_lang = self.choose_language.show()
            elif choice == "diff":
                self.current_diff = self.choose_difficulty.show()
            elif choice == "play":
                self.game_loop(self.current_lang, self.current_diff)

if __name__ == "__main__":
    game = Game()
    game.main()