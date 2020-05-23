import random
import html
import hashlib
import datetime

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


def generate_id():
    # TODO: generate new id
    m = hashlib.md5()
    m.update((str(datetime.datetime.now().timestamp())).encode("utf8"))
    return int(m.hexdigest(), 16) % 1000000
