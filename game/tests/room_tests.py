import pytest
from ..models import *


@pytest.mark.django_db
def test_player_count():
    test_room = Room.objects.get(label="testroom")
    assert test_room.players.count() == 3
    assert test_room.players.filter(player_id=1).count() == 1
    assert test_room.players.filter(player_id=3).count() == 1


@pytest.mark.django_db
def test_get_scores():
    test_room = Room.objects.get(label="testroom")
    assert len(test_room.get_players()) == 1


@pytest.mark.django_db
def test_get_messages():
    test_room = Room.objects.get(label="testroom")
    assert test_room.get_messages() == []


@pytest.mark.django_db
def test_unban():
    test_room = Room.objects.get(label="testroom")
    banned_player = test_room.players.get(player_id=3)
    assert banned_player.banned
    assert banned_player.reported_by.count() == 2
    banned_player.unban()
    assert not banned_player.banned
    assert banned_player.reported_by.count() == 0
    assert test_room.players.count() == 3
