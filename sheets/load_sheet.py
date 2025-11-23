import gspread

# https://developers.google.com/workspace/sheets/api/quickstart/python
# https://docs.gspread.org/en/v6.1.4/user-guide.html

# TODO: pass service account and stuff so we can have multiple LoadSheet sub/classes without loading a new one each time

class LoadSheet:
    def __init__(self, account, spreadsheet_id, sheet_name):
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name
        self.gc = account

    def get_sheet(self):
        return self.gc.open_by_key(self.spreadsheet_id).worksheet(self.sheet_name)

    def load_values(self):
        return self.get_sheet().get_all_values()
    
    def load_records(self):
        return self.get_sheet().get_all_records()