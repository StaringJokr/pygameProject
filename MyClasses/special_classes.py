import pygame as pg
from settings import *

class InteractiveBox(pg.Surface):
    def __init__(self, owner, center, width, height, interact_keys: tuple, can_hold=()):
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


    def draw(self, surf):
        surf.blit(self, (self.owner.rect.center[0] + self.dx - self.width // 2, self.owner.rect.top + self.dy))

class HitZone(pg.Surface):
    def __init__(self, owner, pos, wh, damage, obj_manager):
        width, height = wh
        pg.Surface.__init__(self, (width, height))
        self.rect = self.get_rect()
        self.rect.topleft = pos

        self.damage = damage

        self.already_attacked = set()

        self.mask = pg.mask.from_surface(self)
        self.owner = owner
        self.obj_manager = obj_manager

    def check_collide(self):
        enemys = set(self.obj_manager.get_all()) - set((self.owner, )) - self.already_attacked
        #self.rect = self.get_rect(topleft=(self.rect_for_pl[0], self.rect_for_pl[1]))

        for enemy in enemys:
            if pg.sprite.spritecollide(self, [enemy], False, collide_mask_rect):
                #self.obj_manager.log(f"{type(self.owner).__name__}{self.owner.rect} attacked {type(enemy).__name__}{enemy.rect}")
                enemy.got_attacked(self.owner, self.damage)
                self.already_attacked.add(enemy)


def collide_mask_rect(left, right):
    xoffset = right.rect[0] - left.rect[0]
    yoffset = right.rect[1] - left.rect[1]
    try:
        leftmask = left.mask
    except AttributeError:
        leftmask = pg.mask.Mask(left.rect.size, True)
    try:
        rightmask = right.mask
    except AttributeError:
        rightmask = pg.mask.Mask(right.rect.size, True)
    return leftmask.overlap(rightmask, (xoffset, yoffset))


class InventoryWidget(pg.surface.Surface):
    def __init__(self, owner, center, storage_list, name, name_size,
                 cell_size, offset, interval,
                 name_color=(255, 222, 6), cell_color=(192, 192, 192), bg_color=(30, 30, 30)):
        self.name = pg.font.SysFont("freesansbold.ttf", name_size).render(name, True, name_color)
        pg.surface.Surface.__init__(self, (offset * 2 + len(storage_list[0]) * (cell_size + interval) - interval,
                                           self.name.get_size()[1] + offset * 2 + len(storage_list) * (cell_size + interval) - interval))
        self.rect = self.get_rect()
        self.rect.center = center
        self.columns, self.strokes, = len(storage_list), len(storage_list[0])

        self.storage = storage_list

        self.cell_size = cell_size
        self.c_offset = offset
        self.c_interval = interval

        self.colors = (name_color, cell_color, bg_color)

        self.obj_manager = owner.obj_manager

    def update(self):
        self.fill(self.colors[2])
        self.blit(self.name, self.name.get_rect())
        for yi in range(self.columns):
            for xi in range(self.strokes):
                pg.draw.rect(self, self.colors[1], (self.c_offset + (self.cell_size + self.c_interval) * xi,
                                                    self.name.get_size()[1] + self.c_offset + (self.cell_size + self.c_interval) * yi,
                                                    self.cell_size, self.cell_size))
                if self.storage[yi][xi]:
                    pg.draw.rect(self, (255, 0, 0), (self.c_offset + (self.cell_size + self.c_interval) * xi,
                                                        self.name.get_size()[1] + self.c_offset + (self.cell_size + self.c_interval) * yi,
                                                        self.cell_size, self.cell_size))

    def draw(self):
        self.obj_manager.add_gui(self)
