import asyncio
import websockets
import json
import logging

logger = logging.getLogger(__name__)


class WebsocketClient(object):

    RECONNECT_WAIT = 3

    URL = 'ws://trainspotter.reeves.io/'

    def __init__(self, queue, on_connect=None, on_disconnect=None):
        self.queue = queue
        self.on_connect = on_connect
        self.on_disconnect = on_disconnect

    def _on_connect(self):
        if self.on_connect:
            self.on_connect()

    def _on_disconnect(self):
        if self.on_disconnect:
            self.on_disconnect()

    @asyncio.coroutine
    def run(self):
        while True:
            try:
                logger.info('Attempting to connect')
                self.websocket = yield from websockets.connect(self.URL)

                logger.info('Connected')
                self._on_connect()

                while True:
                    message = yield from self.websocket.recv()
                    if message is None:
                        break
                    message = json.loads(message)
                    self.queue.put_nowait(message)

                yield from self.websocket.close()
            except Exception as e:
                logger.error(e)

            logger.warning('Connection lost')
            self._on_disconnect()

            yield from asyncio.sleep(self.RECONNECT_WAIT)
