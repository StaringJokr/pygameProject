import pygame as pg
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
        with open(self.logfile_name, "w") as file:
            file.writelines(self.logs)


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