import json
import os
import time

def load_json(filename, encoding="utf8") -> dict:
    script_dir = os.path.abspath(os.curdir)
    abs_file_path = os.path.join(script_dir, filename)
    with open(abs_file_path, 'r', encoding=encoding) as f:
        file = json.loads(f.read())
    
    return file

def timestamp_print(string):
    timestamp = time.strftime("%I:%M %p", time.localtime())
    print("[{0}]".format(timestamp), string)

def print_loaded_commands(bot):
    timestamp_print(f"Loaded commands: {', '.join([command.name for command in bot.commands])}")