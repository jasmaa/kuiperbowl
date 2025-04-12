from django.shortcuts import render
from .models import *


# Create your views here.
def home(request):
    return render(request, "game/home.html", {})


def game_room(request, label):
    room, created = Room.objects.get_or_create(label=label)

    return render(
        request,
        "game/game.html",
        {
            "room": room,
        },
    )
