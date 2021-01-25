import os
import pygame
from typing import List
from settings import DATA_FOLDER, SCREEN_RESOLUTION, MAIN_DIR


class Background:
    def __init__(self, background_dir):
        self.images: List = []
        background_path: str = os.path.join(
            MAIN_DIR, DATA_FOLDER, background_dir,
        )
        images_files_len: int = len(
            [
                file
                for file in os.listdir(background_path)
                if os.path.isfile(os.path.join(background_path, file))
            ],
        )

        for i in range(images_files_len):
            file: str = os.path.join(background_path, f'background-{i}.png')
            self.images.append(
                pygame.transform.scale(
                    pygame.image.load(file).convert(), SCREEN_RESOLUTION,
                ),
            )

        self.counter: int = -1
        self.frame_counter: int = 0

    def __iter__(self):
        return self

    def __next__(self):
        self.frame_counter += 1
        if self.frame_counter == 5:
            self.frame_counter = 0
            self.counter += 1
            if self.counter == len(self.images):
                self.counter = 0
        return self.images[self.counter]
