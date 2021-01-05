import os
import pygame
from settings import DATA_FOLDER, MAIN_DIR


class Image:
    def __init__(self):
        self.image = None

    def load_image(self, name):
        path = os.path.join(MAIN_DIR, DATA_FOLDER, name)
        self.image = pygame.image.load(path).convert()


class PointImage(Image):
    def __init__(self, filename, fading_length: int = 100):
        super().__init__()
        self.load_image(filename)
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


class Particle(Image):
    def __init__(self, filename):
        super().__init__()
        self.load_image(filename)
        self.pos = self.image.get_rect()
