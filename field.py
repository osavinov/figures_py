import logging
from typing import Tuple
from figure import Figure
from copy import deepcopy
from figures_templates import get_id_next_figure

logger = logging.getLogger(__name__)

# FIELD COORDINATES MODEL
#
# 0
# ------------X  TOP (start position for figures)
# |
# |
# |
# |
# Y           BOTTOM (final position)
#
# Field indexing: [y][x]


class Field:
    def __init__(self, y_size: int, x_size: int):
        self.x_size = x_size
        self.y_size = y_size

        # current changeable frame = stable_frame + current figure
        self.current_frame = [[0 for _ in range(x_size)] for _ in range(y_size)]

        # frame without moving figure, only frozen
        self.__stable_frame = [[0 for _ in range(x_size)] for _ in range(y_size)]

    def try_to_move_horizontally(self, figure: Figure, shift: int):
        possible_position_x: int = figure.current_pos[0] + shift
        # right border collision
        if possible_position_x + figure.x_size > self.x_size:
            return

        # left border collision
        if possible_position_x < 0:
            return

        for fig_y in range(figure.y_size):
            for fig_x in range(figure.x_size):
                if figure.area[fig_y][fig_x] == 1:  # check only active cells
                    y_pos = fig_y + figure.current_pos[1]
                    x_pos = fig_x + possible_position_x
                    if self.__stable_frame[y_pos][x_pos] == 1:
                        return

        figure.current_pos[0] += shift

    def try_to_move_vertically(self, figure: Figure, shift: int, just_rotated: bool) -> Tuple[bool, bool]:
        possible_position_y: int = figure.current_pos[1] + shift
        is_bottom_intersection: bool
        redraw_rotation: bool
        if self.__is_intersection_with_bottom(figure, possible_position_y):
            is_bottom_intersection = True
        else:
            is_bottom_intersection = False
            figure.current_pos[1] += shift

        if is_bottom_intersection and just_rotated:
            redraw_rotation = True
        else:
            redraw_rotation = False

        return is_bottom_intersection, redraw_rotation

    def try_to_rotate_figure(self, figure: Figure) -> bool:
        cur_figure_id: int = figure.id
        next_figure_id: int = get_id_next_figure(cur_figure_id)

        if next_figure_id == cur_figure_id:
            return False

        logger.debug('Trying to transform (%d)->(%d)', cur_figure_id, next_figure_id)
        figure.transform(next_figure_id)
        if self.__has_field_collision(figure) or self.__prev_figures_collision(figure):
            logger.debug('Keep figure (%d)', cur_figure_id)
            figure.transform(cur_figure_id)  # return prev figure
            return False
        return True

    def __is_intersection_with_bottom(self, figure: Figure, possible_position_y: int) -> bool:
        # bottom collision
        if possible_position_y + figure.y_size > self.y_size:
            logger.debug('Collision with bottom! figure_y_pos=%d', possible_position_y)
            return True

        return self.__prev_figures_collision(figure, possible_position_y)

    def __prev_figures_collision(self, figure: Figure, possible_position_y: int = None) -> bool:
        if possible_position_y is None:
            possible_position_y = figure.current_pos[1]
        for fig_y in range(figure.y_size):
            for fig_x in range(figure.x_size):
                if figure.area[fig_y][fig_x] == 1:  # filled cell of figures area
                    x_pos = fig_x + figure.current_pos[0]
                    y_pos = fig_y + possible_position_y
                    if self.__stable_frame[y_pos][x_pos] == 1:  # ...cell in frame was filled too
                        logger.debug('Collision with other figures on x=%d, y=%d', x_pos, y_pos)
                        return True
        return False

    def __has_field_collision(self, figure: Figure) -> bool:
        # right border collision
        if figure.current_pos[0] + figure.x_size > self.x_size:
            return True

        # left border collision
        if figure.current_pos[0] < 0:
            return True

        # bottom collision
        if figure.current_pos[1] + figure.y_size > self.y_size:
            return True

        return False

    def overlay(self, figure: Figure, is_bottom_intersection: bool, redraw_rotation: bool) -> Tuple[bool, int]:
        if is_bottom_intersection:
            if redraw_rotation:
                logger.debug('Need to redraw current_frame due to rotation!')
                self.__redraw_current_frame(figure)
            points: int = self.delete_rows_if_necessary()
            self.__stable_frame = deepcopy(self.current_frame)
            return True, points

        self.__redraw_current_frame(figure)
        return False, 0

    def __redraw_current_frame(self, figure: Figure):
        new_field = deepcopy(self.__stable_frame)
        for i in range(figure.x_size):
            for j in range(figure.y_size):
                if figure.area[j][i] == 1:
                    x_pos = i + figure.current_pos[0]
                    y_pos = j + figure.current_pos[1]
                    new_field[y_pos][x_pos] = figure.area[j][i]
        self.current_frame = deepcopy(new_field)

    def delete_rows_if_necessary(self) -> int:
        rows_to_delete = [i for i in range(self.y_size) if sum(self.current_frame[i]) == self.x_size]
        if not rows_to_delete:
            return 0
        for x in reversed(rows_to_delete):
            del self.current_frame[x]
        app = [[0 for _ in range(self.x_size)] for _ in range(len(rows_to_delete))]
        logger.debug('%d rows were deleted!', len(rows_to_delete))
        self.current_frame = app + self.current_frame
        return len(rows_to_delete)

    def is_almost_filled(self) -> bool:
        if sum(self.current_frame[1]) > len(self.current_frame[1])/2:
            return True
        return False
