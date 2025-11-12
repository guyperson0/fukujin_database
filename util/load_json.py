import json
import os

def load(filename, encoding="utf8"):
    script_dir = os.path.abspath(os.curdir)
    abs_file_path = os.path.join(script_dir, filename)
    with open(abs_file_path, 'r', encoding=encoding) as f:
        file = json.loads(f.read())
    
    return file