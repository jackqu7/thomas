import os
import asyncio
import multiprocessing
import sys
import logging
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
        def __init__(self, loop):
            self.loop = loop

        def get_next_code(self, q):
            return (yield from self.loop.run_in_executor(
                ThreadPoolExecutor(max_workers=1),
                    q.get))

        def run(self, message_queue):
            m = multiprocessing.Manager()
            q = m.Queue()

            self.loop.run_in_executor(ProcessPoolExecutor(max_workers=1),
                                      lirc_process, q)
            asyncio.async(self._run(q, message_queue))

        @asyncio.coroutine
        def _run(self, q, message_queue):
            while True:
                result = yield from self.get_next_code(q)
                for code in result:
                    message_queue.put_nowait(code)

else:
    class InputStdin(object):
        def __init__(self, loop):
            self.loop = loop

        def got_stdin_data(self, message_queue):
            asyncio.async(message_queue.put(sys.stdin.readline().strip()))

        def run(self, message_queue):
            self.loop.add_reader(sys.stdin, self.got_stdin_data, message_queue)


class Input(object):
    def __init__(self, loop):
        is_arm = os.uname()[4][:3] == 'arm'
        self.input = InputLIRC(loop) if is_arm else InputStdin(loop)
        self.callbacks = {}

    @asyncio.coroutine
    def run(self):
        message_queue = asyncio.Queue()
        self.input.run(message_queue)
        while True:
            result = yield from message_queue.get()
            logger.info('Got input "%s"', result)
            if result in self.callbacks:
                self.callbacks[result]()

    def add_callback(self, code, callback):
        self.callbacks[code] = callback
