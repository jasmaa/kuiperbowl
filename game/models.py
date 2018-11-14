from django.db import models
from django.utils import timezone

# Create your models here.

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
    current_question = models.OneToOneField(Question, on_delete=models.CASCADE, null=True)
    start_time = models.DateTimeField(default=timezone.now, db_index=True)
    end_time = models.DateTimeField(default=timezone.now, db_index=True)

    def get_scores(self):
        scores = []
        for player in self.players.all():
            scores.append((player.name, player.score))
        scores.sort(key=lambda tup: tup[1])
        scores.reverse()
        return scores

class Player(models.Model):
    """Quizbowl player for a room"""

    player_id = models.PositiveIntegerField()
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='players')
    name = models.CharField(max_length=20)
    score = models.IntegerField()
    locked_out = models.BooleanField()

    def __str__(self):
        return self.name + ":" + str(self.player_id)

class Message(models.Model):
    """Message that can be sent by Players"""
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    player = models.OneToOneField(Player, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
