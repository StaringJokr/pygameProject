"""
The main file of game
"""
import MyClasses.player
from settings import *
import sys
import pygame as pg
import MyClasses.control as mc_control
import MyClasses.player as mc_player
from MyClasses.objects import DroppedItem, Entity, LootBox, Chest

from random import randint as rand


def new_coin(x, y, inf=False):
    global coin_textures, CoinsGroup, objManager
    new_c = DroppedItem(x, y, coin_textures, lambda _: pl1.add_money(1), objManager, CoinsGroup, inf=inf)
    return new_c

def new_healka(x, y, inf=False):
    global healka_textures, HealkasGroup
    new_h = DroppedItem(x, y, healka_textures,
                        lambda _: pl1.add_hp(5, rand(1, 5) == 5),
                        objManager, HealkasGroup, inf=inf)
    return new_h

def choose_obj():
    mpos = pg.mouse.get_pos()
    mpos = (mpos[0] / mnog, mpos[1] / mnog)
    print(mpos, pl1.rect.center)
    for obj in CoinsGroup:
        if obj.rect.collidepoint(mpos):
            print(obj)
            gugugaga.set_current(obj)
    for obj in HealkasGroup:
        if obj.rect.collidepoint(mpos):
            print(obj)
            gugugaga.set_current(obj)
    for obj in LootBoxesGroup:
        if obj.rect.collidepoint(mpos):
            print(obj)
            gugugaga.set_current(obj)
    for obj in AllEntities:
        if obj.rect.collidepoint(mpos):
            print(obj)
            gugugaga.set_current(obj)

def interact_item(player, sprite_group, keys):
    for item in sprite_group:
        zone = item.get_interzone()
        if pg.sprite.collide_rect(player, zone):
            zone.collide(player, keys)
        else:
            zone.no_collide(player)


mnog = 0.5
if len(sys.argv) > 1:
    try:
        mnog = min(int(sys.argv[1]) / ORIGSCENEW, int(sys.argv[2]) / ORIGSCENEH)
        WIDTH = int(ORIGSCENEW * mnog)
        HEIGHT = int(ORIGSCENEH * mnog)
    except ValueError:
        print("size in numbers pls...")
    try:
        FPS = int(sys.argv[3])
    except:
        print("cho v 3?")


pg.init()
real_window = pg.display.set_mode([WIDTH, HEIGHT], pg.HWSURFACE | pg.DOUBLEBUF)

window_surface = pg.Surface([ORIGSCENEW, ORIGSCENEH])  # Creating a surface for converting window resolution for different monitors

clock = pg.time.Clock()
saver = mc_control.SaveManager()
saver.load()

bg = pg.image.load(sys.path[0] + "/res/textures/background.png")

font0 = pg.font.SysFont("freesansbold.ttf", 58)
text = font0.render("0", True, (200, 140, 193))
text.get_rect().center = (10, 20)

planims = {"Idle": [], "Walk": [], "Attack": []}

pl_texture = pg.image.load(sys.path[0] + "/res/textures/knight/HeroKnight.png").convert_alpha()

objManager = mc_control.ObjectManager(sys.path[0] + "/log.txt")

for iframe in range(8):
    sprite = pg.Surface((100, 55), pg.SRCALPHA)
    sprite.blit(pl_texture, (0, 0), (iframe * 100, 0, 100, 55))
    planims["Idle"].append(pg.transform.scale(sprite, (200, 110)))

sprite = pg.Surface((100, 55), pg.SRCALPHA)
sprite.blit(pl_texture, (0, 0), (800, 0, 100, 55))
planims["Walk"].append(pg.transform.scale(sprite, (200, 110)))
sprite = pg.Surface((100, 55), pg.SRCALPHA)
sprite.blit(pl_texture, (0, 0), (900, 0, 100, 55))
planims["Walk"].append(pg.transform.scale(sprite, (200, 110)))

for iframe in range(8):
    sprite = pg.Surface((100, 55), pg.SRCALPHA)
    sprite.blit(pl_texture, (0, 0), (iframe * 100, 55, 100, 55))
    planims["Walk"].append(pg.transform.scale(sprite, (200, 110)))

sprite = pg.Surface((100, 55), pg.SRCALPHA)
sprite.blit(pl_texture, (0, 0), (800, 55, 100, 55))
planims["Attack"].append(pg.transform.scale(sprite, (200, 110)))
sprite = pg.Surface((100, 55), pg.SRCALPHA)
sprite.blit(pl_texture, (0, 0), (900, 55, 100, 55))
planims["Attack"].append(pg.transform.scale(sprite, (200, 110)))
for iframe in range(5):
    sprite = pg.Surface((100, 55), pg.SRCALPHA)
    sprite.blit(pl_texture, (0, 0), (iframe * 100, 110, 200, 55))
    planims["Attack"].append(pg.transform.scale(sprite, (200, 110)))


#pl1 = mc_player.Player((60, 60), 400, 100, 75, planims, obj_manager=objManager)
pl1 = saver.player(mc_player.Player, planims, obj_manager=objManager)

gugugaga = mc_control.Info()

coin_textures = [pg.image.load(sys.path[0] + f"/res/textures/coin{i}.png") for i in range(1, 7)]

sprite = pg.Surface((16, 16), pg.SRCALPHA)
sprite.blit(pg.image.load(sys.path[0] + f"/res/textures/Potion.png").convert_alpha(), (0, 0), (16, 17, 16, 16))

healka_textures =[pg.transform.scale(sprite, (48, 48))]


sprite = pg.Surface((16, 16), pg.SRCALPHA)
sprite.blit(pg.image.load(sys.path[0] + f"/res/textures/Barrel16x.png").convert_alpha(), (0, 0), (0, 0, 16, 16))

CoinsGroup = pg.sprite.Group()
HealkasGroup = pg.sprite.Group()
LootBoxesGroup = pg.sprite.Group()
EntitiesGroup = pg.sprite.Group()

#npc1 = Entity((32, 280), 400, 200, 120, 5, planims, obj_manager=objManager, spriteGroup=EntityGroup)
#EntityGroup.add(npc1)

saver.drops(new_coin, drop_type="coin")
saver.drops(new_healka, drop_type="healka")
saver.loot_boxes(LootBox, (pg.transform.scale(sprite, (48, 48)),
                          pg.image.load(sys.path[0] + f"/res/textures/chests/gray_chest1.png")),
                 new_coin, objManager, LootBoxesGroup)
saver.entities(Entity, planims, objManager, EntitiesGroup)

AllEntities = set()
AllEntities.add(pl1)
AllEntities.update(EntitiesGroup)


sprite = pg.Surface((21, 23), pg.SRCALPHA)
sprite.blit(pg.image.load(sys.path[0] + f"/res/textures/chests/gray_chest.png").convert_alpha(), (0, 0), (0, 0, 21, 23))
chest_textures = [pg.transform.scale(sprite, (42, 46))]
sprite = pg.Surface((21, 23), pg.SRCALPHA)
sprite.blit(pg.image.load(sys.path[0] + f"/res/textures/chests/gray_chest1.png").convert_alpha(), (0, 0), (0, 0, 21, 23))
chest_textures.append(pg.transform.scale(sprite, (42, 46)))
chest1 = Chest(300, 500, 10, 4, chest_textures, objManager, HealkasGroup)

while True:
    dt = clock.tick(FPS)

    keys = pg.key.get_pressed()
    if keys[pg.K_i]: saver.save(pl1, CoinsGroup,
                                HealkasGroup, LootBoxesGroup, EntitiesGroup, False)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            print("gg")
            objManager.stop_game()
            exit()
        if event.type == pg.MOUSEBUTTONDOWN:
            print("!!!")
            choose_obj()
        if event.type == pg.KEYDOWN:
            #key = pg.key.name(event.key)
            #print(key, "Key is pressed")
            if event.key == pg.K_ESCAPE:
                print("gg")
                objManager.stop_game()
                exit()
            if event.key == pg.K_TAB: gugugaga.hide = not gugugaga.hide
            if event.key == pg.K_COMMA:
                pl1.action = "Attack"
                pl1.frame_delay = 0.08
                pl1.frame = 0
        if event.type == pg.KEYUP:
            #key = pg.key.name(event.key)
            #print(key, "Key is released")
            pass

    # Background
    # window_surface.blit(bg, (0, 0))
    window_surface.fill(SKYBLUE)

    #touch_coin(pl1, CoinsGroup)
    interact_item(pl1, CoinsGroup, keys)
    interact_item(pl1, HealkasGroup, keys)
    CoinsGroup.update(dtime=dt / 1000, surf=window_surface)
    LootBoxesGroup.update(surf=window_surface)
    HealkasGroup.update(dtime=dt / 1000, surf=window_surface)

    for entity in sorted(AllEntities, key=lambda obj: obj.rect.bottom):
        entity.update_object(W=ORIGSCENEW, H=ORIGSCENEH, dtime=dt / 1000, surf=window_surface)
        entity.draw(window_surface)

    if not gugugaga.hide:
        gugugaga.update_info()
        window_surface.blit(gugugaga, (ORIGSCENEW - 250, ORIGSCENEH // 2 - 380))

    objManager.blit_guis(window_surface)

    frame = pg.transform.scale(window_surface, (WIDTH, HEIGHT))
    real_window.blit(frame, frame.get_rect())
    real_window.blit(text, (0, 0))
    text = font0.render(str(round(clock.get_fps(), 2)), True, (200, 140, 193))

    pg.display.update()
