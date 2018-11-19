import random
import html

PREFIX = [
    "scarred",
    "light",
    "lost",
    "jelly",
    "cursed",
    "latent",
    "fake",
    "immortal",
]

NOUNS = [
    "vampire",
    "crab",
    "snail",
    "monkey",
    "snake",
    "cat",
    "bee",
    "phoenix",
]

def clean_content(content):
    return html.escape(content)

def generate_name():
    return '-'.join([random.choice(PREFIX), random.choice(NOUNS)])
