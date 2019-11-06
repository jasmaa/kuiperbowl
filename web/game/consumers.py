from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.db.models import Q
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .models import *
from .utils import *

import json
import datetime
import hashlib
import random
from fuzzywuzzy import fuzz

GRACE_TIME = 3

class QuizbowlConsumer(AsyncJsonWebsocketConsumer):
    """Websocket consumer for quizbowl game
    """

    async def connect(self):
        """Weboscket connect
        """
        self.room_name = self.scope['url_route']['kwargs']['label']
        self.room_group_name = f"game-{self.room_name}"

        # Join room
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
    
    async def disconnect(self, close_code):
        """Websocket disconnect
        """
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """Websocket receive
        """
        data = json.loads(text_data)
        room = Room.objects.get(label=self.room_name)

        if data['request_type'] == 'ping':
            await self.ping(room, data)
        elif data['request_type'] == 'join':
            await self.join(room, data)
        elif data['request_type'] == 'leave':
            await self.join(room)
        elif data['request_type'] == 'get_answer':
            await self.get_answer(room, data)
        elif data['request_type'] == 'new_user':
            await self.new_user(room)
        elif data['request_type'] == 'set_name':
            await self.set_name(room, data)
        elif data['request_type'] == 'next':
            await self.next(room, data)
        elif data['request_type'] == 'buzz_init':
            await self.buzz_init(room, data)
        elif data['request_type'] == 'buzz_answer':
            await self.buzz_answer(room, data)
        elif data['request_type'] == 'set_category':
            await self.set_category(room, data)
        elif data['request_type'] == 'set_difficulty':
            await self.set_difficulty(room, data)
        elif data['request_type'] == 'reset_score':
            await self.reset_score(room, data)
        elif data['request_type'] == 'chat':
            await self.chat(room, data)
        else:
            pass


    async def update_room(self, event):
        """Room update handler
        """
        await self.send_json(event['data'])

    async def ping(self, room, data):
        """Receive ping
        """
        try:
            p = room.players.get(player_id=data['player_id'])
            p.last_seen = datetime.datetime.now().timestamp()
            p.save()

            update_time_state(room)
                    
            await self.send_json(get_response_json(room))

        except Exception as e:
            await self.new_user(room)

    async def join(self, room, data):
        """Join room
        """
        p = room.players.get(player_id=data['player_id'])
        create_message("join", f"<strong>{p.name}</strong> has joined the room", room)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'update_room',
                'data': get_response_json(room),
            }
        )

    async def leave(self, room):
        """Leave room
        """
        p = room.players.get(player_id=data['player_id'])
        create_message("leave", f"<strong>{p.name}</strong> has left the room", room)
        await self.channel_layer.group_send(self.room_group_name, get_response_json(room))

    async def new_user(self, room):
        """Create new player
        """
        p = create_new_user(room)

        await self.send_json({
            "response_type": "new_user",
            "player_id": p.player_id,
            "player_name": p.name,
        })
        create_message("join", f"<strong>{p.name}</strong> has joined the room", room)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'update_room',
                'data': get_response_json(room),
            }
        )

    async def set_name(self, room, data):
        """Update player name
        """
        p = Player.objects.get(player_id=data['player_id'])
        old_name = p.name
        p.name = clean_content(data['content'])
        try:
            p.full_clean()
            p.save()

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'update_room',
                    'data': get_response_json(room),
                }
            )

        except ValidationError as e:
            return

    async def next(self, room, data):
        """Next question
        """
        update_time_state(room)
        if room.state == 'idle':
            questions = (
                Question.objects.filter(difficulty=room.difficulty)
                if room.category == 'Everything'
                else Question.objects.filter(Q(category=room.category) & Q(difficulty=room.difficulty))
            )
            q = random.choice(questions)

            room.state = 'playing'
            room.start_time = datetime.datetime.now().timestamp()
            room.end_time = room.start_time + q.duration
            room.current_question = q

            room.save()

            # unlock all players
            for p in room.players.all():
                p.locked_out = False
                p.save()

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'update_room',
                    'data': get_response_json(room),
                }
            )

    async def buzz_init(self, room, data):
        """Initialize buzz
        """
        p = room.players.get(player_id=data['player_id'])

        if not p.locked_out and room.state == 'playing':
            room.state = 'contest'
            room.buzz_player = room.players.get(player_id=data['player_id'])
            room.buzz_start_time = datetime.datetime.now().timestamp()
            room.save()

            create_message("buzz_init", f"<strong>{p.name}</strong> has buzzed", room)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'update_room',
                    'data': get_response_json(room),
                }
            )

    async def buzz_answer(self, room, data):
        p = room.players.get(player_id=data['player_id'])

        if p.player_id == room.buzz_player.player_id and room.state == 'contest':
            # fuzzy eval
            cleaned_content = clean_content(data['content'])
            ratio = fuzz.partial_ratio(cleaned_content, room.current_question.answer)

            if cleaned_content != "" and ratio >= 60:
                p.score += room.current_question.points
                p.save()

                # quick end question
                room.end_time = room.start_time
                room.save()

                create_message(
                    "buzz_correct",
                    f"<strong>{p.name}</strong> correctly answered <strong><i>{cleaned_content}</i></strong>",
                    room
                )
            else:
                # question reading ended, do penalty
                if room.end_time - room.buzz_start_time >= GRACE_TIME:
                    p.score -= 10
                p.locked_out = True
                p.save()

                create_message(
                    "buzz_wrong",
                    f"<strong>{p.name}</strong> incorrectly answered <strong><i>{cleaned_content}</i></strong>",
                    room
                )

                await self.send_json({
                    "response_type":"lock_out",
                })

            buzz_duration = datetime.datetime.now().timestamp() - room.buzz_start_time
            room.state = 'playing'
            room.start_time += buzz_duration
            room.end_time += buzz_duration
            room.save()

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'update_room',
                    'data': get_response_json(room),
                }
            )

    async def get_answer(self, room, data):
        """Get answer for room question
        """
        update_time_state(room)
        if room.state == 'idle':
            # generate random question for now if empty
            if room.current_question == None:
                questions = Question.objects.all()
                q = random.choice(questions)
                room.current_question = q
                room.save()
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'update_room',
                    'data': {
                        "response_type": "send_answer",
                        "answer": room.current_question.answer,
                    },
                }
            )

    async def set_category(self, room, data):
        """Set room category
        """
        try:
            room.category = clean_content(data['content'])
            room.current_question = random.choice(Question.objects.all()) if room.current_question == None else room.current_question
            room.buzz_player = room.players.first()
            room.full_clean()
            room.save()

            create_message("set_category", f"The category is now <strong><i>{room.category}</i></strong>", room)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'update_room',
                    'data': get_response_json(room),
                }
            )
        except ValidationError as e:
            pass

    async def set_difficulty(self, room, data):
        """Set room difficulty
        """
        try:
            room.difficulty = clean_content(data['content'])
            room.current_question = (
                random.choice(Question.objects.all())
                if room.current_question == None
                else room.current_question
            )
            room.buzz_player = room.players.first()
            room.full_clean()
            room.save()

            create_message("set_difficulty", f"The difficulty is now <strong><i>{room.difficulty}</i></strong>", room)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'update_room',
                    'data': get_response_json(room),
                }
            )
        except ValidationError as e:
            pass


    async def reset_score(self, room, data):
        """Reset player score
        """
        p = room.players.get(player_id=data['player_id'])
        p.score = 0
        p.save()

        create_message("reset_score", f"<strong>{p.name}</strong> has reset their score", room)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'update_room',
                'data': get_response_json(room),
            }
        )

    async def chat(self, room, data):
        p = room.players.get(player_id=data['player_id'])
        m = clean_content(data['content'])

        create_message("chat", f"<strong>{p.name}</strong>: {m}", room)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'update_room',
                'data': get_response_json(room),
            }
        )


# === Helper methods ===

def update_time_state(room):
    """Checks time and updates state
    """
    if not room.state == 'contest':
        if datetime.datetime.now().timestamp() >= room.end_time:
            room.state = 'idle'
            room.save()

def get_response_json(room):
    """Generates json for update response
    """
    return {
        "response_type":"update",
        "game_state":room.state,
        "current_time":datetime.datetime.now().timestamp(),
        "start_time":room.start_time,
        "end_time":room.end_time,
        "buzz_start_time":room.buzz_start_time,
        "current_question_content": room.current_question.content if room.current_question != None else "",
        "category":room.current_question.category if room.current_question != None else "",
        "room_category":room.category,
        "scores":room.get_scores(),
        "messages":room.get_messages(),
        "difficulty":room.difficulty,
    }

def create_message(tag, content, room):
    """Adds a message to db
    """
    try:
        m = Message(content=content, room=room, tag=tag)
        m.full_clean()
        m.save()
    except ValidationError as e:
        return

def create_new_user(room):
    """Generates new user
    """
    # generate new id
    m = hashlib.md5()
    m.update((room.label + str(datetime.datetime.now().timestamp())).encode("utf8"))
    player_id = int(m.hexdigest(), 16) % 1000000
    p = Player(player_id=player_id, name=generate_name(), room=room)
    p.save()

    return p
