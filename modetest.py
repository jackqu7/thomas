from thomas.config import get_displays, get_berths
from thomas.output import Output
from thomas.drawer import HeadcodeDrawer, FringeDrawer

displays = get_displays()
berths = get_berths()
output = Output(displays)

fringe_train = {
    'headcode': '1C23',
    'is_fringe': True,
    'distance_percent': 0.5,
    'berth': berths['D-WelwynNorth']
}

normal_train = {
    'headcode': '1C23',
    'is_fringe': False,
}


def draw(drawer, train):
    d = drawer(train)
    im = d.draw()
    output.display(im, displays[0])


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
