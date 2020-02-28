from figure import Figure
from copy import deepcopy


class Field:
    def __init__(self, x_size, y_size):
        self.x_size = x_size
        self.y_size = y_size
        self.current_frame = [[0 for x in range(x_size)] for y in range(y_size)]
        self.__stable_frame = [[0 for x in range(x_size)] for y in range(y_size)]

    def __is_collision(self, fig: Figure) -> bool:
        if fig.current_pos[1] + fig.y_size > self.y_size:
            return True
        return False

    def __is_intersection_with_borders(self, fig: Figure) -> bool:
        for i in range(fig.x_size):
            if fig.area[fig.y_size-1][i] == 1:
                if self.current_frame[fig.y_size-1 + fig.current_pos[1]][i + fig.current_pos[0]] == 1:
                    return True

    def overlay(self, fig: Figure) -> bool:
        if self.__is_collision(fig) or self.__is_intersection_with_borders(fig):
            self.delete_rows_if_necessary()
            self.__stable_frame = deepcopy(self.current_frame)
            return True

        new_field = deepcopy(self.__stable_frame)
        for i in range(fig.x_size):
            for j in range(fig.y_size):
                if fig.area[j][i] == 1:
                    new_field[j + fig.current_pos[1]][i + fig.current_pos[0]] = fig.area[j][i]
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
