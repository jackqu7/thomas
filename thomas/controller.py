import asyncio
from collections import OrderedDict

from .async_output import AsyncOutput
from .input import Input
from .berth import Berth, PriorityBerth, FringeBerth
from .websocket_client import WebsocketClient
from .drawer import HeadcodeDrawer


class FatController(object):

    DISPLAY_BERTHS = OrderedDict((
        (11, FringeBerth('0659', '0651', '0637', '0633', '0629', '0627', '0625', '0623')),
        (1, PriorityBerth('0660', alt='0665')),
        (0, Berth('0669')),

        (2, FringeBerth('0661', '0653', '0639', '0635', '0629', '0627', '0625', '0623')),
        (3, Berth('0667')),
        (4, Berth('0671')),

        (5, Berth('0656')),
        (6, Berth('0662')),
        (7, FringeBerth('0666', '0672', '0676', '0684', '0688', '0696', '0708', '0712')),

        (10, Berth('0658')),
        (9, Berth('0664')),
        (8, FringeBerth('0668', '0668', '0674', '0678', '0686', '0690', '0698', '0701', '0944', '0946')),
    ))

    TICK_RATE = 5

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
            for display_number, berth in self.DISPLAY_BERTHS.items():
                changed = berth.tick()
                if changed:
                    train_to_draw = berth.get_current_train()
                    drawer = HeadcodeDrawer(train_to_draw)
                    im = drawer.draw()
                    print('drawing from tick', train_to_draw)
                    self.output.queue_display_update(im, display_number)

            yield from self.output.flush_display_queue()

            yield from asyncio.sleep(self.TICK_RATE)

    @asyncio.coroutine
    def ws_queue_handler(self):
        while True:
            message = yield from self.ws_queue.get()
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
                    print('drawing from update', train_to_draw)
                    self.output.queue_display_update(im, display_number)

        yield from self.output.flush_display_queue()
