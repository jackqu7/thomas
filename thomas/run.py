import logging
import asyncio
from thomas.controller import FatController

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s:%(message)s')
    logger = logging.getLogger('thomas')
    logger.setLevel(logging.DEBUG)
    loop = asyncio.get_event_loop()
    fc = FatController(loop)
    fc.run()
    loop.run_forever()
