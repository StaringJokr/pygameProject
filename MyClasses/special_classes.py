import pygame as pg
from settings import *

class InteractiveBox(pg.Surface):
    def __init__(self, owner, center, width, height, interact_keys: tuple, can_hold: tuple):
        pg.Surface.__init__(self, (width, height))
        self.owner = owner
        self.rect = self.get_rect()
        self.rect.center = center
        self.interact_keys = interact_keys
        self.player_in_zone_now = False
        self.can_hold = can_hold
        self.last_keys = []

    def collide(self, player, keys):
        self.player_in_zone_now = True
        self.owner.when_player_in_zone(player)
        new_last_keys = []
        interacted_keys = []
        for key in self.interact_keys:
            if keys[key]:
                if key in self.can_hold:
                    interacted_keys.append(key)
                elif not (key in self.last_keys):
                    interacted_keys.append(key)
                new_last_keys.append(key)

        self.last_keys = new_last_keys
        if interacted_keys:
            self.owner.interact(player, interacted_keys)

    def no_collide(self, player):
        if self.player_in_zone_now:
            self.owner.when_player_leave_zone(player)
        self.player_in_zone_now = False


class InteractiveWidget(pg.Surface):
    def __init__(self, center, width, height, **kwargs):
        pg.Surface.__init__(self, (width, height))
        self.rect = self.get_rect()
        self.rect.center = center
        self.fill((100, 100, 100))
        self.set_alpha(50)


class ProgressBar(pg.Surface):
    def __init__(self, owner, dxdy: tuple, wh: tuple, percent, bg_color, main_color,
                 outline_c=False, outline_fatness=1):
        pg.Surface.__init__(self, (wh[0], wh[1]))

        self.owner = owner
        self.dx, self.dy = dxdy
        self.width, self.height = wh
        self.percent = percent
        self.bg_color = bg_color
        self.main_color = main_color
        self.outline_c = outline_c
        self.outline_fatness = outline_fatness
        self.update(percent)

    def update(self, percent):
        self.percent = percent
        if self.percent <= 100:
            pg.draw.rect(self, self.bg_color, (0, 0, self.width, self.height))
            pg.draw.rect(self, self.main_color, (0, 0, int(self.width * percent / 100), self.height))
        elif self.percent < 200:
            self.fill(GOLD)
            pg.draw.rect(self, self.main_color, (int(self.width * (percent % 100) / 100), 0, 100, self.height))
        else:
            self.fill(GOLD)

        if self.outline_c:
            pg.draw.rect(self, self.outline_c, (0, 0, self.width, self.height), self.outline_fatness)


    def draw(self, surf: pg.Surface):
        surf.blit(self, (self.owner.rect.center[0] + self.dx - self.width // 2, self.owner.rect.top + self.dy))

class HitZone(pg.Surface):
    def __init__(self, owner, pos, wh, damage, obj_manager):
        width, height = wh
        pg.Surface.__init__(self, (width, height))
        self.rect_for_pl = self.get_rect()
        self.rect_for_pl.topleft = pos

        self.damage = damage

        self.already_attacked = set()

        self.mask = pg.mask.from_surface(self)
        self.owner = owner
        self.obj_manager = obj_manager

    def check_collide(self):
        enemys = set(self.obj_manager.get_all()) - set((self.owner, )) - self.already_attacked
        self.rect = self.get_rect(topleft=(self.rect_for_pl[0], self.rect_for_pl[1]))

        for enemy in enemys:
            if pg.sprite.collide_rect(self, enemy):
                #self.obj_manager.log(f"{type(self.owner).__name__}{self.owner.rect} attacked {type(enemy).__name__}{enemy.rect}")
                enemy.got_attacked(self.owner, self.damage)
                self.already_attacked.add(enemy)
                #enemy.collide(player, keys)
            #else:
                #zone.no_collide(player)

"""class HitBox(pg.rect.Rect):
    def __init__(self, owner, center, wh):
        lefttop = (center[0] - wh[0], center[1] + wh[1])
        pg.rect.Rect.__init__(self, lefttop[0], lefttop[1], wh[0], wh[1])

        self.owner = owner

    def set_center(self, xy):
        self.center = xy"""