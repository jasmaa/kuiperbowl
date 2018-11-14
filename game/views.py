from django.shortcuts import render
from .models import *

# Create your views here.
def home(request):
    return render(request, "game/home.html",{

    })

def game_room(request, name):
    room, created = Room.objects.get_or_create(name=name)

    return render(request, "game/game.html",{
        "sanity":room,
    })
