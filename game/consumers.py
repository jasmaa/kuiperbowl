from django.utils import timezone
from channels import Group
from channels.sessions import channel_session
from .models import *
import json

@channel_session
def ws_connect(message):
    # add user if new to room players

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
        Group('game-'+label).send({'text':{
            "game_state":room.game_state,
            "current_time":timezone.now(),
            "start_time":room.start_time,
            "end_time":room.end_time,
            "current_question_content":room.current_question.content,
            "score_dict":{},
        }})
    else if(data['request_type'] == 'buzz'):
        pass

@channel_session
def ws_disconnect(message):
    label = message.channel_session['room']
    Group('chat-'+label).discard(message.reply_channel)
