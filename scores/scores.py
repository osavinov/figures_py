import csv
import logging
import os
from abc import abstractmethod
from typing import List, Tuple, IO

import apiclient
import httplib2
from oauth2client.service_account import ServiceAccountCredentials

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
]

CREDENTIALS_FILE = 'credentials.json'
SPREADSHEET_ID = '19TJRdBdZvyJeD1HkNU1Xx5qZnDUq0US1nMDKmsQQeG0'

logger = logging.getLogger(__name__)


class ScoresTable:
    def __init__(self):
        self.__scores: List[Tuple[int, str, str]] = []

    def __len__(self) -> int:
        return len(self.__scores)

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
        self.scores_file.close()


class GoogleSheetsReader(AbstractReader):
    def __init__(self):
        self.available = True
        credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPES)
        http_auth = credentials.authorize(httplib2.Http())
        try:
            self.service = apiclient.discovery.build(
                'sheets',
                'v4',
                http=http_auth,
            )
        except httplib2.ServerNotFoundError:
            logger.error('Unable to connect to Google Sheets server!')
            self.available = False

    def read(self) -> ScoresTable:
        scores_table: ScoresTable = ScoresTable()
        if not self.available:
            return scores_table

        results = self.service.spreadsheets().values().batchGet(
            spreadsheetId=SPREADSHEET_ID,
            ranges='score!A1:C9999',
        ).execute()
        sheet_content: List[List] = results['valueRanges'][0]['values']
        for row in sheet_content:
            scores_table.add_record(
                points=row[0],
                username=row[1],
                timestamp=row[2],
            )
        return scores_table

    def rewrite(self, scores_table: ScoresTable):
        if not self.available:
            return
        range_sheet: str = f'score!A1:C{len(scores_table)}'
        self.service.spreadsheets().values().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={
                'valueInputOption': 'USER_ENTERED',
                'data': [
                    {
                        'range': range_sheet,
                        'majorDimension': 'ROWS',
                        'values': scores_table.get_scores(),
                    }
                ]
            }
        ).execute()


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
