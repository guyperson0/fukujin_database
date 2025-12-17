from util.utils import load_json
from util.member_manager import MemberManager
from sheets.load_profiles import ProfilesData
from sheets.load_party_info import PartyData
from sheets.mod_sheet import SheetEditor

display = load_json("en.json")

#TODO: case insensitive profile id

class FukujinDatabaseManager():
    def __init__(self, account, config_path):
        self.gc = account
        self.config = load_json(config_path)

        self.profiles = ProfilesData(
            self.gc,
            self.config['spreadsheet_id'], 
            self.config['player_data_sheet_name']
        )
        self.party = PartyData(
            self.gc,
            self.config['spreadsheet_id'],
            self.config['party_data_sheet_name'],
        )
        self.editor = SheetEditor(
            self.gc,
            self.config['spreadsheet_id'],
            self.config['player_moddable_sheet_name']
        )
        self.members = MemberManager(config_path)

    def get_party_info(self):
        return self.party.get_party_info()

    def get_profile(self, search_id):
        return self.profiles.get_profile(search_id)
            
    def get_default_profile(self, member_id):
        self.get_profile(self.get_default_profile_id(member_id))

    def get_default_profile_id(self, member_id):
        return self.members.get_default_chara_id(member_id)

    def get_profile_ids(self, show_hidden = False):
        return self.profiles.get_profile_ids(show_hidden)

    def add_stats_list(self, search_id, add_stats : list):
        if len(add_stats) != 5:
            raise ValueError("Stats list length must be 5")
        stat_names = self.profiles.stat_names
        base_stats = [int(x) for x in self.profiles.get_base_stats(search_id)]

        edits = dict(zip(stat_names, (i+j for i,j in zip(base_stats, add_stats))))
        
        self.edit_values(search_id, edits)

    def exists(self, search_id):
        return self.profiles.exists(search_id)

    def accessible(self, member_id, search_id):
        if not self.exists(search_id):
            return False
        elif self.profiles.hidden(search_id) and not self.members.has_edit_access(member_id, search_id):
            return False
        else:
            return True

    def is_admin(self, member_id):
        return self.members.is_admin(member_id)

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

    def has_edits(self):
        return self.editor.has_edits()

    def push_updates(self):
        self.editor.update_sheet()
    
    def abort_updates(self):
        self.profiles.load_profile_data()
        self.editor.abort_edits()