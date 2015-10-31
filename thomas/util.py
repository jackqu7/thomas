from os.path import dirname, realpath


def get_filename(dir, name):
    parent = dirname(dirname(realpath(__file__)))
    return '%s/%s/%s' % (parent, dir, name)


def get_asset_filename(name):
    return get_filename('assets', name)


def get_config_filename(dir, name):
    dir = 'config/%s' % dir
    return get_filename(dir, name)
