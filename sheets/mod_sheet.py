from sheets.load_sheet import LoadSheet
import gspread
from util.utils import timestamp_print

class SheetEditor(LoadSheet):
    def __init__(self, account, spreadsheet_id, sheet_name):
        super().__init__(account, spreadsheet_id, sheet_name)
        self.cache = self.load_values()
        self.pending_update = []

    def update_sheet(self):
        if not self.pending_update:
            timestamp_print("No changes made since sheet was last loaded; cancelling update.")
            return
        else:
            timestamp_print("Updating sheet!")

        self.get_sheet().update_cells(self.pending_update)
        self.pending_update.clear()

        timestamp_print("Sheet has been updated! I hope...")
        self.cache = self.load_values()

    def edit_values(self, chara_id : str, update_values : dict):
        fields = self.cache[0]

        timestamp_print(f"Adding updates for {chara_id}: {update_values}")

        row = None
        for i in range(len(self.cache)):
            if self.cache[i][0].lower() == chara_id.lower():
                row = i + 1
                break
        else:
            raise ValueError

        for j in range(len(fields)):
            if fields[j] in update_values:
                col = j + 1
                self.pending_update.append(gspread.Cell(row, col, update_values[fields[j]]))

    def abort_edits(self):
        timestamp_print("Aborting edits...")
        self.pending_update.clear()
        self.cache = self.load_values()