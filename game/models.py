from django.db import models
from django.utils import timezone
import datetime

# Create your models here.

class Question(models.Model):
    """Quizbowl current_question"""
    category = models.TextField()
    points = models.IntegerField()
    content = models.TextField()
    answer = models.TextField()
    duration = models.FloatField()

class Room(models.Model):
    """Room to play quizbowl"""

    IDLE = 'idle'
    PLAYING = 'playing'
    CONTEST = 'contest'
    game_states = (
        (IDLE, 'idle'),
        (PLAYING, 'playing'),
        (CONTEST, 'contest'),
    )

    EVERYTHING = 'Everything'
    SCIENCE = 'Science'
    HISTORY = 'History'
    LITERATURE = 'Literature'
    categories = (
        (EVERYTHING, 'Everything'),
        (SCIENCE, 'Science'),
        (HISTORY, 'History'),
        (LITERATURE, 'Literature'),
    )

    label = models.SlugField(unique=True)
    state = models.CharField(max_length=9, choices=game_states, default=IDLE)

    current_question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='rooms', null=True)
    start_time = models.FloatField(default=datetime.datetime.now().timestamp())
    end_time = models.FloatField(default=datetime.datetime.now().timestamp()+1)

    buzz_player = models.OneToOneField('Player', on_delete=models.CASCADE, null=True, related_name='buzz_player')
    buzz_start_time = models.FloatField(default=datetime.datetime.now().timestamp())
    buzz_end_time = models.FloatField(default=datetime.datetime.now().timestamp()+1)

    category = models.CharField(max_length=30, choices=categories, default=EVERYTHING)

    def __str__(self):
        return self.label

    def get_scores(self):
        scores = []
        for player in self.players.all():
            scores.append((player.name, player.score))
        scores.sort(key=lambda tup: tup[1])
        scores.reverse()
        return scores

    def get_messages(self):
        chrono_messages = []
        for m in self.messages.order_by('timestamp').reverse():
            chrono_messages.append(m.content)
        return chrono_messages

class Player(models.Model):
    """Quizbowl player for a room"""

    player_id = models.PositiveIntegerField(primary_key=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='players')
    name = models.CharField(max_length=20)
    score = models.IntegerField()
    locked_out = models.BooleanField()

    def __str__(self):
        return self.name + ":" + str(self.player_id)

class Message(models.Model):
    """Message that can be sent by Players"""
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
