import logging
import os
import pygame as pg
from typing import Union, List, Dict, Tuple
from settings import DATA_FOLDER, SCREEN_RESOLUTION

logger = logging.getLogger(__name__)

main_dir: Union[str, bytes] = os.path.split(os.path.abspath(__file__))[0]


def load_image(name):
    path = os.path.join(main_dir, DATA_FOLDER, name)
    return pg.image.load(path).convert()


class ClockFace:
    def __init__(self, digits_dir: str):
        self.points_int: int = 0
        digits_path = os.path.join(main_dir, DATA_FOLDER, digits_dir)
        digits_files = sorted([os.path.join(digits_path, file) for file in os.listdir(digits_path)
                               if os.path.isfile(os.path.join(digits_path, file))])
        digits_images: List[pg.Surface] = [pg.image.load(file).convert_alpha() for file in digits_files]
        self.digits: Dict = dict(zip([x for x in range(10)], digits_images))
        logger.debug('digits collection: %s', self.digits)

    def add_points(self, points: int):
        self.points_int += points

    def reset_points(self):
        self.points_int = 0

    def get_digits_representation(self) -> List[Tuple]:
        representation: List = [self.digits[int(c)] for c in str(self.points_int)]

        # every image has to be 60x100 resolution
        start_x_pos: int = 460
        y_pos = 305
        coordinates: List[Tuple[int, int]] = [(start_x_pos + x*60, y_pos) for x in range(len(representation))]
        return list(zip(representation, coordinates))


class PointImage:
    def __init__(self, filename, fading_length: int = 100):
        self.image = load_image(filename)
        self.position = (420, 50)  # (x, y)
        self.max_fading_length = fading_length
        self.fading_phase = 0
        self.activated = False

    def need_to_draw(self):
        if not self.activated:
            return False

        if self.fading_phase < self.max_fading_length:
            self.fading_phase += 1
            return True
        self.activated = False
        self.fading_phase = 0
        return False


class Particle:
    def __init__(self, filename):
        self.image = load_image(filename)
        self.pos = self.image.get_rect()


class ClockFrame:
    def __init__(self, filename):
        path = os.path.join(main_dir, DATA_FOLDER, filename)
        self.image = pg.transform.scale(pg.image.load(path).convert(), (200, 130))
        self.position = (440, 290)


class Background:
    def __init__(self, background_dir):
        self.images: List = []
        background_path: str = os.path.join(main_dir, DATA_FOLDER, background_dir)
        images_files_len: int = len([file for file in os.listdir(background_path)
                                     if os.path.isfile(os.path.join(background_path, file))])

        for i in range(images_files_len):
            file: str = os.path.join(background_path, f'background-{i}.png')
            self.images.append(pg.transform.scale(pg.image.load(file).convert(), SCREEN_RESOLUTION))

        self.counter: int = -1
        self.frame_counter: int = 0

    def __iter__(self):
        return self

    def __next__(self):
        self.frame_counter += 1
        if self.frame_counter == 10:
            self.frame_counter = 0
            self.counter += 1
            if self.counter == len(self.images):
                self.counter = 0
        return self.images[self.counter]
