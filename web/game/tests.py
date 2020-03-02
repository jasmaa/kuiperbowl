import pytest
from .models import *
import datetime

@pytest.mark.django_db
class TestRoom:
    
    def test_player_count(self):
        test_room = Room.objects.get(label='testroom')
        assert test_room.players.count() == 2

    def test_get_scores(self):
        test_room = Room.objects.get(label='testroom')
        assert len(test_room.get_scores()) == 1
    
    def test_get_messages(self):
        test_room = Room.objects.get(label='testroom')
        assert test_room.get_messages() == []