from django.db import models

# Create your models here.

class Player(models.Model):
    """Quizbowl player"""

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

    name = models.CharField(max_length=20)
    state = models.CharField(max_length=9, choices=game_states, default=IDLE)
    players = models.ManyToManyField(Player, related_name='players', blank=True)
    locked_out_players = models.ManyToManyField(Player, related_name='locked_out_players', blank=True)
    current_question = models.OneToOneField(Question, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
