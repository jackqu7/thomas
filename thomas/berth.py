class Berth(object):
    def __init__(self, berth):
        self.berth_id = berth['id']
        self.current_train = None

    def _is_different(self, train1, train2):
        if train1 and train2:
            return train1['headcode'] != train2['headcode']
        else:
            return train1 and not train2 or not train1 and train2

    def _copy_train(self, train, **extra):
        if train:
            return dict(train, **extra)

    def set(self, berth_id, train):
        if berth_id == self.berth_id:
            if self._is_different(train, self.current_train):
                self.current_train = self._copy_train(train)
                return True

    def get_current_train(self):
        return self.current_train

    def tick(self):
        pass


class PriorityBerth(Berth):
    def __init__(self, berth, alt=None):
        self.alt_berth_id = alt['id']
        self.train = None
        self.alt_train = None
        super(PriorityBerth, self).__init__(berth)

    def set(self, berth_id, train):
        if berth_id == self.berth_id:
            self.train = self._copy_train(train)
        if berth_id == self.alt_berth_id:
            self.alt_train = self._copy_train(train)

        current_train = self.train or self.alt_train
        if self._is_different(current_train, self.current_train):
            self.current_train = self._copy_train(current_train)
            return True


class FringeBerth(Berth):
    def __init__(self, berth, *look_back_berths):
        self.look_back_berths = {}
        for b in look_back_berths:
            self.look_back_berths[b['id']] = b
        self.fringe_trains = {}
        self.train = None
        self.counter = 0
        super(FringeBerth, self).__init__(berth)

    def set(self, berth_id, train):
        if berth_id == self.berth_id:
            self.train = self._copy_train(train, is_fringe=False)

        if berth_id in self.look_back_berths:
            self.fringe_trains[berth_id] = \
                self._copy_train(train, is_fringe=True)

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
        else:
            # Otherwise show the active fringe train
            active_trains = list(self._active_fringe_trains())

            if len(active_trains) == 0:
                current_train = None
            else:
                if self.counter > len(active_trains) - 1:
                    self.counter = 0
                current_train = active_trains[self.counter]

        if self._is_different(current_train, self.current_train):
            self.current_train = current_train
            return True

    def _active_fringe_trains(self):
        for fringe_id in self.look_back_berths:
            fringe_train = self.fringe_trains.get(fringe_id)
            if fringe_train:
                yield fringe_train

    def tick(self):
        res = self.choose_current_train()

        self.counter += 1

        return res
