import asyncio
from collections import OrderedDict

from .async_output import AsyncOutput
from .input import Input
from .berth import Berth, PriorityBerth
from .websocket_client import WebsocketClient
from .drawer import HeadcodeDrawer


class FatController(object):

    DISPLAY_BERTHS = OrderedDict((
        (0, Berth('0659')),
        (1, PriorityBerth('0660', alt='0665')),
        (11, Berth('0669')),
        (4, Berth('0661')),
        (3, Berth('0667')),
        (2, Berth('0671')),
        (7, Berth('0656')),
        (6, Berth('0662')),
        (5, Berth('0666')),
        (10, Berth('0658')),
        (9, Berth('0664')),
        (8, Berth('0668')),
    ))

    def __init__(self, loop):
        self.loop = loop

        display_numbers = self.DISPLAY_BERTHS.keys()
        self.output = AsyncOutput(loop, display_numbers)

        self.ws_queue = asyncio.Queue()
        self.ws_client = WebsocketClient(self.ws_queue)

        self.ir_input = Input()
        self.ir_input.add_callback('b_up', self.output.brightness_up)
        self.ir_input.add_callback('b_down', self.output.brightness_down)

        self.status = {}

    @asyncio.coroutine
    def tick(self):
        while True:
            print('tick')
            yield from asyncio.sleep(1)

    @asyncio.coroutine
    def ws_queue_handler(self):
        while True:
            message = yield from self.ws_queue.get()
            print(message)
            self.status.update(message)
            yield from self.update()

    def run(self):
        asyncio.async(self.ws_client.run())
        asyncio.async(self.ir_input.run())

        asyncio.async(self.tick())
        asyncio.async(self.ws_queue_handler())

    def update(self):

        for berth_id, train in self.status.items():

            # Tell all berths about this update, if they care about it they'll
            # return True and we'll then draw their new current_train
            for display_number, berth in self.DISPLAY_BERTHS.items():
                changed = berth.set(berth_id, train)
                if changed:
                    train_to_draw = berth.get_current_train()
                    im = HeadcodeDrawer(train_to_draw).draw()
                    self.output.queue_display_update(im, display_number)

        yield from self.output.flush_display_queue()
