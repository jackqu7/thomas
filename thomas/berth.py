from .drawer import Drawer


class Berth(object):
    def __init__(self, berth_id):
        self.berth_id = berth_id
        self.train = None

    def _is_different(self, train):
        if train and self.train:
            return train['headcode'] != self.train['headcode']
        else:
            return train and not self.train or not train and self.train

    def set(self, berth_id, train):
        if berth_id == self.berth_id:
            if self._is_different(train):
                self.train = train
                return self.draw()

    def draw(self):
        if self.train:
            return Drawer().headcode(self.train['headcode'])
        else:
            return Drawer().blank()
