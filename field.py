import logging
from typing import Tuple

from figure import Figure
from copy import deepcopy

from figuresfactory import get_id_next_figure

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

    def __is_intersection_with_bottom(self, fig: Figure) -> bool:
        # bottom collision
        if fig.current_pos[1] + fig.y_size > self.y_size:
            logger.debug(f"Collision with bottom! figure_y_pos={fig.current_pos[1]}")
            return True

        for fig_y in range(fig.y_size):
            for fig_x in range(fig.x_size):
                if fig.area[fig_y][fig_x] == 1:  # filled cell of figures area
                    x_pos = fig_x + fig.current_pos[0]
                    y_pos = fig_y + fig.current_pos[1]
                    if self.__stable_frame[y_pos][x_pos] == 1:  # ...cell in frame was filled too
                        logger.debug(f"Collision with other figures on x={x_pos}, y={y_pos}")
                        return True
        return False

    def try_to_rotate_figure(self, figure: Figure):
        next_figure_id = get_id_next_figure(figure.id)
        logger.debug(f"Trying to transform #{figure.id}->#{next_figure_id}")

    def overlay(self, fig: Figure) -> Tuple[bool, int]:
        logger.debug(fig)
        if self.__is_intersection_with_bottom(fig):
            logger.debug("Intersection with bottom!")
            points: int = self.delete_rows_if_necessary()
            self.__stable_frame = deepcopy(self.current_frame)
            return True, points

        new_field = deepcopy(self.__stable_frame)
        for i in range(fig.x_size):
            for j in range(fig.y_size):
                if fig.area[j][i] == 1:
                    x_pos = i + fig.current_pos[0]
                    y_pos = j + fig.current_pos[1]
                    new_field[y_pos][x_pos] = fig.area[j][i]
        self.current_frame = deepcopy(new_field)
        return False, 0

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
