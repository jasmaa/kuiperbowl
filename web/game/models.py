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

    current_question = models.ForeignKey(
        Question,
        on_delete=models.SET_NULL,
        related_name='rooms',
        null=True,
        blank=True,
    )
    start_time = models.FloatField(default=0)
    end_time = models.FloatField(default=1)

    buzz_player = models.OneToOneField(
        'Player',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='buzz_player',
    )
    buzz_start_time = models.FloatField(default=0)
    buzz_end_time = models.FloatField(default=1)

    category = models.CharField(
        max_length=30,
        choices=categories,
        default=EVERYTHING,
    )
    difficulty = models.CharField(
        max_length=10,
        choices=difficulties,
        default=HS,
    )

    def __str__(self):
        return self.label

    def get_players(self, p):
        player_list = []
        for player in self.players.filter(last_seen__gte=datetime.datetime.now().timestamp() - 3600):
            active = datetime.datetime.now().timestamp() - player.last_seen < 10

            player_list.append({
                'user_name': player.user.name,
                'player_id': player.player_id,
                'score': player.score,
                'correct': player.correct,
                'negs': player.negs,
                'last_seen': player.last_seen,
                'muted': len(p.muted.filter(player_id=player.player_id)) > 0,
                'active': active,
            })
        player_list.sort(key=lambda player: player['score'])
        return player_list

    def get_messages(self):
        chrono_messages = []
        for m in self.messages.order_by('timestamp').reverse()[:50]:
            chrono_messages.append((m.tag, m.user.name, m.content))
        return chrono_messages


class User(models.Model):
    """Site user"""

    user_id = models.CharField(max_length=100)
    name = models.CharField(max_length=20)

    def __str__(self):
        return str(self.name)


class Player(models.Model):
    """Player in a room"""

    player_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='players',
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='players',
    )
    score = models.IntegerField(default=0)
    correct = models.IntegerField(default=0)
    negs = models.IntegerField(default=0)
    locked_out = models.BooleanField(default=False)

    banned = models.BooleanField(default=False)
    muted = models.ManyToManyField('Player')

    last_seen = models.FloatField(default=0)


class Message(models.Model):
    """Message that can be sent by Players"""

    JOIN = 'join'
    LEAVE = 'leave'
    BUZZ_INIT = 'buzz_init'
    BUZZ_CORRECT = 'buzz_correct'
    BUZZ_WRONG = 'buzz_wrong'
    SET_CATEGORY = 'set_category'
    SET_DIFFICULTY = 'set_difficulty'
    RESET_SCORE = 'reset_score'
    CHAT = 'chat'
    message_tags = (
        (JOIN, 'join'),
        (LEAVE, 'leave'),
        (BUZZ_INIT, 'buzz_init'),
        (BUZZ_CORRECT, 'buzz_correct'),
        (BUZZ_WRONG, 'buzz_wrong'),
        (SET_CATEGORY, 'set_category'),
        (SET_DIFFICULTY, 'set_difficulty'),
        (RESET_SCORE, 'reset_score'),
        (CHAT, 'chat'),
    )

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    content = models.CharField(max_length=200, null=True, blank=True)
    tag = models.CharField(max_length=20, choices=message_tags)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
