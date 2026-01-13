import json
import time
import re
from project import PROJECT_PATH

color_regex = r'^#?([0-9a-f]{3}){1,2}$' 

def load_json(filepath, encoding="utf8") -> dict:
    file = PROJECT_PATH / filepath
    
    with open(file, 'r', encoding=encoding) as f:
        file = json.loads(f.read())
    
    return file

def timestamp_print(string):
    timestamp = time.strftime("%I:%M %p", time.localtime())
    print("[{0}]".format(timestamp), string)

def match_hex_color(value : str):
    value = value.lower().strip()
    value = value if value[0] == '#' else '#' + value
    return re.fullmatch(color_regex, value)

async def send_error(ctx, header, message):
    await ctx.reply(f"**ERROR**: {header}\n{message}", mention_author = False)