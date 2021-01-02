import pytest
import pygame
from images import ClockFace
from settings import SCREEN_RESOLUTION
from typing import List, Tuple


class Anything:
    def __eq__(self, other: object) -> bool:
        return True


anything = Anything()


@pytest.fixture(scope='function')
def setup_pygame():
    pygame.init()
    pygame.display.set_mode(SCREEN_RESOLUTION)
    pygame.display.set_caption('tests')
    yield


@pytest.mark.parametrize(
    'add_points,expected_representation',
    [
        pytest.param(
            None,
            [
                (anything, (460, 305)),
            ],
            id='init_empty',
        ),
        pytest.param(
            1,
            [
                (anything, (460, 305)),
            ],
            id='add_one_point',
        ),
        pytest.param(
            10,
            [
                (anything, (460, 305)),
                (anything, (520, 305)),
            ],
            id='add_ten_points',
        ),
    ]
)
def test_clock_face(setup_pygame, add_points, expected_representation):
    clock_face = ClockFace('digits')
    digits_keys: List[int] = list(clock_face.digits.keys())
    clock_face.get_digits_representation()

    assert digits_keys == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    if add_points:
        clock_face.add_points(add_points)
        lock_images_representation: List[Tuple] = clock_face.get_digits_representation()
        assert clock_face.points_int == add_points
        assert lock_images_representation == expected_representation
