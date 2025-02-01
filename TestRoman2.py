import pygame
import random
import math

pygame.init()

# === Window Setup ===
screen_w, screen_h = 1280, 720
screen = pygame.display.set_mode((screen_w, screen_h))
pygame.display.set_caption("FRUIT SLICER GAME")

# === Background ===
bg_img = pygame.image.load("images/fruit.jpg")
bg_img = pygame.transform.scale(bg_img, (screen_w, screen_h))

# === Fonts & Colors ===
FONT       = pygame.font.SysFont('Roboto', 50)
SMALL_FONT = pygame.font.SysFont('Roboto', 25)
WHITE=(255,255,255); BLACK=(0,0,0); RED=(255,0,0); GREEN=(0,255,0); BROWN=(165,42,42)

# === Sounds ===
snd_fruit  = pygame.mixer.Sound("son/tranche_fruit.mp3")
snd_ice    = pygame.mixer.Sound("son/tranche_glacon.mp3")
snd_bomb   = pygame.mixer.Sound("son/tranche_bombe.mp3")

# === Music (Menu vs In-game) ===
MENU_MUSIC="son/ambiance.mp3"
GAME_MUSIC="son/musique_ambiance.mp3"

# === Language Strings ===
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
        "bomb_over":    "Vous avez frappé une bombe! GAME OVER",
        "strike_over":  "Vous avez atteint 3 strikes! GAME OVER",
        "final_score":  "Score Final",
        "lives":        "Vies",
        "easy":         "Facile",
        "normal":       "Moyen",
        "hard":         "Difficile",
        "back":         "Retour",
        "resume":       "Continuer",
        "pause_menu":   "Jeu en pause",
        "main_menu":    "Menu principal"
    }
}

def draw_text(text, font, color, x, y):
    surf = font.render(text, True, color)
    screen.blit(surf, (x, y))

def load_and_resize_image(path, w, h):
    img = pygame.image.load(path)
    return pygame.transform.scale(img, (w, h))

# === We prepare two slash images: normal & large for big swipes ===
slash_img_small = load_and_resize_image("images/slash.png", 120, 120)
slash_img_big   = load_and_resize_image("images/slash.png", 200, 200)  # bigger slash

heart_icon      = load_and_resize_image("images/red_lives.png", 40, 40)

# === Helper: line vs circle intersection (to detect slicing by drag) ===
def line_circle_intersect(x1,y1, x2,y2, cx,cy, radius):
    """Return True if the line segment (x1,y1)->(x2,y2) intersects circle (cx,cy,radius)."""
    dx = x2 - x1
    dy = y2 - y1

    # If line is effectively a point, just check distance to circle center
    if dx == 0 and dy == 0:
        dist_sq = (cx - x1)**2 + (cy - y1)**2
        return dist_sq <= radius**2

    # param "t" for projection from 0..1 along the segment
    t = ((cx - x1)*dx + (cy - y1)*dy) / float(dx*dx + dy*dy)
    if t < 0:   t=0
    elif t>1:   t=1

    # closest point on line
    closest_x = x1 + t*dx
    closest_y = y1 + t*dy
    dist_sq   = (cx - closest_x)**2 + (cy - closest_y)**2
    return dist_sq <= radius**2

# === FRUIT/ICE/BOMB images + slices ===
new_w,new_h = 100,100

fruit_imgs = [
    load_and_resize_image("images/kiwi.png",   new_w,new_h),
    load_and_resize_image("images/pomme.png",  new_w,new_h),
    load_and_resize_image("images/orange.png", new_w,new_h)
]
fruit_slices = [
    [
        load_and_resize_image("images/kiwi-split1.png",  new_w,new_h),
        load_and_resize_image("images/kiwi-split2.png",  new_w,new_h)
    ],
    [
        load_and_resize_image("images/pomme-split1.png", new_w,new_h),
        load_and_resize_image("images/pomme-split2.png", new_w,new_h)
    ],
    [
        load_and_resize_image("images/orange-split1.png",new_w,new_h),
        load_and_resize_image("images/orange-split2.png",new_w,new_h)
    ]
]

ice_img = load_and_resize_image("images/glacon.png", new_w, new_h)
bomb_img = load_and_resize_image("images/bombe.png", new_w, new_h)
bomb_slices = [
    load_and_resize_image("images/bombe-split1.png", new_w,new_h),
    load_and_resize_image("images/bombe-split2.png", new_w,new_h)
]

# === COMBO SCORING: e.g. if you slice multiple normal fruits in one action. ===
def combo_points(n):
    """
    Return how many points to award if n normal fruits are sliced in a single action.
    For example:
      n=1 => +1
      n=2 => +5
      n=3 => +20
      n=4 => +30
      n>=5 => +50
    Tweak these as you see fit.
    """
    if n<=0: return 0
    if n==1: return 1
    elif n==2: return 5
    elif n==3: return 20
    elif n==4: return 30
    else:      return 50

# === CLASS: FruitObj ===
class FruitObj:
    def __init__(self, image, slices, x, y, speed, letter=None, is_bomb=False, is_ice=False):
        self.image   = image
        self.slices  = slices
        self.x,self.y= x,y
        self.speed   = speed
        self.letter  = letter
        self.is_bomb = is_bomb
        self.is_ice  = is_ice
        self.sliced  = False
        self.sliced_time = 0
        # Offsets for slice anim
        self.offL=-40; self.offR=40
        self.velL=-3;  self.velR=3
        self.grav=1;   self.slice_y=0

    def draw(self):
        if not self.sliced:
            screen.blit(self.image, (self.x,self.y))
            if self.letter:
                draw_text(self.letter, FONT, WHITE,
                          self.x+new_w//2-15, self.y+new_h//2-25)
        else:
            screen.blit(self.slices[0], (self.x+self.offL, self.y+self.slice_y))
            screen.blit(self.slices[1], (self.x+self.offR, self.y+self.slice_y))

    def move(self, freeze=False):
        if not freeze or self.sliced:
            self.y += self.speed
        if self.sliced:
            self.offL  += self.velL
            self.offR  += self.velR
            self.slice_y+= self.grav

    def is_clicked(self, mouse_pos):
        """Check bounding box if user single-clicked exactly on object."""
        main_rect = pygame.Rect(self.x,self.y,new_w,new_h)
        if self.sliced:
            r1=pygame.Rect(self.x+self.offL,self.y+self.slice_y,new_w,new_h)
            r2=pygame.Rect(self.x+self.offR,self.y+self.slice_y,new_w,new_h)
            return (r1.collidepoint(mouse_pos) or r2.collidepoint(mouse_pos))
        else:
            return main_rect.collidepoint(mouse_pos)

    def circle_center(self):
        """Circle bounding for line intersection."""
        cx = self.x + new_w//2
        cy = self.y + new_h//2
        # Expand the radius a bit so slicing is easier
        radius = (new_w // 2) + 5  # e.g. 50 + 5 => 55
        return cx, cy, radius

# === CLASS: SlashFX ===
class SlashFX:
    def __init__(self,x,y, big=False):
        """If big=True, use a bigger slash image for a dragging/katana swipe."""
        self.x,self.y=x,y
        self.start=pygame.time.get_ticks()
        self.lifetime=300
        angle=random.randint(0,360)
        # pick which slash to use
        base_img = slash_img_big if big else slash_img_small
        self.image=pygame.transform.rotate(base_img, angle)

    def draw(self):
        screen.blit(self.image, (self.x - self.image.get_width()//2,
                                 self.y - self.image.get_height()//2))
    def expired(self):
        return (pygame.time.get_ticks() - self.start) > self.lifetime

# === Slicing Helpers ===
def slice_object(obj, slash_effects, sound_on, big_slash=False):
    """Set object to sliced, add a slash effect (big or small), play sound."""
    obj.sliced=True
    obj.sliced_time = pygame.time.get_ticks()
    cx = obj.x + new_w//2
    cy = obj.y + new_h//2
    slash_effects.append(SlashFX(cx,cy,big=big_slash))
    if sound_on:
        if obj.is_bomb: snd_bomb.play()
        elif obj.is_ice: snd_ice.play()
        else: snd_fruit.play()

def create_fruit(objs):
    x = random.randint(20, screen_w - new_w - 20)
    spd= random.uniform(1.0,2.0)
    letter= random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    i = random.randint(0,len(fruit_imgs)-1)
    objs.append(FruitObj(fruit_imgs[i], fruit_slices[i], x,0,spd, letter))

def create_ice(objs):
    x = random.randint(20, screen_w - new_w - 20)
    spd= random.uniform(1.0,2.0)
    letter= random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    objs.append(FruitObj(ice_img,[ice_img,ice_img],x,0,spd, letter, is_ice=True))

def create_bomb(objs):
    x = random.randint(20, screen_w - new_w - 20)
    spd= random.uniform(1.0,2.0)
    objs.append(FruitObj(bomb_img, bomb_slices, x,0,spd, is_bomb=True))

# === GAME OVER SCREEN ===
def game_over_screen(score, strikes, bombed, lang):
    clock=pygame.time.Clock()
    st=pygame.time.get_ticks()
    dur=3000
    while True:
        screen.blit(bg_img,(0,0))
        if bombed:
            draw_text(LANG[lang]["bomb_over"], FONT, RED, 250, screen_h//2-50)
        else:
            draw_text(LANG[lang]["strike_over"], FONT, RED, 250, screen_h//2-50)
        draw_text(f"{LANG[lang]['final_score']}: {score}", FONT, WHITE, 250, screen_h//2+20)
        pygame.display.flip()
        if pygame.time.get_ticks() - st > dur: break
        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                pygame.quit(); return
        clock.tick(60)
    return

def pause_menu(lang):
    clock=pygame.time.Clock()
    while True:
        overlay=pygame.Surface((screen_w,screen_h))
        overlay.set_alpha(180)
        overlay.fill((0,0,0))
        screen.blit(overlay,(0,0))

        draw_text(LANG[lang]["pause_menu"], FONT, RED, screen_w//2 - 100, 150)

        # Resume / MainMenu / Quit
        data=[("resume",300), ("main_menu",400), ("quit",500)]
        btn_rect={}
        for key,ypos in data:
            bw,bh=200,50
            bx=screen_w//2 - bw//2
            rect=pygame.Rect(bx,ypos,bw,bh)
            pygame.draw.rect(screen,BLACK,rect)
            label=LANG[lang].get(key, LANG[lang]["quit"])
            txt=SMALL_FONT.render(label, True, GREEN)
            txt_rect=txt.get_rect(center=rect.center)
            screen.blit(txt,txt_rect)
            btn_rect[key]=rect

        pygame.display.flip()
        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                return "quit"
            elif e.type==pygame.MOUSEBUTTONDOWN:
                mp=e.pos
                if btn_rect["resume"].collidepoint(mp):
                    return "resume"
                elif btn_rect["main_menu"].collidepoint(mp):
                    return "menu"
                elif btn_rect["quit"].collidepoint(mp):
                    return "quit"
        clock.tick(60)

# === MAIN GAME LOOP WITH DRAG-SLICING & COMBOS ===
def game_loop(lang, difficulty):
    # Fade out menu music, start game music
    pygame.mixer.music.fadeout(500)
    pygame.time.wait(300)
    pygame.mixer.music.load(GAME_MUSIC)
    pygame.mixer.music.play(-1)

    clock=pygame.time.Clock()
    objs=[]
    slash_fx=[]
    score,strikes=0,0

    # Difficulty -> spawn intervals & freeze times
    if difficulty=="easy":
        fruit_int,bomb_int,ice_int=(1500,20000,10000)
        freeze_duration=5000
    elif difficulty=="hard":
        fruit_int,bomb_int,ice_int=(100,6000,12000)
        freeze_duration=3000
    else: # normal
        fruit_int,bomb_int,ice_int=(1200,15000,8000)
        freeze_duration=4000

    fruit_t,bomb_t,ice_t=0,0,0
    freeze=False
    freeze_start=0

    bomb_sliced=False
    bomb_sliced_time=0
    BOMB_DELAY=700

    music_on=True
    sound_on=True
    def update_sound():
        vol=1.0 if sound_on else 0.0
        snd_fruit.set_volume(vol)
        snd_ice.set_volume(vol)
        snd_bomb.set_volume(vol)
    update_sound()

    # For drag slicing
    mouse_down=False
    old_mouse_pos=None

    running=True
    while running:
        screen.blit(bg_img,(0,0))
        now=pygame.time.get_ticks()

        # If bomb is sliced, we wait 700ms to show splitted bomb
        if bomb_sliced:
            if (now - bomb_sliced_time)>=BOMB_DELAY:
                game_over_screen(score,strikes,True,lang)
                running=False
        else:
            # Normal logic
            # We'll track slices each frame for combo
            newly_sliced=[]

            for e in pygame.event.get():
                if e.type==pygame.QUIT:
                    running=False
                elif e.type==pygame.MOUSEBUTTONDOWN:
                    mp=e.pos
                    # Check pause/music toggles
                    pause_btn=pygame.Rect(10,10,100,40)
                    if pause_btn.collidepoint(mp):
                        choice=pause_menu(lang)
                        if choice=="resume":
                            pass
                        elif choice=="menu":
                            running=False
                        elif choice=="quit":
                            pygame.quit(); return
                    music_btn=pygame.Rect(screen_w-100,10,40,40)
                    sound_btn=pygame.Rect(screen_w-50,10,40,40)
                    if music_btn.collidepoint(mp):
                        music_on=not music_on
                        pygame.mixer.music.set_volume(1.0 if music_on else 0.0)
                    elif sound_btn.collidepoint(mp):
                        sound_on=not sound_on
                        update_sound()
                    else:
                        # Start drag slicing
                        mouse_down=True
                        old_mouse_pos=mp

                        # Also check single-click bounding box
                        for obj in objs:
                            if not obj.sliced and obj.is_clicked(mp):
                                slice_object(obj, slash_fx, sound_on, big_slash=False)
                                newly_sliced.append(obj)
                                if obj.is_bomb:
                                    bomb_sliced=True
                                    bomb_sliced_time=now
                                elif obj.is_ice:
                                    freeze=True
                                    freeze_start=now
                elif e.type==pygame.MOUSEBUTTONUP:
                    mouse_down=False
                    old_mouse_pos=None
                elif e.type==pygame.MOUSEMOTION:
                    if mouse_down and old_mouse_pos:
                        x1,y1=old_mouse_pos
                        x2,y2=e.pos
                        # We do line vs. circle for each object
                        for obj in objs:
                            if not obj.sliced:
                                cx,cy,r=obj.circle_center()
                                # If line intersects circle => slice
                                if line_circle_intersect(x1,y1,x2,y2, cx,cy,r):
                                    slice_object(obj, slash_fx, sound_on, big_slash=True)
                                    newly_sliced.append(obj)
                                    if obj.is_bomb:
                                        bomb_sliced=True
                                        bomb_sliced_time=now
                                    elif obj.is_ice:
                                        freeze=True
                                        freeze_start=now
                        old_mouse_pos=e.pos
                elif e.type==pygame.KEYDOWN:
                    # letter-based slicing
                    kp=pygame.key.name(e.key).upper()
                    for obj in objs:
                        if not obj.sliced and (obj.letter==kp):
                            slice_object(obj, slash_fx, sound_on, big_slash=False)
                            newly_sliced.append(obj)
                            if obj.is_bomb:
                                bomb_sliced=True
                                bomb_sliced_time=now
                            elif obj.is_ice:
                                freeze=True
                                freeze_start=now

            # After collecting newly_sliced, compute combos for normal fruits
            normal_fruits = [o for o in newly_sliced if not o.is_bomb and not o.is_ice]
            n = len(normal_fruits)
            if n>0:
                # big combo formula
                score += combo_points(n)

        # Freeze logic
        if freeze and now - freeze_start>freeze_duration:
            freeze=False

        # Spawning if not frozen/bombed
        if not freeze and not bomb_sliced:
            if now-fruit_t>fruit_int:
                create_fruit(objs)
                fruit_t=now
            if now-bomb_t>bomb_int:
                create_bomb(objs)
                bomb_t=now
            if now-ice_t>ice_int:
                create_ice(objs)
                ice_t=now

        # Draw pause/music/sound buttons
        pause_btn=pygame.Rect(10,10,100,40)
        pygame.draw.rect(screen,(128,128,128), pause_btn)
        draw_text("Pause", SMALL_FONT, WHITE, pause_btn.x+10, pause_btn.y+5)

        music_btn=pygame.Rect(screen_w-100,10,40,40)
        sound_btn=pygame.Rect(screen_w-50,10,40,40)
        pygame.draw.rect(screen,(128,128,128),music_btn)
        pygame.draw.rect(screen,(128,128,128),sound_btn)
        draw_text("M",SMALL_FONT,WHITE,music_btn.x+10,music_btn.y+5)
        draw_text("S",SMALL_FONT,WHITE,sound_btn.x+10,sound_btn.y+5)

        # Update & draw objects
        to_remove=[]
        for obj in objs:
            obj.move(freeze)
            obj.draw()
            # Miss => strike
            if (obj.y>screen_h) and (not obj.sliced) and (not obj.is_bomb) and (not obj.is_ice):
                strikes+=1
                to_remove.append(obj)
            # remove after 1s if sliced
            if obj.sliced and (now-obj.sliced_time>1000):
                to_remove.append(obj)
        for r in to_remove:
            if r in objs:
                objs.remove(r)

        # Slash effects
        expired_fx=[]
        for fx in slash_fx:
            if fx.expired():
                expired_fx.append(fx)
            else:
                fx.draw()
        for ef in expired_fx:
            slash_fx.remove(ef)

        # 3 strikes => game over if no bomb has been sliced
        if (not bomb_sliced) and (strikes>=3):
            game_over_screen(score,strikes,False,lang)
            running=False

        # HUD
        draw_text(f"{LANG[lang]['score']}: {score}", FONT, WHITE, 10,60)
        hearts_left = 3 - strikes
        for i in range(hearts_left):
            screen.blit(heart_icon, (10 + i*(heart_icon.get_width()+5), 120))

        pygame.display.flip()
        clock.tick(60)

    # after loop => fade out music => back to menu
    pygame.mixer.music.fadeout(500)
    pygame.time.wait(300)
    pygame.mixer.music.load(MENU_MUSIC)
    pygame.mixer.music.play(-1)

# === SUB MENUS / MAIN MENU ===
def choose_language(current_lang):
    clock=pygame.time.Clock()
    while True:
        screen.blit(bg_img,(0,0))
        draw_text("Choisir la Langue / Choose Language", FONT, RED, 300,100)

        # 3 buttons: English, French, Back
        data = [
            ("English", "en", 300),
            ("Français","fr", 400),
            (LANG[current_lang]["back"], None, 500)
        ]
        rects={}
        for label, val, y in data:
            bw,bh=200,50
            bx=screen_w//2 - bw//2
            r=pygame.Rect(bx,y,bw,bh)
            pygame.draw.rect(screen,BLACK,r)
            t=SMALL_FONT.render(label, True, GREEN)
            t_rect=t.get_rect(center=r.center)
            screen.blit(t,t_rect)
            rects[val]=r

        pygame.display.flip()
        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                pygame.quit(); return current_lang
            elif e.type==pygame.MOUSEBUTTONDOWN:
                for val,rct in rects.items():
                    if rct.collidepoint(e.pos):
                        if val==None: # Back
                            return current_lang
                        else:
                            return val
        clock.tick(60)

def choose_difficulty(lang,curr_diff):
    clock=pygame.time.Clock()
    while True:
        screen.blit(bg_img,(0,0))
        draw_text(LANG[lang]["diff"], FONT, RED, screen_w//2-50, 100)

        data = [
            ("easy",   LANG[lang]["easy"],   300),
            ("normal", LANG[lang]["normal"], 400),
            ("hard",   LANG[lang]["hard"],   500),
            ("back",   LANG[lang]["back"],   600)
        ]
        rects={}
        for diff_key,label,y in data:
            bw,bh=200,50
            bx=screen_w//2 - bw//2
            r=pygame.Rect(bx,y,bw,bh)
            pygame.draw.rect(screen,BLACK,r)
            t=SMALL_FONT.render(label,True,GREEN)
            t_rect=t.get_rect(center=r.center)
            screen.blit(t,t_rect)
            rects[diff_key]=r

        pygame.display.flip()
        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                pygame.quit(); return curr_diff
            elif e.type==pygame.MOUSEBUTTONDOWN:
                for k,rct in rects.items():
                    if rct.collidepoint(e.pos):
                        if k=="back":
                            return curr_diff
                        else:
                            return k
        clock.tick(60)

def main_menu(lang,diff):
    clock=pygame.time.Clock()
    while True:
        screen.blit(bg_img,(0,0))
        title_txt = LANG[lang]["menu_title"]
        ts=FONT.render(title_txt,True,BROWN)
        tr=ts.get_rect(center=(screen_w//2,100))
        screen.blit(ts,tr)

        diff_label = LANG[lang]["diff"] + ": " + LANG[lang][diff]
        ds=SMALL_FONT.render(diff_label,True,RED)
        dr=ds.get_rect(center=(screen_w//2,170))
        screen.blit(ds,dr)

        data=[("play",220),("lang",320),("diff",420),("quit",520)]
        rects={}
        for k,y in data:
            bw,bh=200,50
            bx=screen_w//2 - bw//2
            r=pygame.Rect(bx,y,bw,bh)
            pygame.draw.rect(screen,BLACK,r)
            text_str=LANG[lang][k]
            t=SMALL_FONT.render(text_str,True,GREEN)
            t_rect=t.get_rect(center=r.center)
            screen.blit(t,t_rect)
            rects[k]=r

        pygame.display.flip()
        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                return "quit"
            elif e.type==pygame.MOUSEBUTTONDOWN:
                for key in rects:
                    if rects[key].collidepoint(e.pos):
                        return key
        clock.tick(60)

def main():
    pygame.mixer.music.load(MENU_MUSIC)
    pygame.mixer.music.play(-1)

    current_lang="fr"
    current_diff="normal"

    while True:
        choice = main_menu(current_lang, current_diff)
        if choice=="quit":
            pygame.quit(); break
        elif choice=="lang":
            current_lang=choose_language(current_lang)
        elif choice=="diff":
            current_diff=choose_difficulty(current_lang, current_diff)
        elif choice=="play":
            game_loop(current_lang, current_diff)

if __name__=="__main__":
    main()
