from sheets.load_sheet import LoadSheet

class ProfilesData(LoadSheet):
    def __init__(self, spreadsheet_id, sheet_name, sheet_range):
        super().__init__(spreadsheet_id, sheet_name, sheet_range)
        self.profiles = None
        self.load_profile_data()

        self.stat_names = ("STRENGTH", "MAGIC", "AGILITY", "ENDURANCE", "LUCK")

    def load_profile_data(self):
        data = self.load_sheet()
        fields = data[0]
        profiles = {}

        # Construct profile dicts
        for row in data[1:]:
            if len(row) == 0 or not row[0]:
                continue

            profile = {}
            for i in range(len(fields)):
                # first field should always be ID
                if i == 0:
                    continue

                field = fields[i]

                # unfilled field
                if len(row) <= i:
                    profile[field] = ""
                else:
                    if field in ["SKILLS", "TEAM_SKILLS"] and row[i]:
                        profile[field] = construct_skills(row[i])
                    else:
                        profile[field] = row[i]

            profiles[row[0]] = profile
        
        self.profiles = profiles

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

def construct_skills(skills : str):
    skill_list = list(map((lambda x: x.split(":")), skills.split("~")))
    return skill_list