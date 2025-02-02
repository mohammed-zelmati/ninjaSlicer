import pygame

class MainMenu:
    def __init__(self, game):
        self.game = game

    def show(self):
        clock = pygame.time.Clock()
        while True:
            self.game.screen.blit(self.game.bg_img, (0, 0))
            title = self.game.LANG[self.game.current_lang]["menu_title"]
            ts = self.game.FONT.render(title, True, self.game.BROWN)
            tr = ts.get_rect(center=(self.game.screen_w // 2, 100))
            self.game.screen.blit(ts, tr)

            diff_label = self.game.LANG[self.game.current_lang]["diff"] + ": " + self.game.LANG[self.game.current_lang][self.game.current_diff]
            ds = self.game.SMALL_FONT.render(diff_label, True, self.game.RED)
            dr = ds.get_rect(center=(self.game.screen_w // 2, 170))
            self.game.screen.blit(ds, dr)

            data = [("play", 220), ("lang", 320), ("diff", 420), ("quit", 520)]
            rects = {}
            for k, y in data:
                bw, bh = 200, 50
                bx = self.game.screen_w // 2 - bw // 2
                r = pygame.Rect(bx, y, bw, bh)
                pygame.draw.rect(self.game.screen, self.game.BLACK, r)
                txt_str = self.game.LANG[self.game.current_lang][k]
                t = self.game.SMALL_FONT.render(txt_str, True, self.game.GREEN)
                t_rect = t.get_rect(center=r.center)
                self.game.screen.blit(t, t_rect)
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

class ChooseLanguage:
    def __init__(self, game):
        self.game = game

    def show(self):
        clock = pygame.time.Clock()
        while True:
            self.game.screen.blit(self.game.bg_img, (0, 0))
            self.game.draw_text("Choisir la Langue / Choose Language", self.game.FONT, self.game.RED, 300, 100)
            data = [
                ("English", "en", 300),
                ("Français", "fr", 400),
                (self.game.LANG[self.game.current_lang]["back"], None, 500)
            ]
            rects = {}
            for label, val, y in data:
                bw, bh = 200, 50
                bx = self.game.screen_w // 2 - bw // 2
                r = pygame.Rect(bx, y, bw, bh)
                pygame.draw.rect(self.game.screen, self.game.BLACK, r)
                t = self.game.SMALL_FONT.render(label, True, self.game.GREEN)
                t_rect = t.get_rect(center=r.center)
                self.game.screen.blit(t, t_rect)
                rects[val] = r
            pygame.display.flip()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    return self.game.current_lang
                elif e.type == pygame.MOUSEBUTTONDOWN:
                    mp = e.pos
                    for v, rct in rects.items():
                        if rct.collidepoint(mp):
                            if v is None:
                                return self.game.current_lang
                            else:
                                return v
            clock.tick(60)

class ChooseDifficulty:
    def __init__(self, game):
        self.game = game

    def show(self):
        clock = pygame.time.Clock()
        while True:
            self.game.screen.blit(self.game.bg_img, (0, 0))
            self.game.draw_text(self.game.LANG[self.game.current_lang]["diff"], self.game.FONT, self.game.RED, self.game.screen_w // 2 - 50, 100)
            data = [
                ("easy", self.game.LANG[self.game.current_lang]["easy"], 300),
                ("normal", self.game.LANG[self.game.current_lang]["normal"], 400),
                ("hard", self.game.LANG[self.game.current_lang]["hard"], 500),
                ("back", self.game.LANG[self.game.current_lang]["back"], 600)
            ]
            rects = {}
            for diff_key, label, y in data:
                bw, bh = 200, 50
                bx = self.game.screen_w // 2 - bw // 2
                r = pygame.Rect(bx, y, bw, bh)
                pygame.draw.rect(self.game.screen, self.game.BLACK, r)
                txt = self.game.SMALL_FONT.render(label, True, self.game.GREEN)
                txt_rect = txt.get_rect(center=r.center)
                self.game.screen.blit(txt, txt_rect)
                rects[diff_key] = r
            pygame.display.flip()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    return self.game.current_diff
                elif e.type == pygame.MOUSEBUTTONDOWN:
                    mp = e.pos
                    for k, rct in rects.items():
                        if rct.collidepoint(mp):
                            if k == "back":
                                return self.game.current_diff
                            else:
                                return k
            clock.tick(60)