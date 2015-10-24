from thomas.config import BERTHS as B
from thomas.output import Output
from thomas.drawer import HeadcodeDrawer, FringeDrawer


output = Output([1])

fringe_train = {
    'headcode': '1C23',
    'is_fringe': True,
    'distance_percent': 0.5,
    'berth': B['0666']
}

normal_train = {
    'headcode': '1C23',
    'is_fringe': False,
}


def draw(drawer, train):
    d = drawer(train)
    im = d.draw()
    output.display(im, 1)


print('Fringe train on FringeDrawer')
draw(FringeDrawer, fringe_train)
input('show next')

print('Normal train on FringeDrawer')
draw(FringeDrawer, normal_train)
input('show next')

print('Fringe train on HeadcodeDrawer')
draw(HeadcodeDrawer, fringe_train)
input('show next')

print('Normal train on HeadcodeDrawer')
draw(HeadcodeDrawer, normal_train)
input('show next')
