from game.models import Player


def run():
    """Deletes messages from db"""
    players = Player.objects.all()
    players.delete()
