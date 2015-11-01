import asyncio
import logging

from .config import get_displays
from .async_output import AsyncOutput
from .input import Input
from .websocket_client import WebsocketClient
from .drawer import HeadcodeDrawer, FringeDrawer

logger = logging.getLogger(__name__)


class FatController(object):

    TICK_RATE = 5

    FLASH_TIME = 5

    MODE_DRAWERS = {
        'm1': FringeDrawer,
        'm2': HeadcodeDrawer,
    }

    def __init__(self, loop):
        logger.debug('Controller init')
        self.loop = loop

        self.displays = get_displays()
        self.output = AsyncOutput(loop, self.displays)

        self.ws_queue = asyncio.Queue()
        self.ws_client = WebsocketClient(self.ws_queue)

        self.drawer = FringeDrawer

        self.ir_input = Input(loop)
        self.ir_input.add_callback('b_up', self.output.brightness_up)
        self.ir_input.add_callback('b_down', self.output.brightness_down)
        self.ir_input.add_callback('m1', lambda: self.set_mode('m1'))
        self.ir_input.add_callback('m2', lambda: self.set_mode('m2'))

        self.status = {}
        self.message = None
        self._flash_sleep = None

    def run(self):
        logger.info('Thomas Starting')
        asyncio.async(self.ws_client.run())
        asyncio.async(self.ir_input.run())

        asyncio.async(self.tick())
        asyncio.async(self.ws_queue_handler())

    @asyncio.coroutine
    def _set_message(self, msg):
        logger.debug('Set message "%s"', msg)
        self.message = msg
        yield from self.update_displays_immediately()

    @asyncio.coroutine
    def _clear_message(self):
        logger.debug('Clear message')
        self.message = None
        yield from self.update_displays_immediately()

    @asyncio.coroutine
    def _flash_message(self, msg):
        # this breaks if two are flashed at a similar time
        yield from self._set_message(msg)

        # If there is an existing message, cancel it being cleared
        if self._flash_sleep:
            self._flash_sleep.cancel()

        # Sleep until we need to clear the message
        self._flash_sleep = asyncio.async(asyncio.sleep(self.FLASH_TIME))
        try:
            yield from self._flash_sleep
            yield from self._clear_message()
            self._flash_sleep = None
        except asyncio.CancelledError:
            # The clear was cancelled because another message was flashed
            # before we woke up, so do nothing
            pass

    def set_message(self, msg):
        asyncio.async(self._set_message(msg))

    def clear_message(self):
        asyncio.async(self._clear_message())

    def flash_message(self, msg):
        asyncio.async(self._flash_message(msg))

    def set_mode(self, mode):
        logger.debug('Set mode %s', mode)
        drawer = self.MODE_DRAWERS[mode]
        self.drawer = drawer
        # No need to redraw because flash_message will do it for us
        self.flash_message('Mode: %s' % drawer.name)

    @asyncio.coroutine
    def update_displays_immediately(self):
        logger.debug('Update immediately')
        yield from self.call_all_berths_and_draw()

    def call_all_berths_and_draw(self, controller_caller=None, flush=True):
        for display in self.displays:
            if controller_caller:
                update = controller_caller(display.controller)
            else:
                update = True
            if update:
                train_to_draw = display.controller.get_current_train()
                drawer = self.drawer(train_to_draw, message=self.message,
                                     **display.drawer_kwargs)
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
