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

    def draw_text(self, draw, coords, text, font, color, center_x=True, center_y=True):
        x, y = coords

        w, h = font.getsize(text)

        if center_x:
            x = x - w / 2

        if center_y:
            y = y - h / 2

        draw.text((x, y), text, font=font, fill=color)
        return w, h

    def draw_text_wrap(self, draw, coords, text, font, color, center_x=True):
        WIDTH = 160
        LEADING = 25

        x, y = coords

        text_size_x, _ = draw.textsize(text, font=font)
        remaining = WIDTH
        space_width, space_height = draw.textsize(' ', font=font)
        # use this list as a stack, push/popping each line
        output_text = []
        # split on whitespace...
        for word in text.split(None):
            word_width, word_height = draw.textsize(word, font=font)
            if word_width + space_width > remaining:
                output_text.append(word)
                remaining = WIDTH - word_width
            else:
                if not output_text:
                    output_text.append(word)
                else:
                    output = output_text.pop()
                    output += ' %s' % word
                    output_text.append(output)
                remaining = remaining - (word_width + space_width)

        for text in output_text:

            w, h = font.getsize(text)

            if center_x:
                new_x = x - w / 2
            else:
                new_x = x

            # print(text, h, y)

            draw.text((new_x, y), text, font=font, fill=color)
            y += LEADING


class HeadcodeDrawer(Drawer):
    RIGHT = 'right'
    LEFT = 'left'

    def __init__(self, *args, **kwargs):
        self.progress_orientation = \
            kwargs.pop('progress_orientation', None) or self.RIGHT
        super(HeadcodeDrawer, self).__init__(*args, **kwargs)

    def draw(self):
        if self.train:
            if self.train.get('is_fringe'):
                return self.fringe(self.train)
            else:
                return self.headcode(self.train['headcode'])
        else:
            return self.blank()

    def fringe(self, train, color=Drawer.ORANGE):
        draw = ImageDraw.Draw(self.im)

        PROGRESS_HEIGHT = 5
        TOP_SEP = 20
        LINE_SEP = 15

        progress_width = train['distance_percent'] * self.WIDTH
        if self.progress_orientation == self.RIGHT:
            progress_end_x = progress_width
            progress_coords = (
                (0, 0),
                (progress_end_x, PROGRESS_HEIGHT))
        else:
            progress_start_x = self.WIDTH - progress_width
            progress_coords = (
                (progress_start_x, 0),
                (self.WIDTH, PROGRESS_HEIGHT))

        draw.rectangle(progress_coords, fill=color)

        _, h = self.draw_text(
            draw,
            (self.WIDTH / 2 + 4, PROGRESS_HEIGHT + TOP_SEP),
            self.train['headcode'],
            self.large_font,
            color,
            center_y=False)

        self.draw_text_wrap(
            draw,
            (self.WIDTH / 2 + 4, h + PROGRESS_HEIGHT + TOP_SEP + LINE_SEP),
            self.train['berth']['desc'],
            self.small_font,
            color)

        return self.im

    def headcode(self, headcode, color=Drawer.BLUE):
        draw = ImageDraw.Draw(self.im)

        self.draw_text(
            draw,
            (self.WIDTH / 2 + 4, self.HEIGHT / 2),
            headcode,
            self.large_font,
            color)

        return self.im
