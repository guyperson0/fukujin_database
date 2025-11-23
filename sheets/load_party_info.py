from sheets.load_sheet import LoadSheet

class PartyData(LoadSheet):
    def __init__(self, account, spreadsheet_id, sheet_name):
        super().__init__(account, spreadsheet_id, sheet_name)
        self.party_info = None
        self.load_party_data()

    def load_party_data(self):
        data = self.load_values()
        self.party_info = dict(data)
        
    def get_party_info(self):
        return self.party_info.copy()