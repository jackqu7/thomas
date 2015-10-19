import unittest
from thomas.berth import Berth, PriorityBerth


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
