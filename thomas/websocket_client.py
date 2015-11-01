import asyncio
import websockets
import json
import logging

logger = logging.getLogger(__name__)


class WebsocketClient(object):

    RECONNECT_WAIT = 3

    URL = 'ws://192.168.0.7:5000/'

    def __init__(self, queue):
        self.queue = queue

    @asyncio.coroutine
    def run(self):
        while True:
            try:
                logger.info('Attempting to connect')
                self.websocket = yield from websockets.connect(self.URL)
                logger.info('Connected')
                while True:
                    message = yield from self.websocket.recv()
                    if message is None:
                        break
                    message = json.loads(message)
                    self.queue.put_nowait(message)

                yield from self.websocket.close()
            except Exception as e:
                logger.error(e)
            logger.warning('Lost connection')
            yield from asyncio.sleep(self.RECONNECT_WAIT)
