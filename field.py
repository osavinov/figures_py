from figure import Figure
from copy import deepcopy


class Field:
    def __init__(self, y_size: int, x_size: int):
        self.x_size = x_size
        self.y_size = y_size
        self.current_frame = [[0 for x in range(x_size)] for y in range(y_size)]
        self.__stable_frame = [[0 for x in range(x_size)] for y in range(y_size)]

    def try_to_move_horizontally(self, fig: Figure, shift: int):
        possible_position_x: int = fig.current_pos[0] + shift
        # right border collision
        if possible_position_x + fig.x_size > self.x_size:
            return

        # left border collision
        if possible_position_x < 0:
            return

        #for i in range(fig.x_size):
        #    for j in range(fig.y_size):
        #        if fig.area[j][i] == 1:  # check only active cells
        #            y_pos = j + fig.current_pos[1]
        #            x_pos = i + possible_position_x
        #            if self.current_frame[y_pos][x_pos] == 1:
        #                return

        fig.current_pos[0] += shift

    def __is_intersection_with_bottom(self, fig: Figure) -> bool:
        # bottom collision
        if fig.current_pos[1] + fig.y_size > self.y_size:
            return True

        #for i in range(fig.x_size):
        #    for j in range(fig.y_size):
        #        if fig.area[j][i] == 1:
        #            x_pos = i + fig.current_pos[0]
        #            y_pos = j + fig.current_pos[1]
        #            if self.current_frame[y_pos][x_pos] == 1:
        #                return True

    def overlay(self, fig: Figure) -> bool:
        if self.__is_intersection_with_bottom(fig):
            self.delete_rows_if_necessary()
            self.__stable_frame = deepcopy(self.current_frame)
            return True

        new_field = deepcopy(self.__stable_frame)
        for i in range(fig.x_size):
            for j in range(fig.y_size):
                if fig.area[j][i] == 1:
                    x_pos = i + fig.current_pos[0]
                    y_pos = j + fig.current_pos[1]
                    new_field[y_pos][x_pos] = fig.area[j][i]
        self.current_frame = deepcopy(new_field)
        return False

    def delete_rows_if_necessary(self):
        rows_to_delete = [i for i in range(self.y_size) if sum(self.current_frame[i]) == self.x_size]
        if not rows_to_delete:
            return
        for x in reversed(rows_to_delete):
            del self.current_frame[x]
        app = [[0 for x in range(self.x_size)] for y in range(len(rows_to_delete))]
        self.current_frame = app + self.current_frame

    def is_almost_filled(self) -> bool:
        if sum(self.current_frame[1]) > len(self.current_frame[1])/2:
            return True
        return False
