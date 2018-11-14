from channels.routing import route

channel_routing = [
    route("http.request", "game.consumers.http_consumer"),
]
