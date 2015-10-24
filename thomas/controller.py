import asyncio

from .config import BERTHS as B
from .async_output import AsyncOutput
from .input import Input
from .berth import Berth, PriorityBerth, FringeBerth
from .websocket_client import WebsocketClient
from .drawer import HeadcodeDrawer, FringeDrawer


class FatController(object):

    DISPLAY_BERTHS = (
        (11, {'progress_orientation': FringeDrawer.LEFT}, FringeBerth(B['0659'], B['0939'], B['0651'], B['0637'], B['0633'], B['0629'], B['0627'], B['0625'], B['0623'])),
        (1, {}, PriorityBerth(B['0660'], alt=B['0665'])),
        (0, {}, Berth(B['0669'])),
        (2, {'progress_orientation': FringeDrawer.LEFT}, FringeBerth(B['0661'], B['0653'], B['0639'], B['0635'], B['0629'], B['0627'], B['0625'], B['0623'])),
        (3, {}, Berth(B['0667'])),
        (4, {}, Berth(B['0671'])),
        (5, {}, Berth(B['0656'])),
        (6, {}, Berth(B['0662'])),
        (7, {}, FringeBerth(B['0666'], B['0672'], B['0676'], B['0684'], B['0688'], B['0696'], B['0708'], B['0712'])),
        (10, {}, Berth(B['0658'])),
        (9, {}, Berth(B['0664'])),
        (8, {}, FringeBerth(B['0668'], B['0668'], B['0674'], B['0678'], B['0686'], B['0690'], B['0698'], B['0701'], B['0710'], B['0714'], B['0944'], B['0946'])),
    )

    TICK_RATE = 5

    def __init__(self, loop):
        self.loop = loop

        display_numbers = [num for num, _, _ in self.DISPLAY_BERTHS]
        self.output = AsyncOutput(loop, display_numbers)

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

    def call_all_berths_and_draw(self, berth_caller=None, flush=True):
        for display_number, kwargs, berth in self.DISPLAY_BERTHS:
            if berth_caller:
                update = berth_caller(berth)
            else:
                update = True
            if update:
                train_to_draw = berth.get_current_train()
                drawer = self.drawer(train_to_draw, **kwargs)
                im = drawer.draw()
                self.output.queue_display_update(im, display_number)
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
