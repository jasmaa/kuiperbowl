from game.models import Message


def run():
    """Deletes messages from db"""
    messages = Message.objects.all()
    messages.delete()
