import re

def process_name(name):
    if name[-3:].lower() == ' nz':
        name = name[:-3]
    return re.sub('[^a-zA-z0-9]+', '', name.lower())