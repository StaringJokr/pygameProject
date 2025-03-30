import pygame as pg
from settings import *
from MyClasses.special_classes import HitZone, ProgressBar

class Player(pg.sprite.Sprite):
    """
    class PLayer
    args:
        start_pos - position of center
        speed o_o
        filename  - path to texture of player
    """
    def __init__(self, start_pos: tuple, properties: dict, action, animation, frame, fd, dire_r, animations, obj_manager):
        pg.sprite.Sprite.__init__(self)

        self.obj_manager = obj_manager.new_obj(self)

        self.action_to_animation = {"Nothing": "Idle",
                                    "Walk": "Walk",
                                    "Run": "Walk",
                                    "Attack": "Attack"}
        self.action = action
        self.animation = animation
        self.animations = animations

        self.frame = frame
        self.frame_delay = fd #0.2

        self.sprite = self.animations[self.action_to_animation[self.action]][int(self.frame / self.frame_delay)]
        self.mask = pg.mask.from_surface(self.sprite)
        self.rect = self.sprite.get_rect()
        self.rect.center = start_pos

        self.speed = properties.get("speed", 400)
        self.max_stamina = properties.get("max_stamina", 30.0)
        self.stamina = properties.get("stamina", self.max_stamina)
        self.run_boost = properties.get("run_boost", 1.6)
        self.restamina_per_second = properties.get("restamina_per_second", 8)
        self.money = properties.get("money", 0)
        self.max_hp = properties.get("max_hp", 100)
        self.hp = properties.get("hp", self.max_hp)

        self.health_bar = ProgressBar(self, (0, -10), (100, 15), int(self.hp / self.max_hp * 100), RED, GREEN)

        self.direction_r = dire_r

        self.hit_zone = False


    def get_info(self):
        return {"Center": self.rect.center,
                "HP": self.hp,
                "Speed": self.speed,
                "Stamina": round(self.stamina),
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
            surf.blit(self.sprite, self.rect)
        else:
            surf.blit(pg.transform.flip(self.sprite.convert_alpha(), True, False), self.rect)
        self.health_bar.draw(surf)
        if self.hit_zone:
            surf.blit(self.hit_zone, self.hit_zone.rect)

    def animate(self, dt):
        if self.action == "Attack":
            if not self.hit_zone and 0.2 >= self.frame >= 0.1:
                self.start_attacking()
            if self.hit_zone: self.hit_zone.check_collide()
        self.frame += dt

        if self.frame / self.frame_delay * 2 >= len(self.animations[self.action_to_animation[self.action]]) and self.action == "Attack":
            self.stop_attacking()

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
                self.hit_zone = HitZone(self, (self.rect.centerx, self.rect.top), (94, 110), 10, self.obj_manager)
            else:
                self.hit_zone = HitZone(self, (self.rect.centerx - 94, self.rect.top), (94, 110), 10, self.obj_manager)
            self.hit_zone.fill((200, 100, 100))

    def stop_attacking(self):
        self.hit_zone = False

    def set_money(self, n: int):
        self.money = n

    def get_money(self):
        return self.money

    def get_hp(self):
        return self.hp

    def add_money(self, n: int):
        self.money += n

    def add_hp(self, n: int, canExceedMaxHP=False):
        if canExceedMaxHP or n < 0:
            self.hp += n
        elif self.hp < self.max_hp:
            self.hp = min(self.max_hp, self.hp + n)


        if self.hp < 0:
            self.hp = -1
            self.die()
        self.health_bar.update(int(self.hp / self.max_hp * 100))

    def movement(self, w, h, dt):
        if self.action == "Attack": return
        keys = pg.key.get_pressed()

        ymove = 0
        xmove = 0
        cos_or_sin_45 = 1
        if keys[pg.K_a]: xmove += 1
        if keys[pg.K_d]: xmove -= 1
        if keys[pg.K_w]: ymove += 1
        if keys[pg.K_s]: ymove -= 1

        if xmove or ymove:
            self.action = "Walk"
            self.frame_delay = 0.1
            if xmove and ymove:
                cos_or_sin_45 = 0.8071
            if keys[pg.K_LSHIFT]:
                if self.stamina >= dt * 10:
                    self.action = "Run"
                    self.frame_delay = 0.07
                    self.stamina -= dt * 10
                    sp = int(self.speed * dt * self.run_boost)
                else:
                    sp = int(self.speed * dt)
            else:
                sp = int(self.speed * dt)
                self.stamina = min(self.max_stamina, self.stamina + self.restamina_per_second / 2 * dt)
        else:
            if self.action != "Attack":
                self.action = "Nothing"
                self.frame_delay = 0.2
            sp = int(self.speed * dt)
            self.stamina = min(self.max_stamina, self.stamina + self.restamina_per_second * dt)

        if xmove:
            if keys[pg.K_a]:
                self.rect.x -= int(sp * cos_or_sin_45)
                self.direction_r = False
            if keys[pg.K_d]:
                self.rect.x += int(sp * cos_or_sin_45)
                self.direction_r = True
        if ymove:
            if keys[pg.K_w]:
                self.rect.y -= int(sp * cos_or_sin_45)
            if keys[pg.K_s]:
                self.rect.y += int(sp * cos_or_sin_45)

        if self.rect.right - 33 > w:
            self.rect.right = w + 33
        if self.rect.left + 33 < 0:
            self.rect.left = -33
        if self.rect.top < -7:
            self.rect.top = -7
        if self.rect.bottom > h:
            self.rect.bottom = h

    def got_attacked(self, source, damage):
        print(f"Player: Ouch -{damage} hp! Stupid {type(source).__name__}")
        self.add_hp(-damage)

    def die(self):
        self.obj_manager.log(f"{type(self).__name__} died...")