from PIL import Image, ImageDraw, ImageFont

from .util import get_asset_filename


class Drawer(object):

    WIDTH = 160
    HEIGHT = 128

    large_font = ImageFont.truetype(get_asset_filename('font.ttf'), 54)
    small_font = ImageFont.truetype(get_asset_filename('font.ttf'), 20)

    text_color = (0, 204, 255)

    def __init__(self):
        self.im = Image.new('RGB', (self.WIDTH, self.HEIGHT))

    def blank(self):
        return self.im

    def headcode(self, headcode):
        draw = ImageDraw.Draw(self.im)

        self.draw_text(
            draw,
            (self.WIDTH / 2 + 4, self.HEIGHT / 2),
            headcode,
            self.large_font)

        return self.im

    def draw_text(self, draw, coords, text, font, center=True):
        x, y = coords

        if center:
            w, h = font.getsize(text)

            x = x - w / 2

            y = y - h / 2

        draw.text((x, y), text, font=font, fill=self.text_color)
