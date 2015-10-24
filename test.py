import unittest
from thomas.berth import Berth, PriorityBerth, FringeBerth


def _berth_json(**params):
    params.setdefault('id', 'abc')
    params.setdefault('desc', 'desc')
    params.setdefault('distance', 0)
    return params


class BerthTests(unittest.TestCase):

    def test_is_different(self):
        berth = Berth(_berth_json())

        moorgate1 = {
            'headcode': '2F29'
        }
        moorgate2 = {
            'headcode': '2F29'
        }

        kings_cross1 = {
            'headcode': '1P29'
        }
        kings_cross2 = {
            'headcode': '1P29'
        }

        assert berth._is_different(moorgate1, kings_cross1)
        assert berth._is_different(kings_cross1, moorgate1)
        assert berth._is_different(moorgate1, None)
        assert berth._is_different(None, moorgate1)
        assert not berth._is_different(moorgate1, moorgate2)
        assert not berth._is_different(kings_cross2, kings_cross1)

    def test_set(self):
        berth = Berth(_berth_json(id='abc'))

        moorgate1 = {
            'headcode': '2F29'
        }
        kings_cross1 = {
            'headcode': '1P29'
        }

        # Should ignore other berths
        assert berth.set('xyz', moorgate1) is None
        assert berth.get_current_train() is None

        # Should update if given a train for it's berth
        assert berth.set('abc', kings_cross1) is True
        assert berth.get_current_train() == kings_cross1

        # Should ignore the same train again
        assert berth.set('abc', kings_cross1) is None
        assert berth.get_current_train() == kings_cross1

        # Should update if different train overwritten
        assert berth.set('abc', moorgate1) is True
        assert berth.get_current_train() == moorgate1

        # Should update if berth set back to None
        assert berth.set('abc', None) is True
        assert berth.get_current_train() is None


class PriorityBerthTests(unittest.TestCase):
    def test_set(self):
        berth = PriorityBerth(_berth_json(id='abc'), alt=_berth_json(id='efg'))

        moorgate1 = {
            'headcode': '2F29'
        }
        kings_cross1 = {
            'headcode': '1P29'
        }

        # Should ignore other berths
        assert berth.set('xyz', moorgate1) is None
        assert berth.get_current_train() is None

        # Should update if given a train for it's alt berth
        assert berth.set('efg', kings_cross1) is True
        assert berth.get_current_train() == kings_cross1

        # Should ignore the same train again
        assert berth.set('efg', kings_cross1) is None
        assert berth.get_current_train() == kings_cross1

        # Should switch to priority berth if set
        assert berth.set('abc', moorgate1) is True
        assert berth.get_current_train() == moorgate1

        # Should go back to first train if priority berth unset
        assert berth.set('abc', None) is True
        assert berth.get_current_train() == kings_cross1

        # Should show nothing if both unset
        assert berth.set('efg', None) is True
        assert berth.get_current_train() is None

        # Should show priority berth if only berth populated
        assert berth.set('abc', moorgate1) is True
        assert berth.get_current_train() == moorgate1

        # Should not update if alt berth set whilst priority berth populated
        assert berth.set('efg', kings_cross1) is None
        assert berth.get_current_train() == moorgate1


class FringeBerthTests(unittest.TestCase):
    def test_set(self):
        train_a = {
            'headcode': 'AAAA'
        }
        train_b = {
            'headcode': 'BBBB'
        }
        train_c = {
            'headcode': 'CCCC'
        }

        b_main = _berth_json(id='MAIN')
        b_f1 = _berth_json(id='F1', distance=1)
        b_f2 = _berth_json(id='F2', distance=2)
        b_f3 = _berth_json(id='F3', distance=3)
        b_f4 = _berth_json(id='F4', distance=4)

        # MAIN  F1  F2  F3
        # NEW   -   -   -   = NEW
        berth = FringeBerth(b_main, b_f1, b_f2, b_f3, b_f4)
        assert berth.set('MAIN', train_a) is True
        current_train_exp = dict(train_a, is_fringe=False)
        assert berth.get_current_train() == current_train_exp

        # MAIN  F1  F2  F3
        # -     -   -   NEW = NEW
        berth = FringeBerth(b_main, b_f1, b_f2, b_f3, b_f4)
        assert berth.set('F3', train_a) is True
        current_train_exp = dict(
            train_a,
            is_fringe=True,
            berth=b_f3,
            distance_percent=0.75)
        assert berth.get_current_train() == current_train_exp
        assert berth.fringe_trains == {'F3': current_train_exp}

        # MAIN  F1  F2  F3
        # A     -   NEW -   = A
        berth = FringeBerth(b_main, b_f1, b_f2, b_f3, b_f4)
        berth.set('MAIN', train_a)
        assert berth.set('F2', train_b) is None
        current_train_exp = dict(train_a, is_fringe=False)
        f2_exp = dict(
            train_b,
            is_fringe=True,
            berth=b_f2,
            distance_percent=0.5)
        assert berth.get_current_train() == current_train_exp
        assert berth.fringe_trains == {'F2': f2_exp}

        # MAIN  F1  F2  F3
        # NEW   -   A   -   = NEW
        berth = FringeBerth(b_main, b_f1, b_f2, b_f3, b_f4)
        berth.set('F2', train_a)
        assert berth.set('MAIN', train_b) is True
        current_train_exp = dict(train_b, is_fringe=False)
        assert berth.get_current_train() == current_train_exp

        # MAIN  F1  F2  F3
        # -     NEW -   A   = A
        berth = FringeBerth(b_main, b_f1, b_f2, b_f3, b_f4)
        berth.set('F3', train_a)
        assert berth.set('F1', train_b) is None
        f1_exp = dict(
            train_b,
            is_fringe=True,
            berth=b_f1,
            distance_percent=0.25)
        current_train_exp = dict(
            train_a,
            is_fringe=True,
            berth=b_f3,
            distance_percent=0.75)
        assert berth.get_current_train() == current_train_exp
        assert berth.fringe_trains == {
            'F1': f1_exp,
            'F3': current_train_exp}

        # MAIN  F1  F2  F3
        # B     NEW  -   A   = B
        berth = FringeBerth(b_main, b_f1, b_f2, b_f3, b_f4)
        berth.set('F3', train_a)
        berth.set('MAIN', train_b)
        assert berth.set('F1', train_c) is None
        current_train_exp = dict(train_b, is_fringe=False)
        f1_exp = dict(
            train_c,
            is_fringe=True,
            berth=b_f1,
            distance_percent=0.25)
        f3_exp = dict(
            train_a,
            is_fringe=True,
            berth=b_f3,
            distance_percent=0.75)
        assert berth.get_current_train() == current_train_exp
        assert berth.fringe_trains == {
            'F1': f1_exp,
            'F3': f3_exp}

        # MAIN  F1   F2  F3
        # -     NONE -   B   = B
        berth = FringeBerth(b_main, b_f1, b_f2, b_f3, b_f4)
        berth.set('F3', train_b)
        berth.set('F1', train_a)
        assert berth.set('F1', None) is None
        f3_exp = dict(
            train_b,
            is_fringe=True,
            berth=b_f3,
            distance_percent=0.75)
        assert berth.get_current_train() == f3_exp
        assert berth.fringe_trains == {
            'F1': None,
            'F3': f3_exp}

        # MAIN  F1   F2  F3
        # NONE  A    -   B   = B
        berth = FringeBerth(b_main, b_f1, b_f2, b_f3, b_f4)
        berth.set('F3', train_b)
        berth.set('F1', train_a)
        berth.set('MAIN', train_c)
        assert berth.set('MAIN', None) is True
        current_train_exp = dict(
            train_b,
            is_fringe=True,
            berth=b_f3,
            distance_percent=0.75)
        assert berth.get_current_train() == current_train_exp

    def test_tick(self):
        train_a = {
            'headcode': 'AAAA'
        }
        train_b = {
            'headcode': 'BBBB'
        }
        train_c = {
            'headcode': 'CCCC'
        }

        b_main = _berth_json(id='MAIN')
        b_f1 = _berth_json(id='F1', distance=1)
        b_f2 = _berth_json(id='F2', distance=2)
        b_f3 = _berth_json(id='F3', distance=3)
        b_f4 = _berth_json(id='F4', distance=4)

        # Train in the main berth -> do nothing on tick
        berth = FringeBerth(b_main, b_f1, b_f2, b_f3, b_f4)
        berth.set('MAIN', train_a)
        berth.set('F1', train_b)
        berth.tick()
        current_train_exp = dict(train_a, is_fringe=False)
        assert berth.get_current_train() == current_train_exp

        # No train in the main berth -> tick through fringe berths
        berth = FringeBerth(b_main, b_f1, b_f2, b_f3, b_f4)
        berth.set('F1', train_a)
        berth.set('F3', train_b)

        current_train_exp = dict(
            train_a,
            is_fringe=True,
            berth=b_f1,
            distance_percent=0.25)
        assert berth.get_current_train() == current_train_exp

        berth.tick()
        current_train_exp = dict(
            train_b,
            is_fringe=True,
            berth=b_f3,
            distance_percent=0.75)
        assert berth.get_current_train() == current_train_exp

        berth.tick()
        current_train_exp = dict(
            train_a,
            is_fringe=True,
            berth=b_f1,
            distance_percent=0.25)
        assert berth.get_current_train() == current_train_exp

        # Add a new train to F2 -> show it on next tick and show F3 train later
        berth.set('F2', train_c)
        assert berth.get_current_train() == current_train_exp

        berth.tick()
        current_train_exp = dict(
            train_c,
            is_fringe=True,
            berth=b_f2,
            distance_percent=0.5)
        assert berth.get_current_train() == current_train_exp

        berth.tick()
        current_train_exp = dict(
            train_b,
            is_fringe=True,
            berth=b_f3,
            distance_percent=0.75)
        assert berth.get_current_train() == current_train_exp

        berth.tick()
        current_train_exp = dict(
            train_a,
            is_fringe=True,
            berth=b_f1,
            distance_percent=0.25)
        assert berth.get_current_train() == current_train_exp

    def test_is_different(self):
        b_main = _berth_json(id='MAIN')
        b_f1 = _berth_json(id='F1', distance=1)
        b_f2 = _berth_json(id='F2', distance=2)

        berth = FringeBerth(b_main, b_f1, b_f2)

        moorgate1 = {
            'headcode': '2F29'
        }
        moorgate2 = {
            'headcode': '2F29'
        }

        kings_cross1 = {
            'headcode': '1P29',
            'is_fringe': False
        }
        kings_cross2 = {
            'headcode': '1P29',
            'is_fringe': True,
        }

        f1_train = {
            'headcode': '1P29',
            'is_fringe': True,
            'berth': b_f1,
        }
        f1_train2 = {
            'headcode': '1P29',
            'is_fringe': True,
            'berth': b_f1,
        }
        f2_train = {
            'headcode': '1P29',
            'is_fringe': True,
            'berth': b_f2,
        }

        assert berth._is_different(moorgate1, kings_cross1)
        assert berth._is_different(kings_cross1, moorgate1)
        assert berth._is_different(moorgate1, None)
        assert berth._is_different(None, moorgate1)
        assert not berth._is_different(moorgate1, moorgate2)
        assert berth._is_different(kings_cross2, kings_cross1)
        assert not berth._is_different(f1_train, f1_train2)
        assert berth._is_different(f1_train, f2_train)

    def test_set_and_tick(self):
        train_a = {
            'headcode': 'AAAA'
        }
        train_b = {
            'headcode': 'BBBB'
        }
        train_c = {
            'headcode': 'CCCC'
        }
        train_d = {
            'headcode': 'DDDD'
        }

        b_main = _berth_json(id='MAIN')
        b_f1 = _berth_json(id='F1', distance=1)
        b_f2 = _berth_json(id='F2', distance=2)
        b_f3 = _berth_json(id='F3', distance=3)
        b_f4 = _berth_json(id='F4', distance=4)

        berth = FringeBerth(b_main, b_f1, b_f2, b_f3, b_f4)
        berth.set('F2', train_a)
        berth.set('F3', train_b)
        berth.set('F4', train_c)
        assert berth.get_current_train()['headcode'] == 'AAAA'
        berth.tick()
        assert berth.get_current_train()['headcode'] == 'BBBB'
        berth.set('F1', train_d)
        berth.tick()
        assert berth.get_current_train()['headcode'] == 'CCCC'
        berth.set('F3', None)
        assert berth.get_current_train()['headcode'] == 'CCCC'
        berth.tick()
        assert berth.get_current_train()['headcode'] == 'DDDD'
        berth.set('F1', None)
        assert berth.get_current_train()['headcode'] == 'AAAA'
        berth.tick()
        assert berth.get_current_train()['headcode'] == 'CCCC'
        berth.set('F1', train_d)
        assert berth.get_current_train()['headcode'] == 'CCCC'
        berth.tick()
        assert berth.get_current_train()['headcode'] == 'DDDD'
        berth.tick()
        assert berth.get_current_train()['headcode'] == 'AAAA'
        berth.set('F1', None)
        berth.set('F2', None)
        berth.set('F3', None)
        berth.set('F4', None)
        berth.tick()
        assert berth.get_current_train() is None
        assert berth.current_fringe_berth_id is None
        berth.tick()
        berth.set('F3', train_a)
        assert berth.get_current_train()['headcode'] == 'AAAA'
        berth.tick()
        assert berth.get_current_train()['headcode'] == 'AAAA'
