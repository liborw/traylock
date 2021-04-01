#!/usr/bin/env python

import os
os.environ["PYSTRAY_BACKEND"] = 'gtk'

import pystray
import subprocess
import json
from time import sleep
from PIL import Image, ImageDraw
from dataclasses import dataclass


@dataclass
class SystrayLockConfig:
    lock_cmd: str = 'lock'
    pad: int = 2
    size: int = 25
    active: bool = True
    line_width: int = 5
    color_bg: tuple = (0, 0, 0)
    color_fg: tuple = (50, 50, 50)
    color_90: tuple = (200, 200, 200)
    color_10: tuple = (200, 0, 0)
    max_idle_time_s: float = 600
    period_s: float = 10


def get_idle_time_s():
    return float(os.popen('xprintidle').read()) / 1000

class SystrayLock(object):

    def __init__(self, **kvargs):
        self.pad = kvargs.get('pad', 2)
        self.size = kvargs.get('size', 25)
        self.active = kvargs.get('active', True)
        self.line_width = kvargs.get('line_width', 5)
        self.color_bg = tuple(kvargs.get('color_bg', [0, 0, 0]))
        self.color_fg = tuple(kvargs.get('color_fg', [50, 50, 50]))
        self.color_90 = tuple(kvargs.get('color_90', [200, 200, 200]))
        self.color_10 = tuple(kvargs.get('color_10', [200, 0, 0]))
        self.max_idle_time_s = kvargs.get('max_idle_time_s', 600)
        self.lock_cmd = kvargs.get('lock_cmd', 'lock')
        self.period_s = 0.1

        self.icon = pystray.Icon('traylock', menu=self.make_menu())
        self.icon.icon = self.create_idle_icon(0)

    def make_menu(self):
        return pystray.Menu(
                pystray.MenuItem('active',
                                 self.on_clicked,
                                 checked=lambda item: self.active,
                                 default=True)
        )

    def on_clicked(self, icon, item):
        self.active = not self.active
        self.update()

    def update(self):
        if self.active:
            idle_time_s = get_idle_time_s()
            part = int(360 * min(idle_time_s/self.max_idle_time_s, 1))
            self.icon.icon = self.create_idle_icon(part)

            if (idle_time_s > self.max_idle_time_s):
                process = subprocess.run(self.lock_cmd)
        else:
            self.icon.icon = self.create_pause_icon()


    def create_idle_icon(self, part=0):
        size = self.size
        pad = self.pad
        line_width = self.line_width

        # Generate an image and draw a pattern
        image = Image.new('RGB', (size, size), self.color_bg)
        dc = ImageDraw.Draw(image)

        dc.arc([pad, pad, size-pad, size-pad], 0, 360, self.color_fg, line_width)

        xy = [pad, pad, size-pad, size-pad]
        if part < 360-90:
            dc.arc(xy, -90+part, 270, self.color_90, line_width)
        else:
            dc.arc(xy, -90+part, 270, self.color_10, line_width)

        return image

    def create_pause_icon(self):
        size = self.size
        pad = self.pad
        line_width = self.line_width

        # Generate an image and draw a pattern
        image = Image.new('RGB', (size, size), self.color_bg)
        dc = ImageDraw.Draw(image)

        dc.arc([pad, pad, size-pad, size-pad], 0, 360, self.color_fg, line_width)

        xy = [pad*2.1, pad*2, pad*2, size-pad*2]
        dc.line(xy, self.color_90, line_width)

        xy = [size-pad*2,pad*2, size-pad*2, size-pad*2]
        dc.line(xy, self.color_90, line_width)

        return image


    def thread(self, icon):
        icon.visible = True

        while True:
            sleep(self.period_s)
            self.update()


    def run(self):
        self.icon.run(setup=self.thread)


def read_conf():

    conf = dict()

    try:
        path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(path, 'traylock.json'), 'r') as f:
            conf.update(json.load(f))
    except FileNotFoundError:
        pass

    try:
        with open(os.path.join(os.path.expanduser('~/.config'), 'traylock.json'), 'r') as f:
            conf.update(json.load(f))
    except FileNotFoundError:
        pass

    return conf


if __name__ == '__main__':
    conf = read_conf()
    slock = SystrayLock(**conf)
    slock.run()
