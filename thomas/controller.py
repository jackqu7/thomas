import asyncio
from collections import OrderedDict

from .async_output import AsyncOutput
from .input import Input
from .berth import Berth, PriorityBerth, FringeBerth
from .websocket_client import WebsocketClient
from .drawer import HeadcodeDrawer


class FatController(object):

    B = {
        '0659': {
            'id': '0659',
            'desc': 'Stevenage Arr',
            'distance': 0,
        },
        '0660': {
            'id': '0660',
            'desc': 'Stevenage',
            'distance': 0,
        },
        '0665': {
            'id': '0665',
            'desc': 'Stevenage',
            'distance': 0,
        },
        '0669': {
            'id': '0669',
            'desc': 'Stevenage Dep',
            'distance': 0,
        },

        '0661': {
            'id': '0661',
            'desc': 'Stevenage Arr',
            'distance': 0,
        },
        '0667': {
            'id': '0667',
            'desc': 'Stevenage',
            'distance': 0,
        },
        '0671': {
            'id': '0671',
            'desc': 'Stevenage Dep',
            'distance': 0,
        },

        '0656': {
            'id': '0656',
            'desc': 'Stevenage Dep',
            'distance': 0,
        },
        '0662': {
            'id': '0662',
            'desc': 'Stevenage',
            'distance': 0,
        },
        '0666': {
            'id': '0666',
            'desc': 'Stevenage Arr',
            'distance': 0,
        },

        '0658': {
            'id': '0658',
            'desc': 'Stevenage Dep',
            'distance': 0,
        },
        '0664': {
            'id': '0664',
            'desc': 'Stevenage',
            'distance': 0,
        },
        '0668': {
            'id': '0668',
            'desc': 'Stevenage Arr',
            'distance': 0,
        },

        '0939': {
            'id': '0939',
            'desc': 'Langley Junc',
            'distance': 1,
        },

        '0651': {
            'id': '0651',
            'desc': 'Knebworth Dep',
            'distance': 1,
        },
        '0637': {
            'id': '0637',
            'desc': 'Knebworth',
            'distance': 2,
        },
        '0633': {
            'id': '0633',
            'desc': 'Knebworth Arr',
            'distance': 3,
        },

        '0653': {
            'id': '0653',
            'desc': 'Knebworth Dep',
            'distance': 1,
        },
        '0639': {
            'id': '0639',
            'desc': 'Knebworth',
            'distance': 2,
        },
        '0635': {
            'id': '0635',
            'desc': 'Knebworth Arr',
            'distance': 3,
        },


        '0629': {
            'id': '0629',
            'desc': 'Woolmer Green Junc',
            'distance': 4,
        },
        '0627': {
            'id': '0627',
            'desc': 'Welwyn North Tunnel',
            'distance': 5,
        },
        '0625': {
            'id': '0625',
            'desc': 'Welwyn South Tunnel',
            'distance': 6,
        },
        '0623': {
            'id': '0623',
            'desc': 'Welwyn North',
            'distance': 7,
        },

        '0672': {
            'id': '0672',
            'desc': 'North Stevenage',
            'distance': 1,
        },
        '0676': {
            'id': '0676',
            'desc': 'Little Wymondley',
            'distance': 2,
        },
        '0684': {
            'id': '0684',
            'desc': 'Great Wymondley',
            'distance': 3,
        },
        '0688': {
            'id': '0688',
            'desc': 'Hitchin Dep',
            'distance': 4,
        },
        '0696': {
            'id': '0696',
            'desc': 'Hitchin',
            'distance': 5,
        },
        '0708': {
            'id': '0708',
            'desc': 'Hitchin Arr',
            'distance': 6,
        },
        '0712': {
            'id': '0712',
            'desc': 'North Hitchin',
            'distance': 7,
        },


        '0674': {
            'id': '0674',
            'desc': 'North Stevenage',
            'distance': 1,
        },
        '0678': {
            'id': '0678',
            'desc': 'Little Wymondley',
            'distance': 2,
        },
        '0686': {
            'id': '0686',
            'desc': 'Great Wymondley',
            'distance': 3,
        },
        '0690': {
            'id': '0690',
            'desc': 'Hitchin Dep',
            'distance': 4,
        },
        '0698': {
            'id': '0698',
            'desc': 'Hitchin',
            'distance': 5,
        },
        '0701': {
            'id': '0701',
            'desc': 'Hitchin',
            'distance': 5,
        },
        '0710': {
            'id': '0710',
            'desc': 'Hitchin Arr',
            'distance': 6,
        },
        '0714': {
            'id': '0714',
            'desc': 'North Hitchin',
            'distance': 7,
        },

        '0944': {
            'id': '0944',
            'desc': 'Cambridge Junction',
            'distance': 6,
        },
        '0946': {
            'id': '0946',
            'desc': 'Letchworth Dep',
            'distance': 7,
        },


    }

    DISPLAY_BERTHS = OrderedDict((
        (11, FringeBerth(B['0659'], B['0939'], B['0651'], B['0637'], B['0633'], B['0629'], B['0627'], B['0625'], B['0623'])),
        (1, PriorityBerth(B['0660'], alt=B['0665'])),
        (0, Berth(B['0669'])),

        (2, FringeBerth(B['0661'], B['0653'], B['0639'], B['0635'], B['0629'], B['0627'], B['0625'], B['0623'])),
        (3, Berth(B['0667'])),
        (4, Berth(B['0671'])),

        (5, Berth(B['0656'])),
        (6, Berth(B['0662'])),
        (7, FringeBerth(B['0666'], B['0672'], B['0676'], B['0684'], B['0688'], B['0696'], B['0708'], B['0712'])),

        (10, Berth(B['0658'])),
        (9, Berth(B['0664'])),
        (8, FringeBerth(B['0668'], B['0668'], B['0674'], B['0678'], B['0686'], B['0690'], B['0698'], B['0701'], B['0710'], B['0714'], B['0944'], B['0946'])),
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
