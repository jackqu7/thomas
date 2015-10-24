from collections import OrderedDict


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
        self.look_back_berths = OrderedDict()
        self.max_berth_distance = 1
        for b in look_back_berths:
            self.look_back_berths[b['id']] = b
            if b['distance'] > self.max_berth_distance:
                self.max_berth_distance = b['distance']
        self.fringe_trains = {}
        self.train = None
        self.current_fringe_berth_id = None
        super(FringeBerth, self).__init__(berth)

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

            # XXX: this is whack
            if train and not self.current_fringe_berth_id:
                self.current_fringe_berth_id = berth_id
            elif not train and self.current_fringe_berth_id == berth_id:
                self.set_next_fringe_id()

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
            fringe = self.fringe_trains.get(self.current_fringe_berth_id)
            current_train = fringe

        if self._is_different(current_train, self.current_train):
            self.current_train = current_train
            return True

    def _active_fringe_berths(self):
        return [fringe_id
                for fringe_id in self.look_back_berths
                if self.fringe_trains.get(fringe_id)]

    def set_next_fringe_id(self):
        # Get all berths, in order, that have a train in them
        active_berths = self._active_fringe_berths()

        if len(active_berths) == 0:
            # There are no active berths, so show nothing
            self.current_fringe_berth_id = None
            return

        if self.current_fringe_berth_id in active_berths:
            # The berth we're currently showing still has a train in it.

            if len(active_berths) == 1:
                # This is the only train available, so keep showing it
                return

            # More trains are available, so find the next one

            # Find out where we are currently
            current_index = active_berths.index(self.current_fringe_berth_id)

            if current_index < len(active_berths) - 1:
                # If we're not at the end of the list, get the next index
                next_berth = active_berths[current_index + 1]
            else:
                # Otherwise, wrap back round to the start
                next_berth = active_berths[0]
            self.current_fringe_berth_id = next_berth
        else:
            # The berth we're currently showing is now empty.

            if len(active_berths) > 0:
                self.current_fringe_berth_id = active_berths[0]
            else:
                self.current_fringe_berth_id = None

    def tick(self):
        self.set_next_fringe_id()

        res = self.choose_current_train()

        return res
