import os
import asyncio
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

from .util import get_asset_filename

has_lirc = True
try:
    import lirc
except ImportError:
    has_lirc = False

if has_lirc:

    def lirc_process(q):
        filename = get_asset_filename('lircrc')
        lirc.init('nr_view', filename, verbose=True)
        while True:
            q.put(lirc.nextcode())
        lirc.deinit()

    class InputLIRC(object):

        def get_next_code(self, q):
            loop = asyncio.get_event_loop()
            return (yield from loop.run_in_executor(ThreadPoolExecutor(max_workers=1),
                    q.get))

        @asyncio.coroutine
        def run(self, message_queue):
            m = multiprocessing.Manager()
            q = m.Queue()

            loop = asyncio.get_event_loop()
            loop.run_in_executor(ProcessPoolExecutor(max_workers=1),
                                 lirc_process, q)
            while True:
                result = yield from self.get_next_code(q)
                for code in result:
                    message_queue.put_nowait(code)

else:
    class InputDummy(object):
        @asyncio.coroutine
        def run(self, message_queue):
            yield


class Input(object):
    def __init__(self):
        is_arm = os.uname()[4][:3] == 'arm'
        self.input = InputLIRC() if is_arm else InputDummy()
        self.callbacks = {}

    @asyncio.coroutine
    def run(self):
        message_queue = asyncio.Queue()
        asyncio.async(self.input.run(message_queue))
        while True:
            result = yield from message_queue.get()
            print(result)
            if result in self.callbacks:
                self.callbacks[result]()

    def add_callback(self, code, callback):
        self.callbacks[code] = callback
