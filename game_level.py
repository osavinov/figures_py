import logging
from datetime import datetime

import pygame
from typing import Tuple, List

from field import Field
from figure import Figure
from figuresfactory import FiguresFactory
from images.background import Background
from images.clock import ClockFace, ClockFrame
from images.particles import Particle, PointImage
from scores.scores import Scores
from settings import (
    SCREEN_RESOLUTION,
    WINDOWS_CAPTION,
    SPEED_LEVELS,
    MENU_FONT_SIZE,
    SPEED_LABEL_FONT_SIZE,
    SCORES_LABEL_FONT_SIZE,
    MAX_FPS,
)

logger = logging.getLogger(__name__)


class GameLevel:
    def __init__(self, current_user: str, scores: Scores):

        self.scores: Scores = scores

        # init pygame parameters
        pygame.init()
        self.screen: pygame.Surface = pygame.display.set_mode(
            size=SCREEN_RESOLUTION,
        )
        pygame.display.set_caption(WINDOWS_CAPTION)
        pygame.font.init()
        self.menu_font: pygame.font.Font = pygame.font.Font(
            None, MENU_FONT_SIZE,
        )
        self.speed_label_font: pygame.font.Font = pygame.font.Font(
            None, SPEED_LABEL_FONT_SIZE,
        )
        self.scores_label_font: pygame.font.Font = pygame.font.Font(
            None, SCORES_LABEL_FONT_SIZE,
        )
        self.start_screen_font: pygame.font.Font = pygame.font.Font(None, 48)
        self.clock: pygame.time.Clock = pygame.time.Clock()

        self.field_v_size: int = 20
        self.field_h_size: int = 10
        self.background_images: Background = Background('bottle')
        self.points_clock_face: ClockFace = ClockFace('digits')
        self.clock_images_representation: List[
            Tuple
        ] = self.points_clock_face.get_digits_representation()
        self.clock_frame: ClockFrame = ClockFrame('frame.png')
        self.particle: Particle = Particle('obstacle.bmp')
        self.get_point: PointImage = PointImage('point.png')

        self.screen.blit(next(self.background_images), (0, 0))

        self.field = Field(self.field_v_size, self.field_h_size)
        self.figures_factory = FiguresFactory(self.field.x_size)

        self.move_counter: int = 0
        self.frame_counter: int = 0
        self.speed_level: int = 1

        self.pause: bool = False
        self.move_figure_down_immediately: bool = False
        self.figure_just_rotated: bool = False  # flag for force redrawing the field during success rotation attempt
        self.need_to_quit: bool = False
        self.start_screen_active: bool = True

        self.current_user: str = current_user
        self.show_best_scores: bool = False

    # returns False if it's possible to stop updating
    def update_field(self) -> bool:
        self.move_counter += 1
        logger.debug('------- move_counter=%d', self.move_counter)
        current_figure: Figure = self.figures_factory.get_figure()
        figure_moves_counter: int = 0
        stop_moving_current_figure: bool = False  # current_figure have to stop due to field collision
        self.figure_just_rotated = False
        self.move_figure_down_immediately = False

        while not stop_moving_current_figure:
            self.clock.tick(MAX_FPS)
            self.process_events_queue(current_figure)

            if self.need_to_quit:
                return False

            if self.show_best_scores:
                self.scores.update(
                    score=self.points_clock_face.get_points(),
                    username=self.current_user,
                    timestamp=datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                )
                self.draw_show_best_scores()
                continue

            if self.start_screen_active:
                self.draw_start_screen()
                continue

            if self.pause:
                self.draw_pause_menu_screen()
                continue

            if (
                    self.frame_counter < SPEED_LEVELS[self.speed_level - 1]
                    and not self.move_figure_down_immediately
            ):
                self.frame_counter += 1
                self.draw_field()
                continue

            self.frame_counter = 0
            logger.debug('Scene update...')
            stop_moving_current_figure = self.render_current_figure_movement(
                current_figure,
            )

            if self.speed_level == len(SPEED_LEVELS) - 1:
                logger.debug(
                    'Player was reached the highest speed level! Exit game!',
                )
                self.show_best_scores = True
                continue

            if (
                    stop_moving_current_figure
                    and figure_moves_counter == 0
                    and self.field.is_almost_filled()
            ):
                logger.debug('Field is almost filled: exit game!')
                self.show_best_scores = True
                continue

            figure_moves_counter += 1
            logger.debug(
                'figure=%s, figure_moves_counter=%d',
                current_figure,
                figure_moves_counter,
            )
            self.draw_field()
        return True

    def process_events_queue(self, current_figure: Figure):
        # process events queue
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logger.debug('Exit game!')
                self.need_to_quit = True
            elif event.type == pygame.KEYDOWN:
                self.process_keydown(event, current_figure)

    def process_keydown(
            self, event: pygame.event.Event, current_figure: Figure,
    ):
        if self.start_screen_active:
            self.start_screen_active = False
            return
        if event.key == pygame.K_ESCAPE:
            # special event pause
            logger.debug('PRESSED BUTTON K_ESC')
            if self.pause:
                self.pause = False
                logger.debug('Pause mode was disabled')
            else:
                self.pause = True
                logger.debug('Pause mode was enabled')
            if self.show_best_scores:
                self.need_to_quit = True
                logger.debug('End game')
        elif not self.pause:
            if event.key == pygame.K_LEFT:
                logger.debug('PRESSED BUTTON K_LEFT')
                self.field.try_to_move_horizontally(current_figure, -1)
            elif event.key == pygame.K_RIGHT:
                logger.debug('PRESSED BUTTON K_RIGHT')
                self.field.try_to_move_horizontally(current_figure, 1)
            elif event.key == pygame.K_SPACE:
                logger.debug('PRESSED BUTTON K_SPACE')
                self.figure_just_rotated = self.field.try_to_rotate_figure(
                    current_figure,
                )
                logger.debug('after_rotate_attempt: %s', current_figure)
            elif event.key == pygame.K_DOWN:
                logger.debug('PRESSED BUTTON K_DOWN')
                self.move_figure_down_immediately = True

    def render_current_figure_movement(self, current_figure) -> bool:
        is_bottom_intersection, redraw_rotation = (
            self.field.try_to_move_vertically(
                figure=current_figure,
                shift=1,
                just_rotated=self.figure_just_rotated,
            )
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
            self.clock_images_representation = (
                self.points_clock_face.get_digits_representation()
            )
            if self.points_clock_face.points_int >= 10:
                self.speed_level = self.points_clock_face.points_int // 10 + 1
        return stop_moving_current_figure

    def draw_field(self):
        cell_x_size: int = 20
        cell_y_size: int = 20
        border_width: int = 5

        logger.debug('=' * (len(self.field.current_frame[0]) + 2))
        for line in self.field.current_frame:
            logger.debug(
                '|'
                + (''.join([str(x) for x in line]))
                .replace('0', ' ')
                .replace('1', '#')
                + '|',
            )
        logger.debug('=' * (len(self.field.current_frame[0]) + 2))

        # draw background
        background_image = next(self.background_images)
        self.screen.blit(source=background_image, dest=(0, 0))

        # draw the field borders
        pygame.draw.line(
            surface=self.screen,
            color=(0, 0, 0),
            start_pos=(0, 400 + border_width),
            end_pos=(200, 400 + border_width),
            width=border_width,
        )

        pygame.draw.line(
            surface=self.screen,
            color=(0, 0, 0),
            start_pos=(200 + border_width, 0),
            end_pos=(200 + border_width, 400 + border_width),
            width=border_width,
        )

        # draw the field
        for row_num in range(self.field_v_size):
            for elem_num in range(self.field_h_size):
                if self.field.current_frame[row_num][elem_num] == 1:
                    self.screen.blit(
                        source=self.particle.image,
                        dest=(cell_y_size * elem_num, cell_x_size * row_num),
                    )

        # draw image for new points get
        if self.get_point.need_to_draw():
            self.screen.blit(
                source=self.get_point.image, dest=self.get_point.position,
            )

        # draw clocks frame
        self.screen.blit(
            source=self.clock_frame.image, dest=self.clock_frame.position,
        )

        # draw digits into frame
        for digit_record in self.clock_images_representation:
            self.screen.blit(source=digit_record[0], dest=digit_record[1])

        # draw speed label
        self.__draw_custom_label(
            label_text=f'Скорость: {self.speed_level}',
            font=self.speed_label_font,
            label_position=(470, 50),
            update_display=False,
        )

        # draw current user
        self.__draw_custom_label(
            label_text=self.current_user,
            font=self.speed_label_font,
            label_position=(470, 80),
            update_display=False,
        )

        pygame.display.update()
        logger.debug('+++++++++++++++++++++++++++++++++++++++')

    def draw_pause_menu_screen(self):
        self.__draw_custom_label('ПОСОСИТЕ ГОВНА', self.menu_font, (30, 200))

    def draw_start_screen(self):
        self.__draw_custom_label(
            'Жмякни по клавише, браток', self.start_screen_font, (70, 200),
        )

    def draw_show_best_scores(self):
        sorted_scores = sorted(
            self.scores.scores_table.get_scores(),
            key=lambda x: int(x[0]),
            reverse=True,
        )
        max_range: int = 5
        pos_y: int = 40
        if len(sorted_scores) < 5:
            max_range = len(sorted_scores)

        self.__draw_custom_label(
            'Топ братков', self.scores_label_font, (170, pos_y),
        )
        pos_y += 40
        for i in range(max_range):
            record = sorted_scores[i]
            self.__draw_custom_label(
                label_text=f'{i+1}) {record[0]}, {record[1]}',
                font=self.scores_label_font,
                label_position=(150, pos_y),
            )
            pos_y += 35

    def __draw_custom_label(
            self,
            label_text: str,
            font: pygame.font.Font,
            label_position: Tuple[int, int],
            text_color: Tuple = (0, 0, 0),
            background_color: Tuple = (255, 255, 255),
            update_display: bool = True,
    ):
        custom_label: pygame.Surface = font.render(
            label_text, True, text_color, background_color,
        )
        self.screen.blit(source=custom_label, dest=label_position)
        if update_display:
            pygame.display.update()
