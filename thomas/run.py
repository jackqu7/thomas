import asyncio
from thomas.controller import FatController

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    fc = FatController(loop)
    fc.run()
    loop.run_forever()
