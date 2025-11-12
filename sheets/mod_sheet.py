from sheets.load_sheet import LoadSheet
from googleapiclient.discovery import build
from util.utils import timestamp_print

class SheetEditor(LoadSheet):
    def __init__(self, spreadsheet_id, sheet_name, sheet_range):
        super().__init__(spreadsheet_id, sheet_name, sheet_range)
        self.values = self.load_sheet()
        self.values_edited = False

    def update_sheet(self, majorDimension="ROWS"):
        if not self.values_edited:
            timestamp_print("No changes made since sheet was last loaded; cancelling update.")
            return
        else:
            timestamp_print("Updating sheet!")

        service = build("sheets", "v4", credentials=self.get_creds())

        sheet = service.spreadsheets()
        
        sheet.values().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body = {
                "valueInputOption": "USER_ENTERED",
                "data": [
                    {
                        "range": f"'{self.sheet_name}'!{self.sheet_range}",
                        "values": self.values,
                        "majorDimension": majorDimension
                    }   
                ]
            }
        ).execute()
        timestamp_print("Sheet has been updated! I hope...")

        self.values = self.load_sheet()
        self.values_edited = False

    def edit_values(self, chara_id : str, update_values : dict):
        self.values_edited = True
        fields = self.values[0]

        row = None
        for i in range(len(self.values)):
            if self.values[i][0].lower() == chara_id.lower():
                row = i
                break

        if not row:
            raise ValueError
        
        for col in range(len(fields)):
            if len(self.values[row]) == col:
                self.values[row].append('')

            if fields[col] in update_values:
                self.values[row][col] = update_values[fields[col]]