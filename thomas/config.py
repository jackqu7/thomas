import yaml
import os
from collections import OrderedDict
from .berth import (
    BerthController, PriorityBerthController, FringeBerthController)
from .output import Display
from .util import get_config_filename


def _get_berths(file_or_string):
    data = yaml.load(file_or_string)
    output = OrderedDict()
    for datum in data:
        output[datum['id']] = datum
    return output


def get_berths():
    config_dir = os.environ.get('THOMAS_CONFIG', 'stevenage')
    berth_filename = get_config_filename(config_dir, 'berths.yml')
    return _get_berths(open(berth_filename))


def _get_displays(berths, display_file_or_string):
    displays = yaml.load(display_file_or_string)
    output = []
    for display_data in displays:
        type = display_data.get('type')
        if type == 'PRIORITY':
            display_cls = PriorityBerthController
        elif type == 'FRINGE':
            display_cls = FringeBerthController
        else:
            display_cls = BerthController

        display_berths = [berths[berth_id] for berth_id in display_data['berths']]

        controller = display_cls(*display_berths)

        display = Display(
            id=display_data['id'],
            port=display_data['port'],
            device=display_data['device'],
            controller=controller,
            ss=display_data.get('ss'),
            drawer_kwargs=display_data.get('kwargs')
        )

        output.append(display)

    return output


def get_displays():
    config_dir = os.environ.get('THOMAS_CONFIG', 'stevenage')
    display_filename = get_config_filename(config_dir, 'displays.yml')
    return _get_displays(get_berths(), open(display_filename))
