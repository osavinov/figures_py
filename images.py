import os
from os import listdir
from os.path import isfile, join

import pygame as pg
from typing import Union, List

main_dir: Union[str, bytes] = os.path.split(os.path.abspath(__file__))[0]


def load_image(name):
    path = os.path.join(main_dir, "data", name)
    return pg.image.load(path).convert()


class Particle:
    def __init__(self, filename):
        self.image = load_image(filename)
        self.pos = self.image.get_rect()


class Background:
    def __init__(self, background_dir):
        background_path = os.path.join(main_dir, "data", background_dir)
        background_files = [os.path.join(background_path, file) for file in listdir(background_path)
                            if isfile(join(background_path, file))]
        self.images: List = [pg.transform.scale(pg.image.load(file).convert(), (640, 400)) for file in background_files]
        self.counter: int = -1

    def __iter__(self):
        return self

    def __next__(self):
        self.counter += 1
        if self.counter == len(self.images):
            self.counter = 0
        return self.images[self.counter]
