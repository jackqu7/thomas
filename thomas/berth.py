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

    def tick(self):
        pass


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


class FringeBerth(Berth):
    def __init__(self, berth_id, *look_back_ids):
        self.look_back_ids = look_back_ids
        self.fringe_trains = {}
        self.train = None
        self.counter = 0
        super(FringeBerth, self).__init__(berth_id)

    def set(self, berth_id, train):
        if berth_id == self.berth_id:
            self.train = train

        if berth_id in self.look_back_ids:
            self.fringe_trains[berth_id] = train

        # If there's not, let choose_current_train decide what to do
        return self.choose_current_train()

    def _is_different(self, train1, train2):
        if train1 and train2:
            return train1['headcode'] != train2['headcode'] or \
                train1.get('is_fringe') != train2.get('is_fringe')
        else:
            return train1 and not train2 or not train1 and train2

    def choose_current_train(self):
        # If there's a train in the main berth, always show it
        if self.train:
            current_train = self.train
            current_train['is_fringe'] = False
        else:
            # Otherwise show the active fringe train
            active_trains = list(self._active_fringe_trains())

            if len(active_trains) == 0:
                current_train = None
            else:
                if self.counter > len(active_trains) - 1:
                    self.counter = 0
                current_train = active_trains[self.counter]
                current_train['is_fringe'] = True

        if self._is_different(current_train, self.current_train):
            self.current_train = current_train
            return True

    def _active_fringe_trains(self):
        for fringe_id in self.look_back_ids:
            fringe_train = self.fringe_trains.get(fringe_id)
            if fringe_train:
                yield fringe_train

    def tick(self):
        res = self.choose_current_train()

        self.counter += 1

        return res
