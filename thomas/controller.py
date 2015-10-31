import asyncio

from .config import get_displays
from .async_output import AsyncOutput
from .input import Input
from .websocket_client import WebsocketClient
from .drawer import HeadcodeDrawer, FringeDrawer


class FatController(object):

    TICK_RATE = 5

    def __init__(self, loop):
        self.loop = loop

        self.displays = get_displays(
            open('config/berths.yml'), open('config/displays.yml'))
        self.output = AsyncOutput(loop, self.displays)

        self.ws_queue = asyncio.Queue()
        self.ws_client = WebsocketClient(self.ws_queue)

        self.drawer = FringeDrawer

        self.ir_input = Input(loop)
        self.ir_input.add_callback('b_up', self.output.brightness_up)
        self.ir_input.add_callback('b_down', self.output.brightness_down)
        self.ir_input.add_callback(
            'm1',
            lambda: self.set_drawer(HeadcodeDrawer))
        self.ir_input.add_callback(
            'm2',
            lambda: self.set_drawer(FringeDrawer))

        self.status = {}

    def run(self):
        asyncio.async(self.ws_client.run())
        asyncio.async(self.ir_input.run())

        asyncio.async(self.tick())
        asyncio.async(self.ws_queue_handler())

    def set_drawer(self, drawer):
        self.drawer = drawer
        asyncio.async(self._set_drawer())

    @asyncio.coroutine
    def _set_drawer(self):
        yield from self.call_all_berths_and_draw()

    def call_all_berths_and_draw(self, controller_caller=None, flush=True):
        for display in self.displays:
            if controller_caller:
                update = controller_caller(display.controller)
            else:
                update = True
            if update:
                train_to_draw = display.controller.get_current_train()
                drawer = self.drawer(train_to_draw, **display.drawer_kwargs)
                im = drawer.draw()
                self.output.queue_display_update(im, display)
        if flush:
            yield from self.output.flush_display_queue()

    @asyncio.coroutine
    def tick(self):
        while True:
            yield from self.call_all_berths_and_draw(lambda b: b.tick())
            yield from asyncio.sleep(self.TICK_RATE)

    @asyncio.coroutine
    def ws_queue_handler(self):
        while True:
            message = yield from self.ws_queue.get()
            self.status.update(message)
            yield from self.update()

    def update(self):
        for berth_id, train in self.status.items():
            yield from self.call_all_berths_and_draw(
                lambda b: b.set(berth_id, train),
                flush=False)
        yield from self.output.flush_display_queue()
