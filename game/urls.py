from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'home/', views.home, name='home'),
    url(r'^(?P<label>^[a-z0-9_-]+)/$', views.game_room, name='game_room'),
]
