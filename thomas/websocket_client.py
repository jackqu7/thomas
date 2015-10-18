import asyncio
import websockets
import json


class WebsocketClient(object):

    URL = 'ws://192.168.0.7:5000/'

    def __init__(self, queue):
        self.queue = queue

    @asyncio.coroutine
    def run(self):
        self.websocket = yield from websockets.connect(self.URL)

        while True:
            message = yield from self.websocket.recv()
            if message is None:
                break
            message = json.loads(message)
            self.queue.put_nowait(message)

        yield from self.websocket.close()
