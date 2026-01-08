import gspread

# https://developers.google.com/workspace/sheets/api/quickstart/python
# https://docs.gspread.org/en/v6.1.4/user-guide.html

class LoadSheet:
    def __init__(self, account : gspread.Client, spreadsheet_id, sheet_name):
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name
        self.gc = account

    def get_sheet(self):
        return self.gc.open_by_key(self.spreadsheet_id).worksheet(self.sheet_name)

    def load_values(self):
        return self.get_sheet().get_all_values()
    
    def load_records(self):
        return self.get_sheet().get_all_records()