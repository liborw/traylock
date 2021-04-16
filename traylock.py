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
    lock_cmd: str = "lock"

    def __post_init__(self):
        for k, fun in self.__annotations__.items():
            self.__setattr__(k, fun(self.__getattribute__(k)))


def get_idle_time_s():
    return float(os.popen('xprintidle').read()) / 1000


class SystrayLock(object):

    def __init__(self):
        self.active = conf.active
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
            part = int(360 * min(idle_time_s/conf.max_idle_time_s, 1))
            self.icon.icon = self.create_idle_icon(part)

            if (idle_time_s > conf.max_idle_time_s):
                process = subprocess.run(conf.lock_cmd)
        else:
            self.icon.icon = self.create_pause_icon()

    def create_idle_icon(self, part=0):
        size = conf.size
        pad = conf.pad
        line_width = conf.line_width

        # Generate an image and draw a pattern
        image = Image.new('RGB', (size, size), conf.color_bg)
        dc = ImageDraw.Draw(image)

        dc.arc([pad, pad, size-pad, size-pad], 0, 360, conf.color_fg, line_width)

        xy = [pad, pad, size-pad, size-pad]
        if part < 360-90:
            dc.arc(xy, -90+part, 270, conf.color_90, line_width)
        else:
            dc.arc(xy, -90+part, 270, conf.color_10, line_width)

        return image

    def create_pause_icon(self):
        size = conf.size
        pad = conf.pad
        line_width = conf.line_width

        # Generate an image and draw a pattern
        image = Image.new('RGB', (size, size), conf.color_bg)
        dc = ImageDraw.Draw(image)

        dc.arc([pad, pad, size-pad, size-pad], 0, 360, conf.color_fg, line_width)

        xy = [pad*2, pad*2, pad*2, size-pad*2]
        dc.line(xy, conf.color_90, line_width)

        xy = [size-pad*2,pad*2, size-pad*2, size-pad*2]
        dc.line(xy, conf.color_90, line_width)

        return image


    def thread(self, icon):
        icon.visible = True

        while True:
            sleep(conf.period_s)
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
    conf = SystrayLockConfig(**read_conf())
    slock = SystrayLock()
    slock.run()
