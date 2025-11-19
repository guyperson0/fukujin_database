from sheets.load_sheet import LoadSheet

class ProfilesData(LoadSheet):
    def __init__(self, spreadsheet_id, sheet_name, sheet_range):
        super().__init__(spreadsheet_id, sheet_name, sheet_range)
        self.profiles = None
        self.load_profile_data()

        self.stat_names = ("STRENGTH", "MAGIC", "AGILITY", "ENDURANCE", "LUCK")

    def load_profile_data(self):
        data = self.load_sheet()
        
        for record in data:
            record["SKILLS"] = construct_skills(record["SKILLS"])
            record["TEAM_SKILLS"] = construct_skills(record["TEAM_SKILLS"])

        self.profiles = dict(zip([r['ID'] for r in data], data))

    def get_profile(self, id) -> dict:
        return self.profiles[id.lower()].copy()

    def get_profiles(self) -> dict:
        return self.profiles.copy()
    
    def get_value(self, id, stat):
        return self.get_profile(id.lower()).get(stat)

    def get_base_stats(self, id):
        id = id.lower()
        return (self.get_value(id, x) for x in self.stat_names)

    def edit_value(self, id, stat, value):
        self.profiles[id].update(stat, value)

    def edit_values(self, id, update_values):
        self.profiles[id].update(update_values)

    def exists(self, id) -> bool:
        return id in self.profiles

    def hidden(self, id) -> bool:
        return self.get_value(id, "HIDDEN") == "TRUE"

    def get_profile_ids(self, show_hidden = False):
        return [x for x in self.profiles.keys() 
                    if (self.get_value(x, "HIDDEN") == "FALSE") or 
                        show_hidden
                ]

    def load_sheet(self):
        return self.gc.open_by_key(self.spreadsheet_id).worksheet(self.sheet_name).get_all_records()

def construct_skills(skills : str):
    if skills:
        skill_list = list(map((lambda x: x.split(":")), skills.split("~")))
    else: 
        skill_list = [["N/A", "None"]]
    return skill_list