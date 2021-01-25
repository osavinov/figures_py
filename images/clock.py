import logging
import os
import pygame
from typing import List, Dict, Tuple
from settings import DATA_FOLDER, MAIN_DIR

logger = logging.getLogger(__name__)


class ClockFrame:
    def __init__(self, filename):
        path = os.path.join(MAIN_DIR, DATA_FOLDER, filename)
        self.image = pygame.transform.scale(
            pygame.image.load(path).convert(), (200, 130),
        )
        self.position = (440, 290)


class ClockFace:
    def __init__(self, digits_dir: str):
        self.points_int: int = 0
        digits_path = os.path.join(MAIN_DIR, DATA_FOLDER, digits_dir)
        digits_files = sorted(
            [
                os.path.join(digits_path, file)
                for file in os.listdir(digits_path)
                if os.path.isfile(os.path.join(digits_path, file))
            ],
        )
        digits_images: List[pygame.Surface] = [
            pygame.image.load(file).convert_alpha() for file in digits_files
        ]
        self.digits: Dict = dict(zip([x for x in range(10)], digits_images))
        logger.debug('digits collection: %s', self.digits)

    def add_points(self, points: int):
        self.points_int += points

    def reset_points(self):
        self.points_int = 0

    def get_points(self) -> int:
        return self.points_int

    def get_digits_representation(self) -> List[Tuple]:
        representation: List = [
            self.digits[int(c)] for c in str(self.points_int)
        ]

        # every image has to be 60x100 resolution
        start_x_pos: int = 460
        y_pos = 305
        coordinates: List[Tuple[int, int]] = [
            (start_x_pos + x * 60, y_pos) for x in range(len(representation))
        ]
        return list(zip(representation, coordinates))
