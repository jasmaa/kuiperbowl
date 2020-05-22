import pytest

from .models import *
from django.core.management import call_command


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        Question.objects.create(
            pk=1,
            category="Literature",
            points=20,
            content="Test content",
            answer="Test answer",
            duration=23.6,
            difficulty="HS",
        )

        Room.objects.create(
            label='testroom',
        )

        Player.objects.create(
            user=User.objects.create(
                user_id=1,
                name="chad"
            ),
            room=Room.objects.get(label='testroom'),
            last_seen=datetime.datetime.now().timestamp(),
        )
        
        Player.objects.create(
            user=User.objects.create(
                user_id=2,
                name="vivian",
            ),
            room=Room.objects.get(label='testroom'),
        )
