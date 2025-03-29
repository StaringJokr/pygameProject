import pygame as pg
from json import load as json_load
from json import dump as json_dump
from tkinter import filedialog
from settings import *

class ObjectManager:
    def __init__(self, logfile_name, name="Unnamed"):
        self.all_objects = set()
        self.name = name
        self.len = 0
        self.logfile_name = logfile_name
        self.logs = []

    def get_all(self):
        return self.all_objects

    def get_all_of_class(self, classname):
        return [obj for obj in self.all_objects if type(obj) == classname]

    def add(self, obj):
        self.all_objects.add(obj)
        self.len += 1

    def remove(self, obj):
        self.all_objects.remove(obj)
        self.len -= 1

    def add_many(self, objs):
        self.all_objects.update(objs)
        self.len = len(self.all_objects)

    def log(self, message, printing=True, saveToFile=True):
        if printing:    print(message)
        if saveToFile:  self.logs.append(str(round(pg.time.get_ticks() / 1000, 3)) + " " + message + "\n")

    def stop_game(self):
        with open(self.logfile_name, "w", encoding="utf-8") as file:
            file.writelines(self.logs)

    def new_obj(self, obj):
        self.add(obj)
        return self


class Info(pg.Surface):
    """
    For
    """
    def __init__(self):
        pg.Surface.__init__(self, (250, 380))
        self.fill(DARKGRAY)
        self.current = self
        self.font0 = pg.font.SysFont("freesansbold.ttf", 50)
        self.font1 = pg.font.SysFont("freesansbold.ttf", 36)
        self.text = self.font0.render(type(self.current).__name__, True, (230, 100, 100))
        self.details = self.font1.render(str(self.current.get_info()), True, SKYBLUE)
        self.hide = False
        # self.text.get_rect().center = (10, 20)

    def update_info(self):
        self.fill(DARKGRAY)
        # self.text = self.font0.render(type(self.current).__name__, True, (230, 100, 100))
        # self.details = self.font1.render(str(self.current.get_info()), True, (230, 100, 100))
        self.blit_text(type(self.current).__name__, (0, 0), self.font0, (230, 100, 100))
        details = ""
        for k, b in self.current.get_info().items():
            details += f"{k}: {b}\n"
        self.blit_text(details, (0, 40), self.font1, SKYBLUE)

    def blit_text(self, text, pos, font, color):
        words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.
        space = font.size(' ')[0]  # The width of a space.
        max_width, max_height = self.get_size()
        x, y = pos
        for line in words:
            for word in line:
                word_surface = font.render(word, 0, color)
                word_width, word_height = word_surface.get_size()
                if x + word_width >= max_width:
                    x = pos[0]  # Reset the x.
                    y += word_height  # Start on new row.
                self.blit(word_surface, (x, y))
                x += word_width + space
            x = pos[0]  # Reset the x.
            y += word_height  # Start on new row.

    def set_current(self, obj):
        self.current = obj
        print(type(self.current).__name__)

    def get_info(self):
        return {"Swaga": "prisutsvuet"}


class SaveManager:
    def __init__(self):
        pass

    def load(self, file_path=False):
        if not file_path:
            file_path = filedialog.askopenfile(filetypes=[('JSON Files', '*.json'), ('All Files', '*.*')])
        if not file_path: exit()

        self.data = json_load(file_path)

    def save(self, player, c_group, h_group, lb_group, e_group, file_path="save0.json"):
        if not file_path:
            file_path = filedialog.asksaveasfilename(filetypes=[('JSON Files', '*.json'), ('All Files', '*.*')])
            if not file_path:
                return
            if file_path[len(file_path)-5:] != ".json":
                file_path += ".json"


        data = {
                "player": {},
                "CoinsGroup": {},
                "HealkasGroup": {},
                "LootBoxesGroup": {},
                "EntityGroup": {}
                }
        pldat = dict()
        pldat["pos"] = {"x": player.rect.x, "y": player.rect.y}
        pldat["action"] = player.action
        pldat["animation"] = player.animation
        pldat["frame"] = player.frame
        pldat["frame_delay"] = player.frame_delay
        pldat["direction_r"] = player.direction_r
        pldat["properties"] = {"speed": player.speed,
                               "max_hp": player.max_hp,
                               "hp": player.hp,
                               "money": player.money,
                               "max_stamina": player.max_stamina,
                               "stamina": player.stamina,
                               "run_boost": player.run_boost,
                               "restamina_per_second": player.restamina_per_second
                                }
        pldat["isHitzone"] = False
        #if player.hit_zone:
         #   pldat["isHitzone"] = True
        data["player"] = pldat

        cgroup = {"x": [], "y": [], "inf": []}
        for c in c_group:
            cgroup["x"].append(c.rect.centerx)
            cgroup["y"].append(c.rect.centery)
            cgroup["inf"].append(c.inf)
        data["CoinsGroup"] = cgroup

        hgroup = {"x": [], "y": [], "inf": []}
        for h in h_group:
            hgroup["x"].append(h.rect.centerx)
            hgroup["y"].append(h.rect.centery)
            hgroup["inf"].append(h.inf)
        data["HealkasGroup"] = hgroup

        lbgroup = {"x": [], "y": [], "inf": []}
        for lb in lb_group:
            lbgroup["x"].append(lb.rect.centerx)
            lbgroup["y"].append(lb.rect.centery)
            lbgroup["inf"].append(lb.inf)
        data["LootBoxesGroup"] = lbgroup

        egroup = []
        for en in e_group:
            edat = dict()
            edat["pos"] = {"x": en.rect.centerx, "y": en.rect.centery}
            edat["action"] = en.action
            edat["animation"] = en.animation
            edat["frame"] = en.frame
            edat["frame_delay"] = en.frame_delay
            edat["direction_r"] = en.direction_r
            edat["money"] = en.money
            edat["properties"] = {"speed": en.speed,
                                   "max_hp": en.max_hp,
                                   "hp": en.hp,
                                  }
            egroup.append(edat)
            data["EntityGroup"] = egroup

        with open(file_path, 'w', encoding='utf-8') as f:
            json_dump(data, f, ensure_ascii=False, indent=4)

    def player(self, class_name, textures, obj_manager):
        pl_data = self.data["player"]
        pos = pl_data["pos"]
        return class_name((pos["x"], pos["y"]), pl_data["properties"], pl_data["action"], pl_data["animation"],
                          pl_data["frame"], pl_data["frame_delay"], pl_data["direction_r"], textures, obj_manager)

    def drops(self, summon_func, drop_type):
        if drop_type == "coin":
            c_data = self.data["CoinsGroup"]
        elif drop_type == "healka":
            c_data = self.data["HealkasGroup"]

        for i in range(len(c_data.get("x", []))):
            summon_func(c_data["x"][i], c_data["y"][i], c_data["inf"][i])

    def loot_boxes(self, class_summon, costumes, summon_loot_func, obj_manager, group):
        l_data = self.data["LootBoxesGroup"]

        for i in range(len(l_data.get("x", []))):
            class_summon(l_data["x"][i], l_data["y"][i], costumes, summon_loot_func, obj_manager, group, l_data["inf"][i])

    def entities(self, class_summon, costumes, obj_manager, group):
        e_data = self.data["EntityGroup"]

        for en in e_data:
            class_summon((en["pos"]["x"], en["pos"]["y"]), en["properties"],
                         en["action"], en["animation"], en["frame"], en["frame_delay"],
                         en["direction_r"], costumes, obj_manager, group)