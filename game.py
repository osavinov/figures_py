import logging
import os
from datetime import datetime
from typing import Tuple, List

import pygame as pg

from field import Field
from figuresfactory import FiguresFactory
from images import Background, Particle, PointImage, ClockFace, ClockFrame

logger = logging.getLogger(__name__)


class GameLevel:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((640, 480))
        pg.display.set_caption("CRINGEtris v.0.1")
        self.field_v_size = 20
        self.field_h_size = 15

        self.background_images: Background = Background("bottle")
        self.points_clock_face: ClockFace = ClockFace("digits")
        self.clock_images_representation: List[Tuple] = self.points_clock_face.get_digits_representation()
        self.clock_frame: ClockFrame = ClockFrame("frame.png")
        self.particle: Particle = Particle("obstacle.bmp")
        self.get_point: PointImage = PointImage("point.png")

        self.screen.blit(next(self.background_images), (0, 0))

        self.field = Field(self.field_v_size, self.field_h_size)
        self.figures_factory = FiguresFactory(self.field.x_size)

        self.move_counter = 0

    def update_field(self) -> bool:
        self.move_counter += 1
        logger.debug(f"------- move_counter={self.move_counter}")
        current_figure = self.figures_factory.get_figure()
        figure_moves_counter = 0
        stop_moving_current_figure: bool = False  # current_figure have to stop due to field collision
        just_rotated: bool = False  # flag for force redrawing the field during success rotation attempt
        while not stop_moving_current_figure:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_LEFT:
                        logger.debug("PRESSED BUTTON K_LEFT")
                        self.field.try_to_move_horizontally(current_figure, -1)
                    elif event.key == pg.K_RIGHT:
                        logger.debug("PRESSED BUTTON K_RIGHT")
                        self.field.try_to_move_horizontally(current_figure, 1)
                    elif event.key == pg.K_SPACE:
                        logger.debug("PRESSED BUTTON K_SPACE")
                        just_rotated = self.field.try_to_rotate_figure(current_figure)
                        logger.debug(f"after_rotate_attempt: {current_figure}")
                    elif event.key == pg.K_ESCAPE:
                        logger.debug("PRESSED BUTTON K_ESC")
                        return False
            is_bottom_intersection, redraw_rotation = self.field.try_to_move_vertically(current_figure, 1, just_rotated)
            stop_moving_current_figure, points = self.field.overlay(current_figure, is_bottom_intersection,
                                                                    redraw_rotation)
            if points != 0:
                logger.debug("Getting new game points!")
                self.points_clock_face.add_points(points)
                self.get_point.activated = True
                self.clock_images_representation = self.points_clock_face.get_digits_representation()

            self.draw_field()

            if not stop_moving_current_figure:
                pg.time.wait(100)

            if stop_moving_current_figure and figure_moves_counter == 0 and self.field.is_almost_filled():
                return False
            figure_moves_counter += 1
            logger.debug(f"figure={current_figure}, figure_moves_counter={figure_moves_counter}")
        return True

    def draw_field(self):
        cell_x_size: int = 20
        cell_y_size: int = 20
        logger.debug("=" * (len(self.field.current_frame[0]) + 2))
        for line in self.field.current_frame:
            logger.debug("|" + ("".join([str(x) for x in line])).replace("0", " ").replace("1", "#") + "|")
        logger.debug("=" * (len(self.field.current_frame[0]) + 2))

        # draw background
        background_image = next(self.background_images)
        self.screen.blit(background_image, (0, 0))

        # draw the field
        for row_num in range(self.field_v_size):
            for elem_num in range(self.field_h_size):
                if self.field.current_frame[row_num][elem_num] == 1:
                    self.screen.blit(self.particle.image, (cell_y_size * elem_num, cell_x_size * row_num))

        if self.get_point.need_to_draw():  # draw image for new points get
            self.screen.blit(self.get_point.image, self.get_point.position)

        self.screen.blit(self.clock_frame.image, self.clock_frame.position)  # draw clocks frame
        for digit_record in self.clock_images_representation:  # draw digits into frame
            self.screen.blit(digit_record[0], digit_record[1])

        pg.display.update()
        logger.debug("+++++++++++++++++++++++++++++++++++++++")


def main():
    root_dir: str = os.path.split(os.path.abspath(__file__))[0]
    log_filename = datetime.utcnow().isoformat().replace("-", "").replace(":", "")[:15]
    logging.basicConfig(filename=os.path.join(root_dir, "logs", f"{log_filename}.log"), level=logging.DEBUG,
                        format="%(asctime)s - %(levelname)s - %(filename)s.%(funcName)s: %(message)s")
    game = GameLevel()
    while game.update_field():
        pass


if __name__ == "__main__":
    main()
