from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r"(?P<label>^[a-z0-9_-]+)/$", views.game_room, name="game_room"),
]
