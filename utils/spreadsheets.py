import apiclient
import httplib2
from oauth2client.service_account import ServiceAccountCredentials

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
]

CREDENTIALS_FILE = '../credentials.json'
SPREADSHEET_ID = '19TJRdBdZvyJeD1HkNU1Xx5qZnDUq0US1nMDKmsQQeG0'


def get_access(spreadsheet_id: str = None):
    if not spreadsheet_id:
        spreadsheet_id = SPREADSHEET_ID
    service = get_service()
    service.permissions().create(
        fileId=spreadsheet_id,
        body={
            'type': 'user',
            'role': 'writer',
            'emailAddress': 'oleg.savinov.91@gmail.com',
        },
        fields='id',
    ).execute()


def create_sheet() -> str:
    service = get_service()
    spreadsheet = service.spreadsheets().create(
        body={
            'properties': {
                'title': 'scores',
                'locale': 'en_US',
            },
            'sheets': [
                {
                    'properties': {
                        'sheetType': 'GRID',
                        'sheetId': 1,
                        'title': 'score',
                        'gridProperties': {
                            'rowCount': 9999,
                            'columnCount': 3,
                        }
                    }
                }
            ]
        }
    ).execute()
    return spreadsheet['spreadsheetId']


def get_service():
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPES)
    http_auth = credentials.authorize(httplib2.Http())
    return apiclient.discovery.build(
        'sheets',
        'v4',
        http=http_auth,
    )


def main():
    get_access()
    # create_sheet()


if __name__ == '__main__':
    main()
