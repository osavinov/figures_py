import logging
import os
import pygame
from datetime import datetime
from typing import Tuple, List

from field import Field
from figure import Figure
from figuresfactory import FiguresFactory
from images import Background, Particle, PointImage, ClockFace, ClockFrame
from settings import SCREEN_RESOLUTION, WINDOWS_CAPTION, SPEED_LEVELS, MENU_FONT_NAME, MENU_FONT_SIZE

logger = logging.getLogger(__name__)


class GameLevel:
    def __init__(self):
        # init pygame parameters
        pygame.init()
        self.screen: pygame.Surface = pygame.display.set_mode(
            size=SCREEN_RESOLUTION,
        )
        pygame.display.set_caption(WINDOWS_CAPTION)
        pygame.font.init()
        self.menu_font: pygame.font.Font = pygame.font.SysFont(
            name=MENU_FONT_NAME,
            size=MENU_FONT_SIZE,
        )

        self.field_v_size: int = 20
        self.field_h_size: int = 10
        self.background_images: Background = Background('bottle')
        self.points_clock_face: ClockFace = ClockFace('digits')
        self.clock_images_representation: List[Tuple] = self.points_clock_face.get_digits_representation()
        self.clock_frame: ClockFrame = ClockFrame('frame.png')
        self.particle: Particle = Particle('obstacle.bmp')
        self.get_point: PointImage = PointImage('point.png')

        self.screen.blit(next(self.background_images), (0, 0))

        self.field = Field(self.field_v_size, self.field_h_size)
        self.figures_factory = FiguresFactory(self.field.x_size)

        self.move_counter: int = 0
        self.frame_counter: int = 0
        self.level: int = 1

        self.pause: bool = False

    # returns False if it's possible to stop updating
    def update_field(self) -> bool:
        self.move_counter += 1
        logger.debug('------- move_counter=%d', self.move_counter)
        current_figure: Figure = self.figures_factory.get_figure()
        figure_moves_counter = 0
        stop_moving_current_figure: bool = False  # current_figure have to stop due to field collision
        just_rotated: bool = False  # flag for force redrawing the field during success rotation attempt

        while not stop_moving_current_figure:
            self.frame_counter += 1

            # process events queue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    logger.debug('Exit game!')
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # special event pause
                        logger.debug('PRESSED BUTTON K_ESC')
                        if self.pause:
                            self.pause = False
                            logger.debug('Pause mode was disabled')
                        else:
                            self.pause = True
                            logger.debug('Pause mode was enabled')
                    elif not self.pause:
                        if event.key == pygame.K_LEFT:
                            logger.debug('PRESSED BUTTON K_LEFT')
                            self.field.try_to_move_horizontally(current_figure, -1)
                        elif event.key == pygame.K_RIGHT:
                            logger.debug('PRESSED BUTTON K_RIGHT')
                            self.field.try_to_move_horizontally(current_figure, 1)
                        elif event.key == pygame.K_SPACE:
                            logger.debug('PRESSED BUTTON K_SPACE')
                            just_rotated = self.field.try_to_rotate_figure(current_figure)
                            logger.debug('after_rotate_attempt: %s', current_figure)
            if self.pause:
                self.draw_pause_menu_screen()
            else:
                stop_moving_current_figure = self.render_current_figure_movement(
                    current_figure,
                    just_rotated,
                )

                self.draw_field()

                if self.level == len(SPEED_LEVELS)-1:
                    logger.debug('Player was reached the highest speed level!')
                    return False

                pygame.time.wait(SPEED_LEVELS[self.level])

                if stop_moving_current_figure and figure_moves_counter == 0 and self.field.is_almost_filled():
                    logger.debug('Field is almost filled: exit game!')
                    return False
                figure_moves_counter += 1
                logger.debug('figure=%s, figure_moves_counter=%d', current_figure, figure_moves_counter)
        return True

    def render_current_figure_movement(self, current_figure, just_rotated):
        is_bottom_intersection, redraw_rotation = self.field.try_to_move_vertically(
            figure=current_figure,
            shift=1,
            just_rotated=just_rotated,
        )
        stop_moving_current_figure, points = self.field.overlay(
            figure=current_figure,
            is_bottom_intersection=is_bottom_intersection,
            redraw_rotation=redraw_rotation,
        )
        if points != 0:
            logger.debug('Getting new game points!')
            self.points_clock_face.add_points(points)
            self.get_point.activated = True
            self.clock_images_representation = self.points_clock_face.get_digits_representation()
            self.level = self.points_clock_face.points_int // 10
        return stop_moving_current_figure

    def draw_field(self):
        cell_x_size: int = 20
        cell_y_size: int = 20
        logger.debug('=' * (len(self.field.current_frame[0]) + 2))
        for line in self.field.current_frame:
            logger.debug('|' + (''.join([str(x) for x in line])).replace('0', ' ').replace('1', '#') + '|')
        logger.debug('=' * (len(self.field.current_frame[0]) + 2))

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

        pygame.display.update()
        logger.debug('+++++++++++++++++++++++++++++++++++++++')

    def draw_pause_menu_screen(self):
        menu_caption: pygame.Surface = self.menu_font.render(
            'ПОСОСИТЕ ГОВНА',
            False,
            (0, 0, 0),
        )
        self.screen.blit(menu_caption, (0, 0))
        pygame.display.update()


def main():
    root_dir: str = os.path.split(os.path.abspath(__file__))[0]
    logs_dir: str = os.path.join(root_dir, 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    log_filename = datetime.utcnow().isoformat().replace('-', '').replace(':', '')[:15]
    logging.basicConfig(
        filename=os.path.join(logs_dir, f'{log_filename}.log'),
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(filename)s.%(funcName)s: %(message)s',
    )
    game = GameLevel()
    while game.update_field():
        pass


if __name__ == '__main__':
    main()
