from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^(?P<label>^[a-z0-9_-]+)/$', views.game_room, name='game_room'),
]
