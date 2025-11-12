from googleapiclient.errors import HttpError
from sheets.load_sheet import LoadSheet

class PartyData(LoadSheet):
    def __init__(self, spreadsheet_id, sheet_name, sheet_range):
        super().__init__(spreadsheet_id, sheet_name, sheet_range)
        self.party_info = None
        self.load_party_data()

    def load_party_data(self):
        try:
            data = self.load_sheet()
            party_info = {}

            for row in data:
                if row:
                    party_info[row[0]] = row[1]
            
            self.party_info = party_info
        except HttpError as err:
            print(err)
    
    def get_party_info(self):
        return self.party_info.copy()