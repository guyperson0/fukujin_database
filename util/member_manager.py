from util.utils import load_json

class MemberManager():
    def __init__(self):
        self.member_list = {}
        self.load_members()

    def load_members(self) -> None :
        members = load_json("member_info.json")
        config = load_json("config.json")

        for id in members:
            self.member_list[id] = {
                "access": members[id],
                "admin": int(id) in config["admin"]
            }

    def is_member(self, id) -> bool :
        return str(id) in self.member_list

    def is_admin(self, id) -> bool :
        return self.is_member(id) and self.member_list[str(id)]["admin"]

    def has_edit_access(self, member_id, chara_id) -> bool :
        return (
            self.is_member(member_id) and 
            chara_id in self.member_list[str(member_id)]["access"]
        ) or self.is_admin(member_id)

    def get_default_chara_id(self, member_id) -> str :
        member_id = str(member_id)
        if not self.is_member(member_id) or not self.member_list[member_id]["access"]:
            return None
        
        return self.member_list[member_id]["access"][0].lower()