from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'home/', views.home),
    url(r'^(?P<name>^[a-z0-9_-]+)/$', views.game_room),
]
