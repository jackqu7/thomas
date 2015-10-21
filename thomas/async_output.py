import asyncio
import time

from concurrent.futures import ThreadPoolExecutor

from .output import Output


class AsyncOutput(Output):
    def __init__(self, loop, *args, **kwargs):
        super(AsyncOutput, self).__init__(*args, **kwargs)
        self.loop = loop
        self.lock = asyncio.Lock()

    def flush_display_queue(self):
        if len(self.display_queue) == 0:
            return

        yield from self.lock.acquire()

        start_time = time.time()

        sup = super(AsyncOutput, self).flush_display_queue
        if self.type == 'tft':
            yield from self.loop.run_in_executor(
                ThreadPoolExecutor(max_workers=1), sup)
        else:
            sup()

        end_time = time.time()
        print("time: %s" % str(end_time - start_time))

        self.lock.release()
