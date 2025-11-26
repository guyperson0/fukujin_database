import json
import os
import time
import re

color_regex = r'^#?([0-9a-f]{3}){1,2}$' 

def load_json(filename, encoding="utf8") -> dict:
    script_dir = os.path.abspath(os.curdir)
    abs_file_path = os.path.join(script_dir, filename)
    with open(abs_file_path, 'r', encoding=encoding) as f:
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