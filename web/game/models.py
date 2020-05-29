from django.db import models
from django.db.models import Q
from django.utils import timezone
import datetime

# Create your models here.


class Question(models.Model):
    """Quizbowl current_question"""

    question_id = models.AutoField(primary_key=True)
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

    def get_players(self):

        valid_players = self.players.filter(
            Q(last_seen__gte=datetime.datetime.now().timestamp() - 3600) &
            Q(banned=False)
        )

        player_list = [{
            'user_name': player.user.name,
            'player_id': player.player_id,
            'score': player.score,
            'correct': player.correct,
            'negs': player.negs,
            'last_seen': player.last_seen,
            'active': datetime.datetime.now().timestamp() - player.last_seen < 10,
        } for player in valid_players]

        player_list.sort(key=lambda player: player['score'])
        return player_list

    def get_messages(self):

        valid_messages = self.messages.filter(visible=True)

        chrono_messages = [{
            'message_id': m.message_id,
            'tag': m.tag,
            'user_name': m.player.user.name,
            'content': m.content
        } for m in valid_messages.order_by('timestamp').reverse()[:50]]

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
    reported_by = models.ManyToManyField('Player')
    last_seen = models.FloatField(default=0)

    def unban(self):
        """Unban player
        """
        self.banned = False
        self.reported_by.all().delete()
        self.save()

    def __str__(self):
        return self.user.name + ":" + self.room.label


class Message(models.Model):
    """Message that can be sent by Players"""

    JOIN = 'join'
    LEAVE = 'leave'
    BUZZ_INIT = 'buzz_init'
    BUZZ_CORRECT = 'buzz_correct'
    BUZZ_WRONG = 'buzz_wrong'
    BUZZ_FORFEIT = 'buzz_forfeit'
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
        (BUZZ_FORFEIT, 'buzz_forfeit'),
        (SET_CATEGORY, 'set_category'),
        (SET_DIFFICULTY, 'set_difficulty'),
        (RESET_SCORE, 'reset_score'),
        (CHAT, 'chat'),
    )

    message_id = models.AutoField(primary_key=True)
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    content = models.CharField(max_length=200, null=True, blank=True)
    tag = models.CharField(max_length=20, choices=message_tags)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    visible = models.BooleanField(default=True)

    def __str__(self):
        return self.player.user.name + "(" + self.tag + ")" ":" + self.content