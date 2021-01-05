import csv
import os
from abc import abstractmethod
from typing import List, Tuple, IO


class ScoresTable:
    def __init__(self):
        self.__scores: List[Tuple[int, str, str]] = []

    def add_record(self, points: int, username: str, timestamp: str):
        self.__scores.append((points, username, timestamp))

    def get_scores(self) -> List[Tuple[int, str, str]]:
        return self.__scores


class AbstractReader:
    @abstractmethod
    def read(self) -> ScoresTable:
        pass

    @abstractmethod
    def rewrite(self, scores_table: ScoresTable):
        pass


class CSVReader(AbstractReader):
    def __init__(self, root_dir: str):
        self.scores_filename: str = os.path.join(root_dir, 'scores.dat')
        self.scores_file = None

    def read(self) -> ScoresTable:
        if os.path.exists(self.scores_filename):
            self.scores_file: IO = open(
                file=self.scores_filename,
                mode='r+',
            )
            scores_table: ScoresTable = ScoresTable()
            csv_reader = csv.reader(self.scores_file, delimiter=',')
            for row in csv_reader:
                scores_table.add_record(
                    points=int(row[0]),
                    username=row[1],
                    timestamp=row[2],
                )
            self.scores_file.close()
            return scores_table
        return ScoresTable()

    def rewrite(self, scores_table: ScoresTable):
        self.scores_file = open(
            file=self.scores_filename,
            mode='w+',
        )
        csv_writer = csv.writer(self.scores_file, delimiter=',')
        for row in scores_table.get_scores():
            csv_writer.writerow(row)


class GoogleSheetsReader(AbstractReader):
    def read(self) -> ScoresTable:
        pass

    def rewrite(self, scores_table: ScoresTable):
        pass


class Scores:
    def __init__(self, reader: AbstractReader):
        self.reader = reader
        self.scores_table: ScoresTable = self.reader.read()

    def update(self, score: int, username: str, timestamp: str):
        self.scores_table.add_record(
            points=score,
            username=username,
            timestamp=timestamp,
        )

    def rewrite(self):
        self.reader.rewrite(self.scores_table)
