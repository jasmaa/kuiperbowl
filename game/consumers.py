from django.http import HttpResponse
from channels import Group
from channels.sessions import channel_session
from .models import *
import json
import datetime

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
        message.reply_channel.send({'text':json.dumps({
            "game_state":room.state,
            "current_time":datetime.datetime.now().timestamp(),
            "start_time":room.start_time.timestamp(),
            "end_time":room.end_time.timestamp(),
            "current_question_content": room.current_question.content if room.current_question != None else "",
            "score_dict":{},
        })})
    elif(data['request_type'] == 'buzz'):
        Group('chat-'+label).send({'text':json.dumps(m.as_dict())})
        pass

@channel_session
def ws_disconnect(message):
    label = message.channel_session['room']
    Group('chat-'+label).discard(message.reply_channel)
