from util.utils import load_json
from util.member_manager import MemberManager
from sheets.load_profiles import ProfilesData
from sheets.mod_sheet import SheetEditor

config = load_json("config.json")
display = load_json("en.json")

class FukujinDatabaseManager():
    def __init__(self, account):
        self.gc = account

        self.profiles = ProfilesData(
            self.gc,
            config['spreadsheet_id'], 
            config['player_data_sheet_name']
        )
        self.editor = SheetEditor(
            self.gc,
            config['spreadsheet_id'],
            config['player_moddable_sheet_name']
        )
        self.members = MemberManager()

    def get_profile(self, member_id, search_id):
        if not search_id:
            search_id = self.members.get_default_chara_id(member_id)
        
        return self.profiles.get_profile(search_id)
            
    def get_profile_ids(self, show_hidden = False):
        return self.profiles.get_profile_ids(show_hidden)

    def add_stats_list(self, search_id, add_stats : list):
        if len(add_stats) != 5:
            raise ValueError("Stats list length must be 5")
        stat_names = self.profiles.stat_names
        base_stats = self.profiles.get_base_stats(search_id)

        edits = dict(zip(stat_names, (int(i)+j for i,j in zip(base_stats, add_stats))))
        edits["STATS_PENDING"] = str(int(self.profiles.get_value(search_id, "STATS_PENDING")) - sum(add_stats))

        self.edit_values(search_id, edits)

    def exists_and_accessible(self, member_id, search_id):
        if not self.profiles.exists:
            return False
        elif self.profiles.hidden(search_id) and not self.members.has_edit_access(member_id, search_id):
            return False
        else:
            return True

    def reset_stats(self, search_id):
        edit_values = {
            "STRENGTH": 1,
            "MAGIC": 1,
            "AGILITY": 1,
            "ENDURANCE": 1,
            "LUCK": 1
        }

        self.edit_values(search_id, edit_values)

    def change_name(self, search_id, value):
        self.edit_values(search_id, {"DISPLAY_NAME": value})

    def change_icon(self, search_id, value):
        self.edit_values(search_id, {"DISPLAY_ICON": value})

    def change_color(self, search_id, value):
        # raises value error
        self.edit_values(search_id, {"COLOR": value})

    def change_custom_stat(self, search_id, stat_name, stat_abbrev, stat_value):
        edit_values = {}
        self.edit_values(search_id, {
            "CUSTOM_STAT_NAME": stat_name,
            "CUSTOM_STAT_SHORT": stat_abbrev,
            "CUSTOM_STAT_VALUE": stat_value
        })

        self.edit_values(search_id, edit_values)

    def change_theurgia_gauge(self, search_id, left, right):
        self.edit_values(search_id, {
            "GAUGE_PREFIX": left,
            "GAUGE_SUFFIX": right
        })

    def edit_values(self, search_id, update_values : dict):
        self.profiles.update_values(search_id, update_values)
        self.editor.edit_values(search_id, update_values)

    def push_updates(self):
        self.editor.update_sheet()