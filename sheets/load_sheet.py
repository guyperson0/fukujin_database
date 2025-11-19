import gspread
from pathlib import WindowsPath

# https://developers.google.com/workspace/sheets/api/quickstart/python
# https://docs.gspread.org/en/v6.1.4/user-guide.html

class LoadSheet:
    def __init__(self, spreadsheet_id, sheet_name, sheet_range):
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name
        self.sheet_range = sheet_range
        self.gc = gspread.service_account(filename="sheets/credentials/service_account.json")

    def load_sheet(self):
        return self.gc.open_by_key(self.spreadsheet_id).worksheet(self.sheet_name).get_all_values()