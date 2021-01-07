import os
import pytest
from scores.scores import CSVReader, Scores


def test_init():
    scores: Scores = Scores(CSVReader('.'))
    assert scores.scores_table.get_scores() == []


def test_add_points():
    scores: Scores = Scores(CSVReader('.'))

    scores.update(
        score=1,
        username='test',
        timestamp='2020-01-07T00:00:00',
    )
    assert scores.scores_table.get_scores() == [(1, 'test', '2020-01-07T00:00:00')]


def test_add_point_repeat():
    scores: Scores = Scores(CSVReader('.'))

    scores.update(
        score=1,
        username='test1',
        timestamp='2020-01-07T00:00:00',
    )
    scores.update(
        score=2,
        username='test2',
        timestamp='2020-01-07T00:00:00',
    )
    assert scores.scores_table.get_scores() == [
        (1, 'test1', '2020-01-07T00:00:00'),
        (2, 'test2', '2020-01-07T00:00:00'),
    ]


@pytest.fixture(scope='function')
def drop_scores_file():
    yield
    if os.path.exists('./scores.dat'):
        os.remove('./scores.dat')


def test_add_point_rewrite(drop_scores_file):
    scores: Scores = Scores(CSVReader('.'))

    scores.update(
        score=1,
        username='test',
        timestamp='2020-01-07T00:00:00',
    )
    scores.rewrite()
    assert os.path.exists('./scores.dat')


def test_add_points_reload(drop_scores_file):
    scores: Scores = Scores(CSVReader('.'))

    scores.update(
        score=1,
        username='test',
        timestamp='2020-01-07T00:00:00',
    )
    scores.rewrite()

    scores = Scores(CSVReader('.'))
    assert scores.scores_table.get_scores() == [(1, 'test', '2020-01-07T00:00:00')]


def test_add_points_multi_reload(drop_scores_file):
    scores: Scores = Scores(CSVReader('.'))

    scores.update(
        score=1,
        username='test1',
        timestamp='2020-01-07T00:00:00',
    )
    scores.rewrite()

    scores = Scores(CSVReader('.'))

    scores.update(
        score=2,
        username='test2',
        timestamp='2020-01-07T00:00:00',
    )
    scores.rewrite()

    scores = Scores(CSVReader('.'))
    assert scores.scores_table.get_scores() == [
        (1, 'test1', '2020-01-07T00:00:00'),
        (2, 'test2', '2020-01-07T00:00:00'),
    ]
