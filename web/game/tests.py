from django.test import TestCase
from .models import *
import datetime

# Create your tests here.
class RoomTestCase(TestCase):
    def setUp(self):
        Question.objects.create(
            pk=1,
            category="Literature",
            points=20,
            content="Test content",
            answer="Test answer",
            duration=23.6,
            difficulty="HS",
        )
        Room.objects.create(
            label='testroom',
        )
        Player.objects.create(
            player_id=1,
            room=Room.objects.get(label='testroom'),
            name="chad",
            last_seen=datetime.datetime.now().timestamp()
        )
        Player.objects.create(
            player_id=2,
            room=Room.objects.get(label='testroom'),
            name="vivian",
        )
    
    def test_player_count(self):
        test_room = Room.objects.get(label='testroom')
        self.assertEqual(test_room.players.count(), 2)

    def test_get_scores(self):
        test_room = Room.objects.get(label='testroom')
        self.assertEqual(len(test_room.get_scores()), 1)
    
    def test_get_messages(self):
        test_room = Room.objects.get(label='testroom')
        self.assertEqual(test_room.get_messages(), [])