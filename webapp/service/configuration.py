
import json
import sys
import os

def read(path = False):
    if not path:
        path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/config.json'
    
    conf = json.loads(open(path).read())
    conf['base_path'] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return conf

