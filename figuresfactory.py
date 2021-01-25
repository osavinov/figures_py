from figure import Figure
import random

from figures_templates import possible_figures_templates


class FiguresFactory:
    def __init__(self, target_field_width: int):
        self.target_field_width = target_field_width

    def get_figure(self) -> Figure:
        figure_id: int = random.randint(0, len(possible_figures_templates) - 1)
        template = possible_figures_templates[figure_id]
        return Figure(
            template=template,
            target_field_width=self.target_field_width,
            figure_id=figure_id,
        )

    def get_specific_figure(self, figure_id: int) -> Figure:
        return Figure(
            template=possible_figures_templates[figure_id],
            target_field_width=self.target_field_width,
            figure_id=figure_id,
        )
