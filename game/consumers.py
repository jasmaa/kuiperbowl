from channels import Group
from channels.sessions import channel_session
from .models import *
import json

@channel_session
def ws_connect(message):
    pass

@channel_session
def ws_receive(message):
    pass

@channel_session
def ws_disconnect(message):
    pass
