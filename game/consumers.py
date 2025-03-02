from asgiref.sync import async_to_sync
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.db.models import Q
from channels.generic.websocket import JsonWebsocketConsumer

from .models import *
from .utils import clean_content, generate_name, generate_id
from .judge import judge_answer

import json
import datetime
import random

GRACE_TIME = 3

# TODO: Use channels authentication?


class QuizbowlConsumer(JsonWebsocketConsumer):
    """Websocket consumer for quizbowl game
    """

    def connect(self):
        """Websocket connect
        """
        self.room_name = self.scope['url_route']['kwargs']['label']
        self.room_group_name = f"game-{self.room_name}"

        # Join room
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        """Websocket disconnect
        """
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        """Websocket receive
        """
        data = json.loads(text_data)
        if 'content' not in data or data['content'] == None:
            data['content'] = ''

        room = Room.objects.get(label=self.room_name)

        # Handle new user and join room
        if data['request_type'] == 'new_user':
            user = self.new_user(room)
            data['user_id'] = user.user_id
            self.join(room, data)

        # Abort if no user id or request type supplied
        if 'user_id' not in data or 'request_type' not in data:
            return

        # Validate user
        if len(User.objects.filter(user_id=data['user_id'])) <= 0:
            user = self.new_user(room)
            data['user_id'] = user.user_id
            self.join(room, data)

        # Handle join
        if data['request_type'] == 'join':
            self.join(room, data)
            return

        # Get player
        p = room.players.filter(user__user_id=data['user_id']).first()
        if p != None:

            # Kick if banned user
            if p.banned:
                self.kick()
                return

            # Handle requests for joined players
            if data['request_type'] == 'ping':
                self.ping(room, p)
            elif data['request_type'] == 'leave':
                self.leave(room, p)
            elif data['request_type'] == 'get_answer':
                self.get_answer(room)
            elif data['request_type'] == 'set_name':
                self.set_name(room, p, data['content'])
            elif data['request_type'] == 'next':
                self.next(room)
            elif data['request_type'] == 'buzz_init':
                self.buzz_init(room, p)
            elif data['request_type'] == 'buzz_answer':
                self.buzz_answer(room, p, data['content'])
            elif data['request_type'] == 'set_category':
                self.set_category(room, p, data['content'])
            elif data['request_type'] == 'set_difficulty':
                self.set_difficulty(room, p, data['content'])
            elif data['request_type'] == 'reset_score':
                self.reset_score(room, p)
            elif data['request_type'] == 'chat':
                self.chat(room, p, data['content'])
            elif data['request_type'] == 'report_message':
                self.report_message(room, p, data['content'])
            else:
                pass

    def update_room(self, event):
        """Room update handler
        """
        self.send_json(event['data'])

    def ping(self, room, p):
        """Receive ping
        """

        p.last_seen = datetime.datetime.now().timestamp()
        p.save()

        update_time_state(room)

        self.send_json(get_response_json(room))
        self.send_json({
            'response_type': 'lock_out',
            'locked_out': p.locked_out,
        })

    def join(self, room, data):
        """Join room
        """
        user = User.objects.filter(user_id=data['user_id']).first()
        if user == None:
            return

        # Create player if doesn't exist
        p = user.players.filter(room=room).first()
        if p == None:
            p = Player.objects.create(room=room, user=user)

        create_message("join", p, None, room)

        self.send_json(get_response_json(room))

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'update_room',
                'data': get_response_json(room),
            }
        )

    def leave(self, room, p):
        """Leave room
        """

        create_message("leave", p, None, room)
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'update_room',
                'data': get_response_json(room),
            }
        )

    def new_user(self, room):
        """Create new user and player in room
        """
        user = User.objects.create(user_id=generate_id(), name=generate_name())

        self.send_json({
            "response_type": "new_user",
            "user_id": user.user_id,
            "user_name": user.name,
        })

        return user

    def set_name(self, room, p, content):
        """Update player name
        """

        old_name = p.user.name
        p.user.name = clean_content(content)
        try:
            p.user.full_clean()
            p.user.save()

            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'update_room',
                    'data': get_response_json(room),
                }
            )

        except ValidationError as e:
            return

    def next(self, room):
        """Next question
        """

        update_time_state(room)

        if room.state == 'idle':
            questions = (
                Question.objects.filter(difficulty=room.difficulty)
                if room.category == 'Everything'
                else Question.objects.filter(Q(category=room.category) & Q(difficulty=room.difficulty))
            )

            # Abort if no questions
            if len(questions) <= 0:
                return

            q = random.choice(questions)

            room.state = 'playing'
            room.start_time = datetime.datetime.now().timestamp()
            room.end_time = room.start_time + q.duration
            room.current_question = q

            room.save()

            # Unlock all players
            for p in room.players.all():
                p.locked_out = False
                p.save()

            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'update_room',
                    'data': get_response_json(room),
                }
            )

    def buzz_init(self, room, p):
        """Initialize buzz
        """

        # Reject when not in contest
        if room.state != 'playing':
            return

        # Abort if no current question
        if room.current_question == None:
            return

        if not p.locked_out and room.state == 'playing':

            room.state = 'contest'
            room.buzz_player = p
            room.buzz_start_time = datetime.datetime.now().timestamp()
            room.save()

            p.locked_out = True
            p.save()

            create_message("buzz_init", p, None, room)

            self.send_json({
                'response_type': 'buzz_grant',
            })
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'update_room',
                    'data': get_response_json(room),
                }
            )

    def buzz_answer(self, room, p, content):
        # Reject when not in contest
        if room.state != 'contest':
            return

        # Abort if no buzz player or current question
        if room.buzz_player == None or room.current_question == None:
            return

        if p.player_id == room.buzz_player.player_id:
            cleaned_content = clean_content(content)

            # Answer is correct
            if judge_answer(cleaned_content, room.current_question.answer):
                p.score += room.current_question.points
                p.correct += 1
                p.save()

                # Quick end question
                buzz_duration = datetime.datetime.now().timestamp() - room.buzz_start_time
                room.state = 'playing'
                room.start_time += buzz_duration
                room.end_time = room.start_time
                room.save()

                create_message(
                    "buzz_correct",
                    p,
                    cleaned_content,
                    room,
                )
            # Answer is incorrect
            else:
                # Received answer in grace time after question reading ended
                # If answer is still, apply penalty.
                if room.end_time - room.buzz_start_time >= GRACE_TIME:
                    p.score -= 10
                    p.negs += 1
                    p.save()

                create_message(
                    "buzz_wrong",
                    p,
                    cleaned_content,
                    room,
                )

                # Send lock out status to buzzing player
                self.send_json({
                    "response_type": "lock_out",
                    "locked_out": True,
                })

                buzz_duration = datetime.datetime.now().timestamp() - room.buzz_start_time
                room.state = 'playing'
                room.start_time += buzz_duration
                room.end_time += buzz_duration
                room.save()
        # Buzz time is up. Forfeit the question
        elif datetime.datetime.now().timestamp() >= room.buzz_start_time + GRACE_TIME:
            buzz_duration = datetime.datetime.now().timestamp() - room.buzz_start_time
            room.state = 'playing'
            room.start_time += buzz_duration
            room.end_time += buzz_duration
            room.save()

            create_message(
                "buzz_forfeit",
                room.buzz_player,
                None,
                room,
            )

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'update_room',
                'data': get_response_json(room),
            }
        )

    def get_answer(self, room):
        """Get answer for room question
        """

        update_time_state(room)

        if room.state == 'idle':
            # Generate random question for now if empty
            if room.current_question == None:
                questions = Question.objects.all()

                # Abort if no questions
                if len(questions) <= 0:
                    return

                q = random.choice(questions)
                room.current_question = q
                room.save()

            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'update_room',
                    'data': {
                        "response_type": "send_answer",
                        "answer": room.current_question.answer,
                    },
                }
            )

    def set_category(self, room, p, content):
        """Set room category
        """
        # Abort if change locked
        if room.change_locked:
            return

        try:
            room.category = clean_content(content)
            room.full_clean()
            room.save()

            create_message(
                "set_category",
                p,
                room.category,
                room,
            )
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'update_room',
                    'data': get_response_json(room),
                }
            )
        except ValidationError as e:
            pass

    def set_difficulty(self, room, p, content):
        """Set room difficulty
        """
        # Abort if change locked
        if room.change_locked:
            return

        try:
            room.difficulty = clean_content(content)
            room.full_clean()
            room.save()

            create_message(
                "set_difficulty",
                p,
                room.difficulty,
                room,
            )
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'update_room',
                    'data': get_response_json(room),
                }
            )
        except ValidationError as e:
            pass

    def reset_score(self, room, p):
        """Reset player score
        """

        p.score = 0
        p.save()

        create_message("reset_score", p, None, room)
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'update_room',
                'data': get_response_json(room),
            }
        )

    def chat(self, room, p, content):
        """ Send chat message
        """

        m = clean_content(content)

        create_message("chat", p, m, room)
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'update_room',
                'data': get_response_json(room),
            }
        )

    def kick(self):
        """Kick banned player
        """
        self.send_json({
            "response_type": "kick",
        })
        async_to_sync(self.channel_layer.group_discard)(
            self.room_name,
            self.channel_name
        )

    def report_message(self, room, p, message_id):
        """Handle reporting messages
        """
        m = room.messages.filter(message_id=message_id).first()
        if m == None:
            return

        # Only report chat or buzz messages
        if m.tag == 'chat' or m.tag == 'buzz_correct' or m.tag == 'buzz_wrong':
            m.player.reported_by.add(p)
            m.save()

            # Ban if reported by 60% of players
            ratio = len(m.player.reported_by.all()) / len(room.players.all())
            if ratio > 0.6:
                m.player.banned = True
                m.player.save()

# === Helper methods ===


def update_time_state(room):
    """Checks time and updates state
    """
    if not room.state == 'contest':
        if datetime.datetime.now().timestamp() >= room.end_time:
            room.state = 'idle'
            room.save()


def get_response_json(room):
    """Generates JSON for update response
    """
    return {
        "response_type": "update",
        "game_state": room.state,
        "current_time": datetime.datetime.now().timestamp(),
        "start_time": room.start_time,
        "end_time": room.end_time,
        "buzz_start_time": room.buzz_start_time,
        "current_question_content": room.current_question.content if room.current_question != None else "",
        "category": room.current_question.category if room.current_question != None else "",
        "room_category": room.category,
        "messages": room.get_messages(),
        "difficulty": room.difficulty,
        "players": room.get_players(),
        "change_locked": room.change_locked,
    }


def create_message(tag, p, content, room):
    """Adds a message to db
    """
    try:
        m = Message(tag=tag, player=p, content=content, room=room)
        m.full_clean()
        m.save()
    except ValidationError as e:
        return
