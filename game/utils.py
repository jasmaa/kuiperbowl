import re
import random

WORDS = [
    "dingleberries",
    "my ex girlfriend",
    "not the bees",
    "god",
    "yes",
    "no",
]

def clean_content(content):
    m = re.match(r'^[ \w]+$', content.strip())
    return random.choice(WORDS) if m == None else m.group()
