from figure import Figure
import random

possible_figures_templates = [
    [[0, 1], [1, 1], [1, 0]],
    [[1, 0], [1, 0], [1, 1]],
    [[1, 1], [1, 1]],
    [[0, 1, 0], [1, 1, 1]],
    [[1, 0], [1, 1], [1, 0]],
    [[1, 1, 1], [0, 1, 0]],
    [[1, 1, 1, 1]],
    [[1], [1], [1], [1]]
]


class FiguresFactory:
    def __init__(self, target_field_width: int):
        self.target_field_width = target_field_width

    def get_figure(self) -> Figure:
        template = possible_figures_templates[random.randint(0, len(possible_figures_templates)-1)]
        return Figure(template, self.target_field_width)
