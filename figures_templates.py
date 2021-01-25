from typing import Tuple, Optional, List


class Sequence:
    def __init__(self, values: Tuple):
        self._values: Tuple = values
        self._index: int = -1

    def __contains__(self, item: int) -> bool:
        return item in self._values

    def next_elem(self, value: int) -> Optional[int]:
        if value not in self._values:
            return None
        for i in range(len(self._values)):
            if self._values[i] == value:
                if i < len(self._values) - 1:
                    return self._values[i + 1]
                return self._values[0]


figures_sequences: List[Sequence] = [
    Sequence((0, 1)),
    Sequence((2, 3, 4, 5)),
    Sequence((6,)),
    Sequence((7, 8, 9, 10)),
    Sequence((11, 12)),
]


def get_id_next_figure(current_fig_id: int) -> int:
    for seq in figures_sequences:
        if current_fig_id in seq:
            return seq.next_elem(current_fig_id)
    return -1


possible_figures_templates: List[List[List[int]]] = [
    [[0, 1], [1, 1], [1, 0]],
    [[1, 1, 0], [0, 1, 1]],
    [[1, 0], [1, 0], [1, 1]],
    [[1, 1, 1], [1, 0, 0]],
    [[1, 1], [0, 1], [0, 1]],
    [[0, 0, 1], [1, 1, 1]],
    [[1, 1], [1, 1]],
    [[0, 1, 0], [1, 1, 1]],
    [[1, 0], [1, 1], [1, 0]],
    [[1, 1, 1], [0, 1, 0]],
    [[0, 1], [1, 1], [0, 1]],
    [[1, 1, 1, 1]],
    [[1], [1], [1], [1]],
]
