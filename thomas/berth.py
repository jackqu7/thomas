from collections import OrderedDict


class BerthController(object):
    def __init__(self, berth):
        self.berth_id = berth['number']
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


class PriorityBerthController(BerthController):
    def __init__(self, berth, alt):
        self.alt_berth_id = alt['number']
        self.train = None
        self.alt_train = None
        super(PriorityBerthController, self).__init__(berth)

    def set(self, berth_id, train):
        if berth_id == self.berth_id:
            self.train = self._copy_train(train)
        if berth_id == self.alt_berth_id:
            self.alt_train = self._copy_train(train)

        current_train = self.train or self.alt_train
        if self._is_different(current_train, self.current_train):
            self.current_train = self._copy_train(current_train)
            return True


class FringeBerthController(BerthController):
    def __init__(self, berth, *look_back_berths):
        self.look_back_berths = OrderedDict()
        self.max_berth_distance = 1
        for b in look_back_berths:
            self.look_back_berths[b['number']] = b
            if b['distance'] > self.max_berth_distance:
                self.max_berth_distance = b['distance']
        self.fringe_trains = {}
        self.train = None
        self.current_fringe_berth_id = None
        super(FringeBerthController, self).__init__(berth)

    def _is_different(self, train1, train2):
        if train1 and train2:
            return train1['headcode'] != train2['headcode'] or \
                train1.get('is_fringe') != train2.get('is_fringe') or \
                train1.get('berth') != train2.get('berth')
        else:
            return train1 and not train2 or not train1 and train2

    def choose_current_train(self):
        # If there's a train in the main berth, always show it
        if self.train:
            current_train = self.train
        else:
            # Otherwise show the active fringe train
            fringe = self.fringe_trains.get(self.current_fringe_berth_id)
            current_train = fringe

        if self._is_different(current_train, self.current_train):
            self.current_train = current_train
            return True

    def _fringe_berth_ids(self):
        return list(self.look_back_berths.keys())

    def set_next_fringe_id(self):
        fringe_berth_ids = self._fringe_berth_ids()

        if self.current_fringe_berth_id:
            # If we're currently showing a fringe train, get the index of it
            # in the berth order
            current_index = fringe_berth_ids.index(
                self.current_fringe_berth_id)
        else:
            # Otherwise, set current_index to -1 so we start looking for trains
            # at berth 0
            current_index = -1

        # Go through the list of fringe berths until we find the next active
        # one, or we come back to ourselves
        for i in range(len(fringe_berth_ids)):
            current_index += 1
            if current_index == len(fringe_berth_ids):
                # Wrap around if we reached the end of the list
                current_index = 0
            current_id = fringe_berth_ids[current_index]
            if self.fringe_trains.get(current_id):
                self.current_fringe_berth_id = current_id
                return

        # If we got here, there are no active trains at all
        self.current_fringe_berth_id = None

    def tick(self):
        self.set_next_fringe_id()

        res = self.choose_current_train()

        return res

    def set(self, berth_id, train):
        if berth_id == self.berth_id:
            self.train = self._copy_train(train, is_fringe=False)

        if berth_id in self.look_back_berths:
            berth = self.look_back_berths[berth_id]
            distance_percent = berth['distance'] / self.max_berth_distance
            self.fringe_trains[berth_id] = \
                self._copy_train(
                    train,
                    is_fringe=True,
                    berth=berth,
                    distance_percent=distance_percent)

            if train and not self.current_fringe_berth_id:
                # We've got a new fringe train, but we're currently not
                # showing any fringe trains - so start showing it
                self.set_next_fringe_id()
            elif not train and self.current_fringe_berth_id == berth_id:
                # This berth has been cleared, but it's the one we're
                # currently showing, so move to the next fringe berth
                self.set_next_fringe_id()

        return self.choose_current_train()
