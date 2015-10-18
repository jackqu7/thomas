from os.path import dirname, realpath


def get_asset_filename(name):
    parent = dirname(dirname(realpath(__file__)))
    return '%s/assets/%s' % (parent, name)
