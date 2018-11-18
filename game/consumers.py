from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from channels import Group
from channels.sessions import channel_session
from .models import *
from .utils import *

import json
import datetime
import hashlib
import random
from fuzzywuzzy import fuzz

GRACE_TIME = 3

@channel_session
def ws_connect(message):
    # get room
    prefix, label = message['path'].strip('/').split('/')
    room = Room.objects.get(label=label)
    Group('game-'+label).add(message.reply_channel)
    message.reply_channel.send({"accept":True})
    message.channel_session['room'] = room.label

@channel_session
def ws_receive(message):
    # get message
    label = message.channel_session['room']
    room = Room.objects.get(label=label)
    data = json.loads(message['text'])

    # determine request type
    if(data['request_type'] == 'ping'):
        # update ping
        update_time_state(room)
        message.reply_channel.send(get_response_json(room))

    elif(data['request_type'] == 'new_user'):
        # new user
        # generate new id
        m = hashlib.md5()
        m.update((label + str(datetime.datetime.now().timestamp())).encode("utf8"))
        player_id = int(m.hexdigest(), 16) % 1000000
        p = Player(player_id=player_id, name="Jerry", score=0, locked_out=False, room=room)
        p.save()

        message.reply_channel.send({'text':json.dumps({
            "response_type":"new_user",
            "player_id":p.player_id,
            "player_name":p.name,
        })})

    elif(data['request_type'] == 'set_name'):
        # update name
        p = Player.objects.get(player_id=int(data['player_id']))
        old_name = p.name
        p.name = clean_content(data['content'])
        p.save()

        Group('game-'+label).send(get_response_json(room))

    elif(data['request_type'] == 'next'):
        # next question
        update_time_state(room)
        if room.state == 'idle':
            questions = Question.objects.all() if room.category == 'Everything' else Question.objects.filter(category=room.category)
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

            Group('game-'+label).send(get_response_json(room))

    elif(data['request_type'] == 'buzz_init'):
        # buzz init

        p = room.players.get(player_id=data['player_id'])

        if not p.locked_out and room.state == 'playing':
            room.state = 'contest'
            room.buzz_player = room.players.get(player_id=data['player_id'])
            room.buzz_start_time = datetime.datetime.now().timestamp()
            room.save()

            create_message("buzz_init", f"<strong>{p.name}</strong> has buzzed", room)
            Group('game-'+label).send(get_response_json(room))

    elif(data['request_type'] == 'buzz_answer'):
        # buzz answer

        p = room.players.get(player_id=data['player_id'])

        if not p.locked_out and room.state == 'contest':
            # fuzzy eval
            cleaned_content = clean_content(data['content'])
            ratio = fuzz.partial_ratio(cleaned_content, room.current_question.answer)

            if cleaned_content != "" and ratio >= 60:
                p.score += room.current_question.points
                p.save()

                # quick end question
                room.end_time = room.start_time
                room.save()

                create_message("buzz_correct", f"<strong>{p.name}</strong> correctly answered <strong><i>{cleaned_content}</i></strong>", room)
            else:
                # question going ended do penalty
                if room.end_time - room.buzz_start_time >= GRACE_TIME:
                    p.score -= 10
                p.locked_out = True
                p.save()

                create_message("buzz_wrong", f"<strong>{p.name}</strong> incorrectly answered <strong><i>{cleaned_content}</i></strong>", room)

                message.reply_channel.send({'text':json.dumps({
                    "response_type":"lock_out",
                })})

            buzz_duration = datetime.datetime.now().timestamp() - room.buzz_start_time
            room.state = 'playing'
            room.start_time += buzz_duration
            room.end_time += buzz_duration
            room.save()

            Group('game-'+label).send(get_response_json(room))

    elif(data['request_type'] == 'get_answer'):
        update_time_state(room)
        if room.state == 'idle':
            # generate random question for now if empty
            if room.current_question == None:
                questions = Question.objects.all()
                q = random.choice(questions)
                room.current_question = q
                room.save()

            Group('game-'+label).send({'text':json.dumps({
                "response_type":"send_answer",
                "answer":room.current_question.answer,
            })});

    elif(data['request_type'] == 'set_category'):
        room.category = data['content']
        room.save()

        create_message("set_category", f"The category is now <strong><i>{room.category}</i></strong>", room)
        Group('game-'+label).send(get_response_json(room))

    elif(data['request_type'] == 'reset_score'):
        p = room.players.get(player_id=data['player_id'])
        p.score = 0
        p.save()

        create_message("reset_score", f"<strong>{p.name}</strong> has reset their score", room)
        Group('game-'+label).send(get_response_json(room))

@channel_session
def ws_disconnect(message):
    label = message.channel_session['room']
    Group('game-'+label).discard(message.reply_channel)

# === Helper methods ===

def update_time_state(room):
    """Checks time and updates state"""
    if not room.state == 'contest':
        if datetime.datetime.now().timestamp() >= room.end_time:
            room.state = 'idle'
            room.save()

def get_response_json(room):
    """Generates json for update response"""

    return {'text':json.dumps({
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
    })}

def create_message(tag, content, room):
    m = Message(content=content, room=room, tag=tag)
    m.save()
