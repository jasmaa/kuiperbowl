import json
import pytest
from channels.routing import  URLRouter
from channels.testing import WebsocketCommunicator
from django.urls import re_path
from ..consumers import QuizbowlConsumer

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_quizbowl_consumer():
    application = URLRouter([
        re_path(r'ws/game/(?P<label>[a-z0-9_-]+)/$', QuizbowlConsumer.as_asgi()),
    ])
    communicator = WebsocketCommunicator(application, "ws/game/testroom2/")
    connected, _ = await communicator.connect()
    assert connected

    # Join game
    raw_join_message = json.dumps({
        "request_type": "join",
        "user_id": "",
    })
    await communicator.send_to(text_data=raw_join_message)

    raw_new_user_message = await communicator.receive_from()
    new_user_message = json.loads(raw_new_user_message)

    assert new_user_message["response_type"] == "new_user"
    assert len(new_user_message["user_id"]) > 0
    assert len(new_user_message["user_name"]) > 0

    user_id = new_user_message["user_id"]

    # Ping room
    raw_ping_message = json.dumps({
        "request_type": "ping",
        "user_id": user_id,
    })
    await communicator.send_to(text_data=raw_ping_message)

    raw_update_message = await communicator.receive_from()
    update_message = json.loads(raw_update_message)

    assert update_message["response_type"] == "update"

    await communicator.disconnect()
