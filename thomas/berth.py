class Berth(object):
    def __init__(self, berth_id):
        self.berth_id = berth_id
        self.current_train = None

    def _is_different(self, train1, train2):
        if train1 and train2:
            return train1['headcode'] != train2['headcode']
        else:
            return train1 and not train2 or not train1 and train2

    def set(self, berth_id, train):
        if berth_id == self.berth_id:
            if self._is_different(train, self.current_train):
                self.current_train = train
                return True

    def get_current_train(self):
        return self.current_train


class PriorityBerth(Berth):
    def __init__(self, berth_id, alt=None):
        self.alt_berth_id = alt
        self.train = None
        self.alt_train = None
        super(PriorityBerth, self).__init__(berth_id)

    def set(self, berth_id, train):
        if berth_id == self.berth_id:
            self.train = train
        if berth_id == self.alt_berth_id:
            self.alt_train = train

        current_train = self.train or self.alt_train
        if self._is_different(current_train, self.current_train):
            self.current_train = current_train
            return True
