from django.db import models
from django.utils import timezone
import datetime

# Create your models here.

class Question(models.Model):
    """Quizbowl current_question"""

    category = models.TextField(default="Everything")
    points = models.IntegerField()
    content = models.TextField()
    answer = models.TextField()
    duration = models.FloatField()
    difficulty = models.TextField(default="HS")

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
    PHILOSOPHY = 'Philosophy'
    RELIGION = 'Religion'
    GEOGRAPHY = 'Geography'
    FINE_ARTS = 'Fine Arts'
    SOCIAL_SCIENCE = 'Social Science'
    MYTHOLOGY = 'Mythology'
    TRASH = 'Trash'
    categories = (
        (EVERYTHING, 'Everything'),
        (SCIENCE, 'Science'),
        (HISTORY, 'History'),
        (LITERATURE, 'Literature'),
        (PHILOSOPHY, 'Philosophy'),
        (RELIGION, 'Religion'),
        (GEOGRAPHY, 'Geography'),
        (FINE_ARTS, 'Fine Arts'),
        (SOCIAL_SCIENCE, 'Social Science'),
        (MYTHOLOGY, 'Mythology'),
        (TRASH, 'Trash'),
    )

    COLLEGE = "College"
    HS = "HS"
    MS = "MS"
    difficulties = (
        (COLLEGE, 'College'),
        (MS, 'MS'),
        (HS, 'HS'),
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
    difficulty = models.CharField(max_length=10, choices=difficulties, default=HS)

    def __str__(self):
        return self.label

    def get_scores(self):
        scores = []
        for player in self.players.filter(last_seen__gte=datetime.datetime.now().timestamp() - 3600):
            active = datetime.datetime.now().timestamp() - player.last_seen < 10
            scores.append((player.name, player.score, active))
        scores.sort(key=lambda tup: tup[1])
        scores.reverse()
        return scores

    def get_messages(self):
        chrono_messages = []
        for m in self.messages.order_by('timestamp').reverse()[:50]:
            chrono_messages.append( (m.tag, m.content) )
        return chrono_messages

class Player(models.Model):
    """Quizbowl player for a room"""

    player_id = models.PositiveIntegerField(primary_key=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='players')
    name = models.CharField(max_length=20)
    score = models.IntegerField()
    locked_out = models.BooleanField()
    last_seen = models.FloatField(default=datetime.datetime.now().timestamp())

    def __str__(self):
        return self.name + ":" + str(self.player_id)

class Message(models.Model):
    """Message that can be sent by Players"""

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    content = models.CharField(max_length=200)
    tag = models.CharField(max_length=20)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
