import pygame
import random

pygame.init()

# === Window Setup ===
screen_w, screen_h = 1280, 720
screen = pygame.display.set_mode((screen_w, screen_h))
pygame.display.set_caption("FRUIT SLICER GAME")

bg_img = pygame.image.load("images/fruit.jpg")
bg_img = pygame.transform.scale(bg_img, (screen_w, screen_h))

# === Fonts / Colors ===
FONT = pygame.font.SysFont('Roboto', 50)
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

def load_and_resize_image(path,w,h):
    img=pygame.image.load(path)
    return pygame.transform.scale(img,(w,h))

# === Slash + Lives Icon ===
slash_img  = load_and_resize_image("images/slash.png",120,120)
heart_icon = load_and_resize_image("images/red_lives.png",40,40)

# === Fruit / Ice / Bomb Setup ===
new_w,new_h=100,100
fruit_imgs = [
    load_and_resize_image("images/kiwi.png",   new_w,new_h),
    load_and_resize_image("images/pomme.png",  new_w,new_h),
    load_and_resize_image("images/orange.png", new_w,new_h)
]
fruit_slices = [
    [load_and_resize_image("images/kiwi-split1.png",  new_w,new_h),
     load_and_resize_image("images/kiwi-split2.png",  new_w,new_h)],
    [load_and_resize_image("images/pomme-split1.png", new_w,new_h),
     load_and_resize_image("images/pomme-split2.png", new_w,new_h)],
    [load_and_resize_image("images/orange-split1.png",new_w,new_h),
     load_and_resize_image("images/orange-split2.png",new_w,new_h)]
]

ice_img = load_and_resize_image("images/glacon.png", new_w,new_h)
# Bomb + bomb slices (bombe-split1.png / bombe-split2.png)
bomb_img     = load_and_resize_image("images/bombe.png", new_w,new_h)
bomb_slices  = [
    load_and_resize_image("images/bombe-split1.png", new_w,new_h),
    load_and_resize_image("images/bombe-split2.png", new_w,new_h)
]

# === CLASSES ===
class FruitObj:
    def __init__(self, image, slices, x, y, speed, letter=None, is_bomb=False, is_ice=False):
        self.image=image
        self.slices=slices
        self.x,self.y=x,y
        self.speed=speed
        self.letter=letter
        self.is_bomb=is_bomb; self.is_ice=is_ice
        self.sliced=False
        self.sliced_time=0
        self.offL=-40; self.offR=40
        self.velL=-3;  self.velR=3
        self.grav=1;   self.slice_y=0
    def draw(self):
        if not self.sliced:
            screen.blit(self.image,(self.x,self.y))
            if self.letter:
                draw_text(self.letter, FONT, WHITE,
                          self.x+new_w//2-15, self.y+new_h//2-25)
        else:
            screen.blit(self.slices[0],(self.x+self.offL, self.y+self.slice_y))
            screen.blit(self.slices[1],(self.x+self.offR, self.y+self.slice_y))
    def move(self, frozen=False):
        if not frozen or self.sliced:
            self.y+=self.speed
        if self.sliced:
            self.offL+=self.velL
            self.offR+=self.velR
            self.slice_y+=self.grav
    def is_clicked(self, mp):
        main_rect=pygame.Rect(self.x, self.y, new_w, new_h)
        if self.sliced:
            r1=pygame.Rect(self.x+self.offL,self.y+self.slice_y,new_w,new_h)
            r2=pygame.Rect(self.x+self.offR,self.y+self.slice_y,new_w,new_h)
            return (r1.collidepoint(mp) or r2.collidepoint(mp))
        else:
            return main_rect.collidepoint(mp)

class SlashFX:
    def __init__(self,x,y):
        self.x,self.y=x,y
        self.start=pygame.time.get_ticks()
        self.life=300
        angle=random.randint(0,360)
        self.image=pygame.transform.rotate(slash_img, angle)
    def draw(self):
        screen.blit(self.image,(self.x-self.image.get_width()//2,
                                self.y-self.image.get_height()//2))
    def expired(self):
        return pygame.time.get_ticks()-self.start>self.life

# === CREATE OBJECTS ===
def create_fruit(objs):
    x=random.randint(20, screen_w-new_w-20)
    y=0
    spd=random.uniform(1.0,2.0)
    letter=random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    idx=random.randint(0,len(fruit_imgs)-1)
    fruit=FruitObj(fruit_imgs[idx], fruit_slices[idx], x,y,spd, letter)
    objs.append(fruit)

def create_ice(objs):
    x=random.randint(20, screen_w-new_w-20)
    spd=random.uniform(1.0,2.0)
    letter=random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    ice=FruitObj(ice_img,[ice_img,ice_img],x,0,spd,letter,is_ice=True)
    objs.append(ice)

def create_bomb(objs):
    x=random.randint(20, screen_w-new_w-20)
    y=0
    spd=random.uniform(1.0,2.0)
    bomb=FruitObj(bomb_img, bomb_slices, x,y,spd,is_bomb=True)
    objs.append(bomb)

def slice_obj(obj, slash_fx, sound_on):
    obj.sliced=True
    obj.sliced_time=pygame.time.get_ticks()
    cx,cy=obj.x+new_w//2, obj.y+new_h//2
    slash_fx.append(SlashFX(cx,cy))
    if sound_on:
        if obj.is_bomb: snd_bomb.play()
        elif obj.is_ice: snd_ice.play()
        else: snd_fruit.play()

# === GAME OVER SCREEN ===
def game_over_screen(score,strikes,bombed, lang):
    clock=pygame.time.Clock()
    st=pygame.time.get_ticks(); dur=3000
    while True:
        screen.blit(bg_img,(0,0))
        if bombed:
            draw_text(LANG[lang]["bomb_over"], FONT, RED, 250, screen_h//2-50)
        else:
            draw_text(LANG[lang]["strike_over"], FONT, RED, 250, screen_h//2-50)
        draw_text(f"{LANG[lang]['final_score']}: {score}", FONT, WHITE, 250, screen_h//2+20)
        pygame.display.flip()
        if pygame.time.get_ticks()-st>dur: break
        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                pygame.quit(); return
        clock.tick(60)
    return

# === PAUSE MENU (in-game) ===
def pause_menu(lang):
    clock=pygame.time.Clock()
    while True:
        # Overlay
        overlay=pygame.Surface((screen_w,screen_h))
        overlay.set_alpha(180)
        overlay.fill((0,0,0))
        screen.blit(overlay,(0,0))

        draw_text(LANG[lang]["pause_menu"], FONT, RED, screen_w//2-100, 150)

        # Buttons (Resume, MainMenu, Quit)
        btn_data=[("resume",300), ("main_menu",400), ("quit",500)]
        btn_rects={}
        for key,ypos in btn_data:
            bw,bh=200,50
            bx=screen_w//2 - bw//2
            rect=pygame.Rect(bx,ypos,bw,bh)
            pygame.draw.rect(screen,BLACK,rect)
            label=LANG[lang].get(key, LANG[lang]["quit"])
            txt_surf=SMALL_FONT.render(label,True,GREEN)
            txt_rect=txt_surf.get_rect(center=rect.center)
            screen.blit(txt_surf,txt_rect)
            btn_rects[key]=rect

        pygame.display.flip()
        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                return "quit"
            if e.type==pygame.MOUSEBUTTONDOWN:
                mp=e.pos
                if btn_rects["resume"].collidepoint(mp):
                    return "resume"
                elif btn_rects["main_menu"].collidepoint(mp):
                    return "menu"
                elif btn_rects["quit"].collidepoint(mp):
                    return "quit"
        clock.tick(60)

# === GAME LOOP ===
def game_loop(lang, difficulty):
    # Fade out menu music & start game music
    pygame.mixer.music.fadeout(500)
    pygame.time.wait(300)
    pygame.mixer.music.load(GAME_MUSIC)
    pygame.mixer.music.play(-1)

    clock=pygame.time.Clock()
    objs=[]
    slash_fx=[]
    score=0
    strikes=0

    # Freeze durations by diff
    if difficulty=="easy":
        fruit_int,bomb_int,ice_int = (1500,20000,10000)
        freeze_duration=5000
    elif difficulty=="hard":
        fruit_int,bomb_int,ice_int = (800,8000,12000)
        freeze_duration=3000
    else:
        fruit_int,bomb_int,ice_int = (1200,15000,8000)
        freeze_duration=4000

    fruit_t,bomb_t,ice_t=0,0,0
    freeze=False
    freeze_start=0

    # Slicing a bomb => we still want to see splitted bomb for ~700ms
    bomb_sliced=False
    bomb_sliced_time=0
    BOMB_DELAY=700  # how long to show splitted bomb before Game Over

    music_on=True
    sound_on=True
    def update_sndvol():
        vol=1.0 if sound_on else 0.0
        snd_bomb.set_volume(vol)
        snd_fruit.set_volume(vol)
        snd_ice.set_volume(vol)
    update_sndvol()

    running=True
    while running:
        screen.blit(bg_img,(0,0))
        now=pygame.time.get_ticks()

        # If we already sliced a bomb, wait ~700ms then do game over
        if bomb_sliced:
            if now - bomb_sliced_time >= BOMB_DELAY:
                game_over_screen(score,strikes,True,lang)
                running=False
            else:
                # We STILL draw objects (including splitted bomb), so the user can see the effect
                pass
        else:
            # Normal input handling only if bomb not already sliced
            # (so you can’t slice more fruits after the bomb is sliced)
            for e in pygame.event.get():
                if e.type==pygame.QUIT:
                    running=False
                elif e.type==pygame.MOUSEBUTTONDOWN:
                    mp=e.pos
                    # Pause button?
                    pause_rect=pygame.Rect(10,10,100,40)
                    if pause_rect.collidepoint(mp):
                        pm_choice=pause_menu(lang)
                        if pm_choice=="resume":
                            pass
                        elif pm_choice=="menu":
                            running=False
                        elif pm_choice=="quit":
                            pygame.quit()
                            return
                    # Music toggle?
                    music_btn=pygame.Rect(screen_w-100,10,40,40)
                    sound_btn=pygame.Rect(screen_w-50,10,40,40)
                    if music_btn.collidepoint(mp):
                        music_on=not music_on
                        pygame.mixer.music.set_volume(1.0 if music_on else 0.0)
                    elif sound_btn.collidepoint(mp):
                        sound_on=not sound_on
                        update_sndvol()
                    else:
                        # Check objects
                        for obj in objs:
                            if not obj.sliced and obj.is_clicked(mp):
                                slice_obj(obj, slash_fx, sound_on)
                                if obj.is_bomb:
                                    # Mark bomb_sliced => show splitted
                                    bomb_sliced=True
                                    bomb_sliced_time=now
                                elif obj.is_ice:
                                    freeze=True
                                    freeze_start=now
                                else:
                                    score+=1
                                break
                elif e.type==pygame.KEYDOWN:
                    kp=pygame.key.name(e.key).upper()
                    for obj in objs:
                        if not obj.sliced and obj.letter==kp:
                            slice_obj(obj, slash_fx, sound_on)
                            if obj.is_bomb:
                                bomb_sliced=True
                                bomb_sliced_time=now
                            elif obj.is_ice:
                                freeze=True
                                freeze_start=now
                            else:
                                score+=1
                            break

        # Pause button
        pause_rect=pygame.Rect(10,10,100,40)
        pygame.draw.rect(screen,(128,128,128), pause_rect)
        draw_text("Pause",SMALL_FONT,WHITE, pause_rect.x+10, pause_rect.y+5)

        # Music / Sound toggles
        music_rect=pygame.Rect(screen_w-100,10,40,40)
        sound_rect=pygame.Rect(screen_w-50,10,40,40)
        pygame.draw.rect(screen,(128,128,128),music_rect)
        pygame.draw.rect(screen,(128,128,128),sound_rect)
        draw_text("M",SMALL_FONT,WHITE,music_rect.x+10,music_rect.y+5)
        draw_text("S",SMALL_FONT,WHITE,sound_rect.x+10,sound_rect.y+5)

        if freeze and now - freeze_start>= freeze_duration:
            freeze=False

        if not freeze:
            if now-fruit_t>fruit_int:
                create_fruit(objs)
                fruit_t=now
            if now-bomb_t>bomb_int:
                create_bomb(objs)
                bomb_t=now
            if now-ice_t>ice_int:
                create_ice(objs)
                ice_t=now

        # Update & Draw objects
        to_remove=[]
        for obj in objs:
            obj.move(freeze)
            obj.draw()
            # Miss => strike
            if obj.y>screen_h and not obj.sliced and not obj.is_bomb:
                strikes+=1
                to_remove.append(obj)
            # remove after 1s if sliced
            if obj.sliced and now-obj.sliced_time>1000:
                to_remove.append(obj)
        for r in to_remove:
            if r in objs: objs.remove(r)

        # Slash effects
        dead_fx=[]
        for fx in slash_fx:
            if fx.expired(): dead_fx.append(fx)
            else: fx.draw()
        for d in dead_fx: slash_fx.remove(d)

        # 3 strikes => game over
        if not bomb_sliced and strikes>=3:
            game_over_screen(score,strikes,False,lang)
            running=False

        # HUD
        draw_text(f"{LANG[lang]['score']}: {score}", FONT, WHITE, 10,60)
        hearts_left = 3 - strikes
        for i in range(hearts_left):
            screen.blit(heart_icon,(10 + i*(heart_icon.get_width()+5),120))

        pygame.display.flip()
        clock.tick(60)

    # after game loop => fade out game music => back to menu music
    pygame.mixer.music.fadeout(500)
    pygame.time.wait(300)
    pygame.mixer.music.load(MENU_MUSIC)
    pygame.mixer.music.play(-1)

# === SUB MENUS (with BACK button) ===
def choose_language(current_lang):
    clock=pygame.time.Clock()
    while True:
        screen.blit(bg_img,(0,0))
        draw_text("Choisir la Langue / Choose Language",FONT,RED, 300,100)

        # We'll define 3 buttons: English, French, Back
        btn_data=[("English","en",300), ("Français","fr",400), (LANG[current_lang]["back"], None,500)]
        btn_rects={}
        for label, val, ypos in btn_data:
            bw,bh=200,50
            bx=screen_w//2 - bw//2
            rect=pygame.Rect(bx,ypos,bw,bh)
            pygame.draw.rect(screen,BLACK,rect)
            txt_surf=SMALL_FONT.render(label, True, GREEN)
            txt_rect=txt_surf.get_rect(center=rect.center)
            screen.blit(txt_surf, txt_rect)
            btn_rects[val]=rect

        pygame.display.flip()
        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                pygame.quit()
                return current_lang
            elif e.type==pygame.MOUSEBUTTONDOWN:
                mp=e.pos
                for val,rect in btn_rects.items():
                    if rect.collidepoint(mp):
                        if val==None: # clicked on "Back"
                            return current_lang
                        else:
                            return val
        clock.tick(60)

def choose_difficulty(current_lang,current_diff):
    clock=pygame.time.Clock()
    while True:
        screen.blit(bg_img,(0,0))
        # Title
        draw_text(LANG[current_lang]["diff"], FONT, RED, screen_w//2-50, 100)

        # Buttons: easy, normal, hard, back
        diff_data=[
            ("easy", LANG[current_lang]["easy"], 300),
            ("normal", LANG[current_lang]["normal"], 400),
            ("hard", LANG[current_lang]["hard"], 500),
            ("back", LANG[current_lang]["back"], 600)
        ]
        btn_rects={}
        for diff_key,label,ypos in diff_data:
            bw,bh=200,50
            bx=screen_w//2 - bw//2
            rect=pygame.Rect(bx,ypos,bw,bh)
            pygame.draw.rect(screen,BLACK,rect)
            txt_surf=SMALL_FONT.render(label,True,GREEN)
            txt_rect=txt_surf.get_rect(center=rect.center)
            screen.blit(txt_surf,txt_rect)
            btn_rects[diff_key]=rect

        pygame.display.flip()
        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                pygame.quit()
                return current_diff
            elif e.type==pygame.MOUSEBUTTONDOWN:
                mp=e.pos
                for diff_key, rct in btn_rects.items():
                    if rct.collidepoint(mp):
                        if diff_key=="back":
                            return current_diff
                        else:
                            return diff_key
        clock.tick(60)

# === MAIN MENU ===
def main_menu(current_lang, current_diff):
    clock=pygame.time.Clock()
    while True:
        screen.blit(bg_img,(0,0))
        # Title
        title_str = LANG[current_lang]["menu_title"]
        title_surf=FONT.render(title_str,True,BROWN)
        title_rect=title_surf.get_rect(center=(screen_w//2,100))
        screen.blit(title_surf,title_rect)

        # Show chosen difficulty
        diff_label = LANG[current_lang]["diff"] + ": " + LANG[current_lang][current_diff]
        diff_surf  = SMALL_FONT.render(diff_label,True,RED)
        diff_rect  = diff_surf.get_rect(center=(screen_w//2,170))
        screen.blit(diff_surf,diff_rect)

        # 4 Buttons: play, lang, diff, quit
        menu_items=[("play",220),("lang",320),("diff",420),("quit",520)]
        btn_rects={}
        for key,ypos in menu_items:
            bw,bh=200,50
            bx=screen_w//2 - bw//2
            rect=pygame.Rect(bx,ypos,bw,bh)
            pygame.draw.rect(screen,BLACK,rect)
            text_str=LANG[current_lang][key]
            text_surf=SMALL_FONT.render(text_str,True,GREEN)
            text_rect=text_surf.get_rect(center=rect.center)
            screen.blit(text_surf, text_rect)
            btn_rects[key]=rect

        pygame.display.flip()
        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                return "quit"
            if e.type==pygame.MOUSEBUTTONDOWN:
                mp=e.pos
                for key in btn_rects:
                    if btn_rects[key].collidepoint(mp):
                        return key
        clock.tick(60)

def main():
    # Start menu music
    pygame.mixer.music.load(MENU_MUSIC)
    pygame.mixer.music.play(-1)

    current_lang="fr"
    current_diff="normal"

    while True:
        choice=main_menu(current_lang, current_diff)
        if choice=="quit":
            pygame.quit()
            break
        elif choice=="lang":
            current_lang=choose_language(current_lang)
        elif choice=="diff":
            current_diff=choose_difficulty(current_lang,current_diff)
        elif choice=="play":
            game_loop(current_lang, current_diff)

if __name__=="__main__":
    main()
