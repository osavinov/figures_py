import copy
import random


class Figure:
    def __init__(self, template: list, target_field_width: int):
        self.x_size = len(template[0])
        self.y_size = len(template)
        self.area = copy.deepcopy(template)

        self.start_pos = [0, 0]  # [x, y]
        self.current_pos = [random.randint(0, target_field_width - self.x_size), -1]  # starts from y=-1
