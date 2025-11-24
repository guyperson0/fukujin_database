import asyncio
import discord
import re
import requests
from discord.ext import commands, tasks
from traceback import print_exception

from util.utils import load_json, timestamp_print

config = load_json("config.json")
display = load_json("en.json")

class Profiles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database = bot.database
        self.auto_update_database.start()

        self.user_locks = {}
        self.chara_locks = {}
        self.lock = asyncio.Lock()

        self.min_display_name_len = 3
        self.max_display_name_len = 32
        
        self.color_regex = r'^#?([0-9a-f]{3}){1,2}$' # really hope i wrote this right
        
        self.min_stat_name_len = 1
        self.max_stat_name_len = 16
        self.min_stat_abbrev_len = 1
        self.max_stat_abbrev_len = 8
        self.min_stat_val_len = 1
        self.max_stat_val_len = 12

        self.min_ult_deco_len = 1
        self.max_ult_deco_len = 5
    
    @commands.hybrid_command(name="view", with_app_command=True)
    async def view(self, ctx, search_id=None, search_type="all", *, search_fields=None):
        """Retrieves the profile of a party member

        Parameters
        -----------
        search_id: str
            the id of the party member to be retrieved; defaults to yours if left empty
        search_type: str
            how fields are selected; one of "all", "short", "omit", or "only", defaults to all
        search_fields
            what fields to return, separated by space: "persona", "stats", "theurgia" "equips", "skills", "team_skills"
        
        """

        try:
            if search_id and not self.database.exists_and_accessible(ctx.author.id, search_id):
                raise KeyError

            p = self.database.get_profile(ctx.author.id, search_id)

            if not(var_embed := await self.__assemble_profile(p, search_type, search_fields)):
                return

            await ctx.send(embed=var_embed)
        except Exception as e:
            if isinstance(e, KeyError):
                if not search_id:
                    await send_error(ctx, "NO DEFAULT PROFILE", "NO DEFAULT PROFILE HAS BEEN ASSIGNED TO YOU. PLEASE ENTER A VALID PROFILE ID.")
                else:
                    await send_error(ctx, "NO SUCH PROFILE", f"PROFILE `{search_id}` DOES NOT EXIST.")            
            elif isinstance(e, SyntaxError):
                await send_error(ctx, "INVALID SEARCH TYPE", f"SEARCH TYPE `{search_type}` IS INVALID.")            
            else:
                print_exception(e)
                await send_error(ctx, "UNKNOWN", "PLEASE CONTACT ADMINISTRATOR EVOLI SIGIA AS SOON AS POSSIBLE.")

            debug_print(ctx, 
                        search_id=search_id, 
                        search_type=search_type, 
                        search_fields=search_fields
            )

    @commands.command(name='list')
    async def list_ids(self, ctx, unhide=""):
        try:
            response = "**VALID IDENTIFIERS**: "

            if unhide.lower() == "unhide" and self.database.members.is_admin(ctx.author.id):
                    response = "ACCESSING HIDDEN IDENTIFIERS...\n" + response
                    response += create_id_list(
                        self.database.get_profile_ids(True)
                    )
                    await ctx.reply(response, mention_author = False)
                    return
            
            response += create_id_list(
                        self.database.get_profile_ids()
                    )
            
            await ctx.reply(response, mention_author = False)
        except Exception as e:
            print_exception(e)
            debug_print(ctx, unhide=unhide)
            await send_error(ctx, "UNKNOWN", "PLEASE CONTACT ADMINISTRATOR EVOLI SIGIA AS SOON AS POSSIBLE.")

    @commands.command(name='allocate')
    async def add_stats(self, ctx, search_id, strength, magic, agility, endurance, luck):
        base_stats = [int(x) for x in self.database.profiles.get_base_stats(search_id)]

        try:
            add_stats = (int(strength), int(magic), int(agility), int(endurance), int(luck))
        except ValueError:
            await send_error("INVALID INPUT", f"INPUT MUST CONSIST OF ONLY INTEGERS")
            return

        async def validate():
            total = sum(add_stats)
            pending = int(self.database.profiles.get_value(search_id, "STATS_PENDING"))
            
            if total > pending:
                await send_error(ctx, "TOO MANY STATS ALLOCATED", f"ATTEMPTED TO ALLOCATE `{total}` STATS WITH `{pending}` STATS PENDING")
                return False

            return (
                await validate_add_bound(ctx, "STRENGTH", 1, 99, base_stats[0], add_stats[0]) and
                await validate_add_bound(ctx, "MAGIC", 1, 99, base_stats[1], add_stats[1]) and
                await validate_add_bound(ctx, "AGILITY", 1, 99, base_stats[2], add_stats[2]) and
                await validate_add_bound(ctx, "ENDURANCE", 1, 99, base_stats[3], add_stats[3]) and
                await validate_add_bound(ctx, "LUCK", 1, 99, base_stats[4], add_stats[4])
            )

        confirm_msg = (f"CONFIRMING THE ADDITION OF "
            f"`{add_stats[0]} Strength`, "
            f"`{add_stats[1]} Magic`, "
            f"`{add_stats[2]} Agility`, "
            f"`{add_stats[3]} Endurance`, "
            f"AND `{add_stats[4]} Luck` TO `{search_id}`")
        
        def edit_database():
            self.database.add_stats_list(search_id, add_stats)
        
        await self.edit_command(ctx, search_id, validate, confirm_msg, edit_database)

    @commands.command(name='editname')
    async def change_display_name(self, ctx, search_id, value):
        
        async def validate():
            return await validate_length(ctx, "DISPLAY NAME", self.min_display_name_len, self.max_display_name_len, value)

        confirm_msg = f"CONFIRMING DISPLAY CHANGE OF `{search_id}` TO `{value}`."

        def edit_database():
            self.database.change_name(search_id, value)

        await self.edit_command(ctx, search_id, validate, confirm_msg, edit_database)

    @commands.command(name='editicon')
    async def change_icon(self, ctx, search_id, value = None):
        icon_link = None
        
        for file in ctx.message.attachments:
            if is_image_link(file.url):
                icon_link = file.url
                break
        else:
            icon_link = value
            
        async def validate():
            if not icon_link:
                await send_error(ctx, "NO IMAGE ATTACHED", "NO IMAGE OR IMAGE LINK COULD BE FOUND IN THE INVOCATION MESSAGE")
                return False
            elif not is_image_link(icon_link):
                await send_error(ctx, "INVALID LINK", f"THE LINK `{icon_link}` TIMED OUT OR DID NOT RETURN A VALID IMAGE")
                return False
            
            return True

        confirm_msg = f"CONFIRMING ICON CHANGE TO THE FOLLOWING IMAGE:\n{icon_link}"

        def edit_database():
            self.database.change_icon(search_id, icon_link)

        await self.edit_command(ctx, search_id, validate, confirm_msg, edit_database)

    @commands.command(name='editcolor')
    async def change_color(self, ctx, search_id, value):
        value = value.lower().strip()
        if not value[0] == '#':
            value = '#' + value 

        async def validate():
            if not re.search(self.color_regex, value):
                await send_error(ctx, "INVALID COLOR", f"INVALID COLOR `{value}` WAS SUPPLIED; PLEASE ENTER A VALID HEXADECIMAL COLO")
                return False
            return True

        confirm_msg = f"CONFIRMING COLOR CHANGE OF `{search_id}` to `{value}`"

        def edit_database():
            self.database.change_color(search_id, value)

        await self.edit_command(ctx, search_id, validate, confirm_msg, edit_database)

    @commands.command(name='editcustomstat')
    async def change_custom_stat(self, ctx, search_id, stat_name, stat_abbrev, stat_value):

        async def validate():
            return (
                await validate_length(ctx, "CUSTOM STAT NAME", self.min_stat_name_len, self.max_stat_name_len, stat_name) and
                await validate_length(ctx, "CUSTOM STAT ABBREV.", self.min_stat_abbrev_len, self.max_stat_abbrev_len, stat_abbrev) and
                await validate_length(ctx, "CUSTOM STAT VALUE", self.min_stat_val_len, self.max_stat_val_len, stat_value)
            )
        
        confirm_msg = f"CONFIRMING CUSTOM STAT CHANGES OF `{search_id}` TO `{stat_name}: {stat_value}` (`{stat_value} {stat_abbrev}`)"

        def edit_database():
            self.database.change_custom_stat(search_id, stat_name, stat_abbrev, stat_value)

        await self.edit_command(ctx, search_id, validate, confirm_msg, edit_database)

    @commands.command(name='editdecorators')
    async def change_theurgia(self, ctx, search_id, left, right):
        
        async def validate():
            return (
                await validate_length(ctx, "LEFT DECORATOR", self.min_ult_deco_len, self.max_ult_deco_len, left) and
                await validate_length(ctx, "RIGHT DECORATOR", self.min_ult_deco_len, self.max_ult_deco_len, right)
            )

        confirm_msg = f"CONFIRMING THEURGY GAUGE DECORATORS: `{left} 2000 / 2000 {right}`"

        def edit_database():
            self.database.change_theurgia_gauge(search_id, left, right)

        await self.edit_command(ctx, search_id, validate, confirm_msg, edit_database)

    @tasks.loop(minutes=20.0)
    async def auto_update_database(self):
        timestamp_print("Automatically updating database!")
        self.bot.database.push_updates()

    async def __assemble_profile(self, profile, search_type, search_fields):
        if search_fields:
            fields = [x.lower() for x in search_fields.split()]
        else:
            fields = []

        match search_type.lower():
            case None | "all":
                return construct_embed(profile)
            case "short":
                return construct_embed(profile, persona_skills = False, team_skills = False)
            case "only" | "omit":
                omit = search_type == "omit"
                return construct_embed(profile,
                    persona = ("persona" in fields) ^ omit,
                    stats = ("stats" in fields) ^ omit,
                    theurgia = ("theurgia" in fields) ^ omit,
                    equipment = ("equipment" in fields or "equips" in fields) ^ omit,
                    persona_skills = ("skills" in fields or "persona_skills" in fields) ^ omit,
                    team_skills = ("team_skills" in fields) ^ omit
                )
            case _:
                raise SyntaxError(f"Search type {search_type} unrecognized")

    async def edit_after_confirm(self, ctx, confirm_message, edit_function, confirm = '✅', reject = '❎', time = 20.0):
        msg = await ctx.reply(confirm_message, mention_author = False)
        
        await msg.add_reaction(confirm)
        await msg.add_reaction(reject)
        
        try:
            def check(reaction, user):
                if not reaction.message == msg:
                    return False
                return user == ctx.message.author and str(reaction.emoji) in (confirm, reject)

            reaction, user = await self.bot.wait_for('reaction_add', timeout = time, check=check)
        except asyncio.TimeoutError:
            await msg.reply("REQUEST EXPIRED.")
        else:
            if str(reaction.emoji) == confirm:
                edit_function()
                await msg.reply("CHANGES CONFIRMED.")
            else:
                await msg.reply("CHANGES ABORTED.")

    async def edit_command(self, ctx, search_id, validate, confirm_msg, edit_database):
        try:
            user_id = ctx.author.id

            if not await self.permission_checks(ctx, user_id, search_id):
                return

            if not await validate():
                return
            
            if not await self.acquire_lock(ctx, user_id, search_id):
                return
            
            await self.edit_after_confirm(ctx, confirm_msg, edit_database)
            await self.release_lock(user_id)
        except Exception as e:
            print_exception(e)
            await send_error(ctx, "UNKNOWN", "PLEASE CONTACT ADMINISTRATOR EVOLI SIGIA AS SOON AS POSSIBLE.")
            await self.release_lock(user_id)
            
            debug_print(ctx, search_id=search_id)

    async def permission_checks(self, ctx, user_id, search_id, need_edit_access = True):
        if not self.database.exists_and_accessible(user_id, search_id):
            await send_error(ctx, "INVALID IDENTIFIER", f"THE ID `{search_id}` IS NOT VALID OR ACCESSIBLE.")
            return False
        elif need_edit_access and not self.database.members.has_edit_access(user_id, search_id):
            await send_error(ctx, "INSUFFICIENT PERMISSION", f"YOU DO NOT HAVE PERMISSION TO ACCESS THE PROFILE `{search_id}`")
            return False
        
        return True

    async def acquire_lock(self, ctx, user_id, search_id):
        async with self.lock:
            if user_id in self.user_locks:
                await send_error(ctx, "EDIT IN PROGRESS", f"YOU ARE CURRENTLY EDITING THE PROFILE `{self.user_locks[user_id]}`")
                return False
            elif search_id in self.chara_locks:
                chara_lock_holder = discord.Client.get_user(int(self.chara_locks[search_id]))
                await send_error(ctx, "EDIT IN PROGRESS", f"THIS PROFILE IS BEING EDITING BY `{chara_lock_holder.display_name} ({chara_lock_holder.name})`")
                return False
            
            self.user_locks[user_id] = search_id
            self.chara_locks[search_id] = user_id
            return True
              
    async def release_lock(self, user_id):
        async with self.lock:
            if user_id not in self.user_locks:
                return
            
            chara_id = self.user_locks.pop(user_id)
            self.chara_locks.pop(chara_id)

def add_member_info(embed, profile, add_icon=True):
    profile_icon = None
    if profile["DISPLAY_ICON"] and add_icon:
        profile_icon = profile["DISPLAY_ICON"]
    
    embed.set_author(name = profile["DISPLAY_NAME"])
    embed.set_thumbnail(url = profile_icon)

def add_persona(embed, profile):
    if profile["PERSONA_NAME"]:
        persona = display["persona"].format(
            arcana = profile["ARCANA"],
            persona = profile["PERSONA_NAME"]
        )
    else:
        persona = display["empty"]
    
    if profile["AFFINITIES"]:
        affinity = display["affinities"].format(affinities = profile["AFFINITIES"])
    else:
        affinity = display["neutral"]

    embed.add_field(name="Persona", value=persona, inline=True)
    embed.add_field(name="Affinities", value=affinity, inline=True)

def add_stats(embed, profile):
    stats = None

    if profile["CUSTOM_STAT_SHORT"] and profile["CUSTOM_STAT_VALUE"]:
        stats = display["stats_custom"]
    else:
        stats = display["stats"]

    if not int(profile["STATS_PENDING"]) == 0:
        stats += "\n" + display["pending_stat"]

    stats = stats.format(
        strength = profile["STRENGTH"],
        magic = profile["MAGIC"],
        agility = profile["AGILITY"],
        endurance = profile["ENDURANCE"],
        luck = profile["LUCK"],
        custom_value = profile["CUSTOM_STAT_VALUE"],
        custom_stat = profile["CUSTOM_STAT_SHORT"],
        pending = profile["STATS_PENDING"]
    )
    
    embed.add_field(name="Stats", value=stats, inline=False)

def add_theurgia(embed, profile):
    if profile["THEURGIA_NAME"]:
        theurgia_title = display["theurgy_title"].format(
            prefix = profile["GAUGE_PREFIX"],
            suffix = profile["GAUGE_SUFFIX"],
            charge = profile["THEURGY_CHARGE"],
            max = profile["MAX_THEURGY_CHARGE"]
        )
        theurgia_skill = display["theurgy_skill"].format(
            name = profile["THEURGIA_NAME"],
            effect = profile["THEURGIA_EFFECT"]
        )
    else:
        theurgia_title = display["theurgy_title_basic"]
        theurgia_skill = display["empty"]
    
    embed.add_field(name=theurgia_title, value=theurgia_skill, inline=False)

def add_equipment(embed, profile):
    if profile["WEAPON_NAME"]:
        if profile["WEAPON_EFFECT"]:
            weapon = display["weapon"]
        else:
            weapon = display["weapon_basic"]

        weapon = weapon.format(
            name = profile["WEAPON_NAME"],
            type = profile["WEAPON_TYPE"],
            element = profile["WEAPON_ELEMENT"],
            power = profile["WEAPON_POWER"],
            effect = profile["WEAPON_EFFECT"]
        )
    else:
        weapon = display["empty"]

    if profile["ACCESSORY_NAME"]:
        accessory = display["accessory"].format(
            name = profile["ACCESSORY_NAME"],
            effect = profile["ACCESSORY_EFFECT"]
        )
    else:
        accessory = display["empty"]

    embed.add_field(name="Accessory", value=accessory, inline=True)
    embed.add_field(name="Weapon", value=weapon, inline=True)

def add_persona_skills(embed, profile):
    if profile["SKILLS"]:
        skills = profile["SKILLS"]
        skills_display = ""

        for i in range(len(profile["SKILLS"])):
            if not i == 0:
                skills_display += "\n"
            
            skills_display += display["skill_bullet"]
            skills_display += display["skill"].format(
                name = skills[i][0],
                effect = skills[i][1]
            )
    else:
        skills_display = display["empty"]

    embed.add_field(name="Skills", value=skills_display, inline=False)

def add_team_skills(embed, profile):
    if profile["TEAM_SKILLS"]:
        team_skills = profile["TEAM_SKILLS"]
        skills_display = ""

        for i in range(len(profile["TEAM_SKILLS"])):
            if not i == 0:
                skills_display += "\n"
            
            skills_display += display["team_skill_bullet"]
            skills_display += display["team_skill"].format(
                name = team_skills[i][0],
                effect = team_skills[i][1]
            )
    else:
        skills_display = display["empty"]

    embed.add_field(name="Team Skills", value=skills_display, inline=False)

def add_pending(embed, profile):
    embed.set_footer(
        text = display["pending_footer"].format(
            stats = profile["STATS_PENDING"],
            other = profile["OTHER_PENDING"]
        )
    )

def construct_embed(profile, persona=True, stats=True, theurgia=True, equipment=True, persona_skills=True, team_skills=True):
    colour = None
    if profile["COLOR"]:
        colour = discord.Colour.from_str(profile["COLOR"])
    else:
        colour = discord.Colour.random()

    var_embed = discord.Embed(colour=colour)

    add_member_info(var_embed, profile)
    add_pending(var_embed, profile)
    if persona:
        add_persona(var_embed, profile)
    if stats:
        add_stats(var_embed, profile)
    if theurgia:
        add_theurgia(var_embed, profile)
    if equipment:
        add_equipment(var_embed, profile)
    if persona_skills:
        add_persona_skills(var_embed, profile)
    if team_skills:
        add_team_skills(var_embed, profile)

    return var_embed

def create_id_list(names : list):
    ids = ""
    for i in range(len(names)):
        if not i == 0:
            ids += ", "
        ids += f"`{names[i]}`"

    return ids

def debug_print(ctx):
    print(f"{ctx.author.name} ({ctx.author.id}) encountered error invoking {ctx.invoked_with}:")
    print(f"\t{ctx.message.content}")

def is_image_link(link):
    try: 
        r = requests.get(link, timeout=5)
        print(r.headers['content-type'])
        return r.headers['content-type'] in ('image/jpeg', 'image/png', 'image/gif', 'image/webp')
    except TimeoutError:
        return False

async def send_error(ctx, header, message):
    await ctx.reply(f"**ERROR**: {header}\n{message}", mention_author = False)

async def validate_length(ctx, field_name, min, max, value):
    return await validate_size(ctx, min, max, len(value), "INVALID LENGTH", 
                         f"{field_name} `{value}` MUST HAVE LENGTH BETWEEN `{min}` AND `{max}` (CURRENTLY: `{len(value)}`)")
    
async def validate_add_bound(ctx, field_name, min, max, base, add):
    return await validate_size(ctx, min, max, base + add, "INVALID ADDITION", 
                         f"`{field_name}` MUST BE BETWEEN `{min}` AND `{max}` (ATTEMPTED TO ADD {add} TO {base})")
        
async def validate_size(ctx, min, max, value, header, message):
    if value < min or value > max:
        await send_error(ctx, header, message)
        return False
    
    return True

async def setup(bot):
    await bot.add_cog(Profiles(bot))