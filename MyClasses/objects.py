import pygame as pg
from MyClasses.special_classes import InteractiveBox, InteractiveWidget, ProgressBar, HitZone
from MyClasses.player import Player
from random import randint as rand
from settings import *


class DroppedItem(pg.sprite.Sprite):
    def __init__(self, x, y, costumes, func_when_die, obj_manager):
        pg.sprite.Sprite.__init__(self)
        self.costumes = costumes
        self.image = self.costumes[0]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        self.costumeNumber = 0.0
        self.anim_time = 1
        self.isOneFrame = len(costumes) == 1

        self.obj_manager = obj_manager

        self.interact_zone = InteractiveBox(self, self.rect.center, 50, 50, (pg.K_e, pg.K_q), (pg.K_e,))
        self.interact_widget = None
        self.func_when_die = func_when_die

    def update(self, **kwargs):
        if not self.isOneFrame:
            if self.costumeNumber < len(self.costumes) - 1:
                self.costumeNumber += kwargs["dtime"] * len(self.costumes) / self.anim_time
            else:
                self.costumeNumber = 0
            self.image = self.costumes[int(self.costumeNumber) % (len(self.costumes))]

        self.draw(kwargs["surf"])

    def draw(self, surf):
        surf.blit(self.image, self.rect)
        if self.interact_widget:
            surf.blit(self.interact_widget, self.interact_widget.rect)

    def get_info(self):
        return {"Center": self.rect.center, "Frame": int(self.costumeNumber) % (len(self.costumes))}

    def get_interzone(self):
        return self.interact_zone

    def interact(self, player: Player, keys):
        self.func_when_die(self)
        self.obj_manager.log(f"{Player} interacted with {self}")
        self.kill()

    def when_player_in_zone(self, player: Player):
        if self.interact_widget:
            pass
        else:
            self.interact_widget = InteractiveWidget(self.rect.center, 100, 40)



    def when_player_leave_zone(self, player):
        self.interact_widget = None

    def got_attacked(self, source, damage):
        self.obj_manager.log(f"this bro({source}) rly trying to kill dropped item😂💀")


class Entity(pg.sprite.Sprite):
    def __init__(self, start_pos: tuple, speed: int, max_hp, hp,  animations, obj_manager):
        pg.sprite.Sprite.__init__(self)

        self.obj_manager = obj_manager

        self.action_to_animation = {"Nothing": "Idle",
                                    "Walk": "Walk",
                                    "Run": "Walk",
                                    "Attack": "Attack"}
        self.action = "Nothing"
        self.animation = self.action_to_animation[self.action]
        self.animations = animations

        self.frame = 0
        self.frame_delay = 0.2

        self.sprite = self.animations[self.action_to_animation[self.action]][self.frame]
        self.mask = pg.mask.from_surface(self.sprite)
        self.rect = self.sprite.get_rect()
        self.rect.center = start_pos

        self.speed = speed

        self.max_hp = max_hp
        self.hp = hp

        self.health_bar = ProgressBar(self, (0, -10), (100, 15), int(hp / max_hp * 100), RED, GREEN)

        self.money = 0

        self.direction_r = True

        self.hit_zone = False

    def get_info(self):
        return {"Center": self.rect.center,
                "HP": self.hp,
                "Speed": self.speed,
                "Money": self.money,
                "Action": self.action,
                "Animation": self.action_to_animation[self.action] + " " + str(int(1 / self.frame_delay)) +"x",
                "Frame": int(self.frame / self.frame_delay),
                "Direction": ("Left", "Right")[int(self.direction_r)]}

    def update_object(self, **kwargs):
        self.movement(kwargs["W"], kwargs["H"], kwargs["dtime"])
        self.animate(kwargs["dtime"])

    def draw(self, surf: pg.surface.Surface):
        if self.direction_r:
            pg.draw.rect(self.sprite, (255, 0, 0), (0, 0, self.rect.right - self.rect.left, self.rect.bottom - self.rect.top), 2)
            surf.blit(self.sprite, self.rect)
        else:
            surf.blit(pg.transform.flip(self.sprite.convert_alpha(), True, False), self.rect)
        self.health_bar.draw(surf)
        if self.hit_zone:
            surf.blit(self.hit_zone, self.hit_zone.rect_for_pl)

    def animate(self, dt):
        if self.action == "Attack":
            if (self.frame <= 0.4 or not self.hit_zone) and self.frame >= 0.1:
                self.start_attacking()
            if self.hit_zone: self.hit_zone.check_collide()
        self.frame += dt

        if self.frame / self.frame_delay >= len(self.animations[self.action_to_animation[self.action]]):
            if self.action == "Attack":
                self.stop_attacking()
                self.frame_delay = 0.2
                self.action = "Nothing"
            self.frame = 0
        self.sprite = self.animations[self.action_to_animation[self.action]][int(self.frame / self.frame_delay)]
        if self.direction_r:
            self.mask = pg.mask.from_surface(self.sprite)
        else:
            self.mask = pg.mask.from_surface(pg.transform.flip(self.sprite.convert_alpha(), True, False))

    def start_attacking(self):
        if not self.hit_zone:
            if self.direction_r:
                self.hit_zone = HitZone(self, (self.rect.centerx, self.rect.top), (94, 110), 5, self.obj_manager)
            else:
                self.hit_zone = HitZone(self, (self.rect.centerx - 94, self.rect.top), (94, 110), 5, self.obj_manager)
            self.hit_zone.fill((250, 100, 100))

    def stop_attacking(self):
        self.hit_zone = False

    def add_hp(self, n: int, canExceedMaxHP=False):
        if canExceedMaxHP:
            self.hp += n
        elif self.hp < self.max_hp:
            self.hp = min(self.max_hp, self.hp + n)

        if self.hp < 0:
            self.hp = -1
            self.die()
        self.health_bar.update(int(self.hp / self.max_hp * 100))

    def movement(self, w, h, dt):
        if self.action == "Attack": return

    def got_attacked(self, source, damage):
        self.add_hp(-damage)
        self.stop_attacking()
        self.frame = 0
        self.action = "Attack"

    def die(self):
        self.hp = 999999999
        self.obj_manager.log(f"RIP {self}")


class Storage(pg.sprite.Sprite):
    pass


class LootBox(pg.sprite.Sprite):
    def __init__(self, x, y, costumes, func_when_die, obj_manager):
        pg.sprite.Sprite.__init__(self)
        self.costumes = costumes
        self.costumeNumber = 0
        self.image = self.costumes[0]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        self.obj_manager = obj_manager

        self.func_when_die = func_when_die

    def update_object(self, **kwargs):
        self.image = self.costumes[int(self.costumeNumber)]
        self.draw(kwargs["surf"])

    def draw(self, surf):
        surf.blit(self.image, self.rect)

    def get_info(self):
        return {"Center": self.rect.center, "Frame": int(self.costumeNumber)}

    def got_attacked(self, source, damage):
        self.obj_manager.log(f"{type(source).__name__}{source.rect} looted LootBox{self.rect}")
        self.costumeNumber = 0
        self.summon_loot(damage)
        self.kill()

    def summon_loot(self, luck):
        #global coin_textures, CoinsGroup, objManager, pl1, new_coin
        print(int(luck // 2 ), int(luck // 1.2))
        for _ in range(0, rand(int(luck // 2 ), int(luck // 1.2)), 2):
            #new_c = DroppedIte(rand(self.rect.left, self.rect.right), rand(self.rect.top, self.rect.bottom), coin_textures,
            #                    lambda x: (new_coin(), pl1.add_money(1)), objManager)
            #CoinsGroup.add(new_c)
            self.func_when_die(rand(self.rect.left, self.rect.right), rand(self.rect.top, self.rect.bottom))


