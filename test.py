import unittest
from thomas.berth import Berth, PriorityBerth, FringeBerth


class BerthTests(unittest.TestCase):

    def test_is_different(self):
        berth = Berth('abc')

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
        berth = Berth('abc')

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
        berth = PriorityBerth('abc', alt='efg')

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

        # MAIN  F1  F2  F3
        # NEW   -   -   -   = NEW
        berth = FringeBerth('MAIN', 'F1', 'F2', 'F3')
        assert berth.set('MAIN', train_a) is True
        assert berth.get_current_train() == dict(train_a, is_fringe=False)

        # MAIN  F1  F2  F3
        # -     -   -   NEW = NEW
        berth = FringeBerth('MAIN', 'F1', 'F2', 'F3')
        assert berth.set('F3', train_a) is True
        assert berth.get_current_train() == dict(train_a, is_fringe=True)
        assert berth.fringe_trains == {'F3': dict(train_a, is_fringe=True)}

        # MAIN  F1  F2  F3
        # A     -   NEW -   = A
        berth = FringeBerth('MAIN', 'F1', 'F2', 'F3')
        berth.set('MAIN', train_a)
        assert berth.set('F2', train_b) is None
        assert berth.get_current_train() == dict(train_a, is_fringe=False)
        assert berth.fringe_trains == {'F2': dict(train_b, is_fringe=True)}

        # MAIN  F1  F2  F3
        # NEW   -   A   -   = NEW
        berth = FringeBerth('MAIN', 'F1', 'F2', 'F3')
        berth.set('F2', train_a)
        assert berth.set('MAIN', train_b) is True
        assert berth.get_current_train() == dict(train_b, is_fringe=False)

        # MAIN  F1  F2  F3
        # -     NEW -   A   = NEW
        berth = FringeBerth('MAIN', 'F1', 'F2', 'F3')
        berth.set('F3', train_a)
        assert berth.set('F1', train_b) is True
        assert berth.get_current_train() == dict(train_b, is_fringe=True)
        assert berth.fringe_trains == {
            'F1': dict(train_b, is_fringe=True),
            'F3': dict(train_a, is_fringe=True)}

        # MAIN  F1  F2  F3
        # B     NEW  -   A   = B
        berth = FringeBerth('MAIN', 'F1', 'F2', 'F3')
        berth.set('F3', train_a)
        berth.set('MAIN', train_b)
        assert berth.set('F1', train_c) is None
        assert berth.get_current_train() == dict(train_b, is_fringe=False)
        assert berth.fringe_trains == {
            'F1': dict(train_c, is_fringe=True),
            'F3': dict(train_a, is_fringe=True)}

        # MAIN  F1   F2  F3
        # -     NONE -   B   = B
        berth = FringeBerth('MAIN', 'F1', 'F2', 'F3')
        berth.set('F3', train_b)
        berth.set('F1', train_a)
        assert berth.set('F1', None) is True
        assert berth.get_current_train() == dict(train_b, is_fringe=True)
        assert berth.fringe_trains == {
            'F1': None,
            'F3': dict(train_b, is_fringe=True)}

        # MAIN  F1   F2  F3
        # NONE  A    -   B   = A
        berth = FringeBerth('MAIN', 'F1', 'F2', 'F3')
        berth.set('F3', train_b)
        berth.set('F1', train_a)
        berth.set('MAIN', train_c)
        assert berth.set('MAIN', None) is True
        assert berth.get_current_train() == dict(train_a, is_fringe=True)

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

        # Train in the main berth -> do nothing on tick
        berth = FringeBerth('MAIN', 'F1', 'F2', 'F3')
        berth.set('MAIN', train_a)
        berth.set('F1', train_b)
        berth.tick()
        assert berth.get_current_train() == dict(train_a, is_fringe=False)
        assert berth.counter == 1

        # No train in the main berth -> tick through fringe berths
        berth = FringeBerth('MAIN', 'F1', 'F2', 'F3')
        berth.set('F1', train_a)
        berth.set('F3', train_b)

        berth.tick()
        assert berth.get_current_train() == dict(train_a, is_fringe=True)
        assert berth.counter == 1

        berth.tick()
        assert berth.get_current_train() == dict(train_b, is_fringe=True)
        assert berth.counter == 2

        berth.tick()
        assert berth.get_current_train() == dict(train_a, is_fringe=True)
        assert berth.counter == 1

        # Add a new train to F2 -> show it on next tick and show F3 train later
        berth.set('F2', train_c)

        berth.tick()
        assert berth.get_current_train() == dict(train_c, is_fringe=True)
        assert berth.counter == 2

        berth.tick()
        assert berth.get_current_train() == dict(train_b, is_fringe=True)
        assert berth.counter == 3

        berth.tick()
        assert berth.get_current_train() == dict(train_a, is_fringe=True)
        assert berth.counter == 1

    def test_is_different(self):
        berth = FringeBerth('abc')

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

        assert berth._is_different(moorgate1, kings_cross1)
        assert berth._is_different(kings_cross1, moorgate1)
        assert berth._is_different(moorgate1, None)
        assert berth._is_different(None, moorgate1)
        assert not berth._is_different(moorgate1, moorgate2)
        assert berth._is_different(kings_cross2, kings_cross1)
