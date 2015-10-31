import yaml
import os
from collections import OrderedDict
from .berth import (
    BerthController, PriorityBerthController, FringeBerthController)
from .output import Display
from .util import get_config_filename


def load_yaml(file_or_string):
    data = yaml.load(file_or_string)
    output = OrderedDict()
    for datum in data:
        output[datum['id']] = datum
    return output


def _get_displays(berth_file_or_string, display_file_or_string):
    berths = load_yaml(berth_file_or_string)
    displays = load_yaml(display_file_or_string) # no need for this to be a dict
    output = []
    for id, display_data in displays.items():
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
    berth_filename = get_config_filename(config_dir, 'berths.yml')
    display_filename = get_config_filename(config_dir, 'displays.yml')
    return _get_displays(open(berth_filename), open(display_filename))
