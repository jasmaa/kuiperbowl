from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'game/(?P<label>[a-z0-9_-]+)/$', consumers.QuizbowlConsumer),
]