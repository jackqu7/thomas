import yaml
from collections import OrderedDict
from .berth import Berth, PriorityBerth, FringeBerth


def load_yaml(file_or_string):
    data = yaml.load(file_or_string)
    output = OrderedDict()
    for datum in data:
        output[datum['id']] = datum
    return output


def get_displays(berth_file_or_string, display_file_or_string):
    berths = load_yaml(berth_file_or_string)
    displays = load_yaml(display_file_or_string)
    output = []
    for id, display in displays.items():
        type = display.get('type')
        if type == 'PRIORITY':
            display_cls = PriorityBerth
        elif type == 'FRINGE':
            display_cls = FringeBerth
        else:
            display_cls = Berth

        display_berths = [berths[berth_id] for berth_id in display['berths']]

        output.append((
            id,
            display.get('kwargs', {}),
            display_cls(*display_berths)
        ))
    return output
