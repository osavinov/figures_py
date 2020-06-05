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
        self.current_frame = [[0 for x in range(x_size)] for y in range(y_size)]

        # frame without moving figure, only frozen
        self.__stable_frame = [[0 for x in range(x_size)] for y in range(y_size)]

    def try_to_move_horizontally(self, fig: Figure, shift: int):
        possible_position_x: int = fig.current_pos[0] + shift
        # right border collision
        if possible_position_x + fig.x_size > self.x_size:
            return

        # left border collision
        if possible_position_x < 0:
            return

        for fig_y in range(fig.y_size):
            for fig_x in range(fig.x_size):
                if fig.area[fig_y][fig_x] == 1:  # check only active cells
                    y_pos = fig_y + fig.current_pos[1]
                    x_pos = fig_x + possible_position_x
                    if self.__stable_frame[y_pos][x_pos] == 1:
                        return

        fig.current_pos[0] += shift

    def try_to_move_vertically(self, fig: Figure, shift: int, just_rotated: bool) -> Tuple[bool, bool]:
        possible_position_y: int = fig.current_pos[1] + shift
        is_bottom_intersection: bool
        redraw_rotation: bool
        if self.__is_intersection_with_bottom(fig, possible_position_y):
            is_bottom_intersection = True
        else:
            is_bottom_intersection = False
            fig.current_pos[1] += shift

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

        logger.debug(f"Trying to transform ({cur_figure_id})->({next_figure_id})")
        figure.transform(next_figure_id)
        if self.__has_field_collision(figure) or self.__prev_figures_collision(figure):
            logger.debug(f"Keep figure ({cur_figure_id})")
            figure.transform(cur_figure_id)  # return prev figure
            return False
        return True

    def __is_intersection_with_bottom(self, fig: Figure, possible_position_y: int) -> bool:
        # bottom collision
        if possible_position_y + fig.y_size > self.y_size:
            logger.debug(f"Collision with bottom! figure_y_pos={possible_position_y}")
            return True

        return self.__prev_figures_collision(fig, possible_position_y)

    def __prev_figures_collision(self, fig: Figure, possible_position_y: int = None) -> bool:
        if possible_position_y is None:
            possible_position_y = fig.current_pos[1]
        for fig_y in range(fig.y_size):
            for fig_x in range(fig.x_size):
                if fig.area[fig_y][fig_x] == 1:  # filled cell of figures area
                    x_pos = fig_x + fig.current_pos[0]
                    y_pos = fig_y + possible_position_y
                    if self.__stable_frame[y_pos][x_pos] == 1:  # ...cell in frame was filled too
                        logger.debug(f"Collision with other figures on x={x_pos}, y={y_pos}")
                        return True
        return False

    def __has_field_collision(self, fig: Figure) -> bool:
        # right border collision
        if fig.current_pos[0] + fig.x_size > self.x_size:
            return True

        # left border collision
        if fig.current_pos[0] < 0:
            return True

        # bottom collision
        if fig.current_pos[1] + fig.y_size > self.y_size:
            return True

        return False

    def overlay(self, fig: Figure, is_bottom_intersection: bool, redraw_rotation: bool) -> Tuple[bool, int]:
        if is_bottom_intersection:
            if redraw_rotation:
                logger.debug("Need to redraw current_frame due to rotation!")
                self.__redraw_current_frame(fig)
            points: int = self.delete_rows_if_necessary()
            self.__stable_frame = deepcopy(self.current_frame)
            return True, points

        self.__redraw_current_frame(fig)
        return False, 0

    def __redraw_current_frame(self, fig: Figure):
        new_field = deepcopy(self.__stable_frame)
        for i in range(fig.x_size):
            for j in range(fig.y_size):
                if fig.area[j][i] == 1:
                    x_pos = i + fig.current_pos[0]
                    y_pos = j + fig.current_pos[1]
                    new_field[y_pos][x_pos] = fig.area[j][i]
        self.current_frame = deepcopy(new_field)

    def delete_rows_if_necessary(self) -> int:
        rows_to_delete = [i for i in range(self.y_size) if sum(self.current_frame[i]) == self.x_size]
        if not rows_to_delete:
            return 0
        for x in reversed(rows_to_delete):
            del self.current_frame[x]
        app = [[0 for x in range(self.x_size)] for y in range(len(rows_to_delete))]
        logger.debug(f"{len(rows_to_delete)} rows were deleted!")
        self.current_frame = app + self.current_frame
        return len(rows_to_delete)

    def is_almost_filled(self) -> bool:
        if sum(self.current_frame[1]) > len(self.current_frame[1])/2:
            return True
        return False
