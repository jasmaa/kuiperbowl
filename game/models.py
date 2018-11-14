from django.db import models
from django.utils import timezone

# Create your models here.

class Player(models.Model):
    """Quizbowl player"""

    player_id = models.PositiveIntegerField()
    name = models.CharField(max_length=20)
    score = models.IntegerField()

class Question(models.Model):
    """Quizbowl current_question"""
    category = models.TextField()
    points = models.IntegerField()
    content = models.TextField()
    answer = models.TextField()

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

    label = models.SlugField(unique=True)
    state = models.CharField(max_length=9, choices=game_states, default=IDLE)
    players = models.ManyToManyField(Player, related_name='players', blank=True)
    locked_out_players = models.ManyToManyField(Player, related_name='locked_out_players', blank=True)
    current_question = models.OneToOneField(Question, on_delete=models.CASCADE, null=True)
    start_time = models.DateTimeField(default=timezone.now, db_index=True)
    end_time = models.DateTimeField(default=timezone.now, db_index=True)

class Message(models.Model):
    """Message that can be sent by Players"""
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    player = models.OneToOneField(Player, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
