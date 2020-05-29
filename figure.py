import copy
import logging
import random
from typing import Tuple, List

from figures_templates import possible_figures_templates

logger = logging.getLogger(__name__)


class Figure:
    def __init__(self, template: list, target_field_width: int, figure_id: int):
        self.x_size = len(template[0])
        self.y_size = len(template)
        self.area: List[List] = copy.deepcopy(template)
        self.id = figure_id
        self.current_pos = [random.randint(0, target_field_width - self.x_size), -1]  # [x, y] starts from y=-1

    def __str__(self):
        return f"(id={self.id}, x_size={self.x_size}, y_size={self.y_size}, current_pos={self.current_pos}, area={self.area})"

    def transform(self, figure_id: int):
        new_template: Tuple = possible_figures_templates[figure_id]
        self.x_size = len(new_template[0])
        self.y_size = len(new_template)
        self.area = copy.deepcopy(new_template)
        self.id = figure_id
