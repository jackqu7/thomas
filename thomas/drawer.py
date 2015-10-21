from PIL import Image, ImageDraw, ImageFont

from .util import get_asset_filename


class Drawer(object):

    WIDTH = 160
    HEIGHT = 128

    large_font = ImageFont.truetype(get_asset_filename('font.ttf'), 54)
    small_font = ImageFont.truetype(get_asset_filename('font.ttf'), 20)

    BLUE = (0, 204, 255)
    ORANGE = (255, 153, 51)

    def __init__(self, train, text_color=BLUE):
        self.im = Image.new('RGB', (self.WIDTH, self.HEIGHT))
        self.train = train
        self.text_color = text_color

    def draw(self):
        return self.blank()

    def blank(self):
        return self.im

    def draw_text(self, draw, coords, text, font, color, center=True):
        x, y = coords

        if center:
            w, h = font.getsize(text)

            x = x - w / 2

            y = y - h / 2

        draw.text((x, y), text, font=font, fill=color)


class HeadcodeDrawer(Drawer):
    def draw(self):
        if self.train:
            if self.train.get('is_fringe'):
                color = self.ORANGE
            else:
                color = self.BLUE
            return self.headcode(self.train['headcode'], color=color)
        else:
            return self.blank()

    def headcode(self, headcode, color=Drawer.BLUE):
        draw = ImageDraw.Draw(self.im)

        self.draw_text(
            draw,
            (self.WIDTH / 2 + 4, self.HEIGHT / 2),
            headcode,
            self.large_font,
            color)

        return self.im
