import re

def process_name(name):
    return re.sub('[^a-zA-z0-9]+', '', name.lower())