from sheets.load_sheet import LoadSheet

class ProfilesData(LoadSheet):
    def __init__(self, account, spreadsheet_id, sheet_name):
        super().__init__(account, spreadsheet_id, sheet_name)
        self.load_profile_data()

        self.stat_names = ("STRENGTH", "MAGIC", "AGILITY", "ENDURANCE", "LUCK")

    def load_profile_data(self):
        data = self.load_records()
        
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
        return [int(self.get_value(id, x)) for x in self.stat_names]

    def update_value(self, id, stat, value):
        self.profiles[id].update_values({stat: value})

    def update_values(self, id, update_values):
        profile = self.profiles[id]
        profile.update(update_values)
        profile["STATS_PENDING"] = profile["BASE_STATS"] - sum(profile[x] for x in self.stat_names)

    def exists(self, id) -> bool:
        return id in self.profiles

    def hidden(self, id) -> bool:
        return self.get_value(id, "HIDDEN") == "TRUE"

    def get_profile_ids(self, show_hidden = False):
        return [x for x in self.profiles.keys() 
                    if (self.get_value(x, "HIDDEN") == "FALSE") or 
                        show_hidden
                ]

def construct_skills(skills : str):
    if skills:
        skill_list = list(map((lambda x: x.split(":")), skills.split("~")))
    else: 
        skill_list = [["N/A", "None"]]
    return skill_list