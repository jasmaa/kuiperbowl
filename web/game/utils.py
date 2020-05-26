import random
import html
import datetime
import uuid

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
    """Escapes HTML
    """
    return html.escape(content)


def generate_name():
    """Generates randomized name
    """
    return '-'.join([random.choice(PREFIX), random.choice(NOUNS)])


def generate_id():
    """Generate user id
    """
    # TODO: account for collision??
    return uuid.uuid4().hex
