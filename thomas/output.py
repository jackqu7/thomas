from PIL import Image

import math
import os

has_tk = True
try:
    from tkinter import Tk, Label
    from PIL import ImageTk
except ImportError:
    has_tk = False

has_tft = True
try:
    import Adafruit_ILI9341 as TFT
    from Adafruit_GPIO import SPI, GPIO, PWM
except ImportError:
    has_tft = False


class Display(object):
    def __init__(self, id, port, device, controller, ss=None,
                 drawer_kwargs=None):
        self.id = id

        self.port = port
        self.device = device
        self.ss = ss

        self.drawer_kwargs = drawer_kwargs or {}

        self.controller = controller


width = 160
height = 128

if has_tk:

    class UI(Label):

        def __init__(self, master):
            im = Image.new('RGB', (width, height))
            self.image = ImageTk.PhotoImage(im)
            Label.__init__(self, master, image=self.image, bd=2)

        def display(self, im):
            self.image.paste(im)

    class OutputTk(object):
        def __init__(self, displays):
            self.root = Tk()
            self.root.wm_attributes('-topmost', 1)

            self.uis = {}

            count = len(displays)
            if count < 4:
                grid = count
            else:
                grid = 3

            for i, display in enumerate(displays):
                ui = UI(self.root)
                col = int(i % grid)
                row = int(math.floor(i / grid))
                ui.grid(row=row, column=col)
                self.uis[display.id] = ui

        def display(self, img, display):
            self.uis[display.id].display(img)
            self.root.update()

        def brightness_up(self):
            pass

        def brightness_down(self):
            pass


if has_tft:
    class OutputTFT(object):
        PWM_FREQ = 120
        PWM_PIN = 21

        DC = 27
        RST = 18
        SPI_PORT = 0
        SPI_DEVICE = 0

        A0 = 22
        A1 = 23
        A2 = 24
        A3 = 25

        def _get_spi(self, port, device):
            key = '%s-%s' % (port, device)
            if key not in self._spis:
                self._spis[key] = SPI.SpiDev(port, device)
            return self._spis[key]

        def __init__(self, displays):

            self.init_pwm()

            self._spis = {}

            self.gpio = GPIO.get_platform_gpio()
            self.gpio.setup(self.A0, GPIO.OUT)
            self.gpio.setup(self.A1, GPIO.OUT)
            self.gpio.setup(self.A2, GPIO.OUT)
            self.gpio.setup(self.A3, GPIO.OUT)

            self.tfts = {}

            has_reset = False

            for display in displays:
                print('init', display.id)

                # only reset once
                if not has_reset:
                    rst = self.RST
                    has_reset = True
                else:
                    rst = None

                self.address(display)

                spi = self._get_spi(display.port, display.device)
                disp = TFT.ST7735(self.DC, rst=rst, spi=spi, clock=16000000)
                disp.begin()

                # Set to black and then display it
                disp.clear()
                disp.display()

                self.tfts[display.id] = disp

        def address(self, display):
            if display.ss:
                a0 = display.ss & 0b0001 != 0
                a1 = display.ss & 0b0010 != 0
                a2 = display.ss & 0b0100 != 0
                a3 = display.ss & 0b1000 != 0

                self.gpio.output(self.A0, a0)
                self.gpio.output(self.A1, a1)
                self.gpio.output(self.A2, a2)
                self.gpio.output(self.A3, a3)

        def display(self, img, display):
            self.address(display)
            self.tfts[display.id].display(img.rotate(90))

        def init_pwm(self):
            self.pwm = PWM.get_platform_pwm()

            self.brightness = 100

            self.pwm.start(self.PWM_PIN, self.brightness, self.PWM_FREQ)

        def brightness_up(self):
            self._change_brightness(+5)

        def brightness_down(self):
            self._change_brightness(-5)

        def _change_brightness(self, change):
            self.brightness += change
            if self.brightness < 0:
                self.brightness = 0
            elif self.brightness > 100:
                self.brightness = 100
            self.pwm.set_duty_cycle(self.PWM_PIN, self.brightness)


class Output(object):
    def __init__(self, displays):
        is_arm = os.uname()[4][:3] == 'arm'

        self.type = 'tft' if is_arm else 'tk'
        output = OutputTFT if is_arm else OutputTk
        self.output = output(displays)
        self.display_queue = []

    def queue_display_update(self, img, display):
        self.display_queue.append((img, display))

    def flush_display_queue(self):
        for args in self.display_queue:
            self.display(*args)
        self.display_queue = []

    def __getattr__(self, name):
        return getattr(self.output, name)
