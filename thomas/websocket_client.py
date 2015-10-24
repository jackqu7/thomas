import asyncio
import websockets
import json


class WebsocketClient(object):

    RECONNECT_WAIT = 3

    URL = 'ws://192.168.0.7:5000/'

    def __init__(self, queue):
        self.queue = queue

    @asyncio.coroutine
    def run(self):
        while True:
            try:
                print('Attempting to connect')
                self.websocket = yield from websockets.connect(self.URL)
                print('Connected')
                while True:
                    message = yield from self.websocket.recv()
                    if message is None:
                        break
                    message = json.loads(message)
                    self.queue.put_nowait(message)

                yield from self.websocket.close()
            except Exception as e:
                print('Caught %s' % e)
            print('Lost connection')
            yield from asyncio.sleep(self.RECONNECT_WAIT)
