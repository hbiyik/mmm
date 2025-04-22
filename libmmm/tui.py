'''
Created on Apr 18, 2025

@author: boogie
'''

import curses
import curses.textpad

from libmmm import devices
from libmmm import io

LEVEL_CATALOG = 0
LEVEL_DEVICE = 1
LEVEL_REGISTER = 2
LEVEL_POINT = 3


class Screen:
    UP = -1
    DOWN = 1

    def __init__(self, header=""):
        self.window = None
        self.headers = [header, ""]
        self.msg = ""

        self.width = 0
        self.height = 0
        curses.set_escdelay(25)
        self.init_curses()

        self.options = {}
        self.max_lines = curses.LINES - len(self.headers)
        self.prevs = {}
        self.top = 0
        self.bottom = 0
        self.current = 0
        self.page = 0
        self.path = ""
        self.device = None
        self.level = None
        self.prevs = []
        self.on_select()

    def getoptkey(self, offset=None):
        offset = offset if offset is not None else self.current
        return list(self.options)[offset]

    def getopt(self, offset=None):
        offset = offset if offset is not None else self.current
        return self.options[self.getoptkey(offset)]

    def back(self):
        self.init(*self.prevs.pop(), prev=False)

    def on_active(self):
        opt = self.getopt()
        txt = f"{opt[0]}"
        if self.level == LEVEL_POINT:
            register = opt[1]
            txts = []
            if register.unit is not None:
                txts.append(f"unit: {register.unit}")
            if register.default is not None:
                txts.append(f"default={register.default}")
            if register.validity:
                txts.append(f"validity={register.validity.help()}")
            txt += " ".join(txts)
        self.headers[1] += txt

    def on_select(self):
        options = {}
        if self.level is None:
            for catname, Devices in devices.catalogs.items():
                options[catname] = catname, Devices
            self.init(options, level=LEVEL_CATALOG, prev=False)
        elif self.level == LEVEL_CATALOG:
            _, Devices = self.getopt()
            for Device in Devices:
                device = Device()
                options[device.name] = device.name, device
            self.init(options, LEVEL_DEVICE)
        elif self.level == LEVEL_DEVICE:
            _, device = self.getopt()
            if not device.io:
                device.io = io.Memory
            for register in device:
                options[register.name] = register.name, register
            self.init(options, LEVEL_REGISTER)
        elif self.level == LEVEL_REGISTER:
            _, register = self.getopt()
            register.read()
            for point in register:
                options[point.name] = f"{point.name} = {point.value}", point
            self.init(options, LEVEL_POINT)

    def init(self, options, level=None, current=0, prev=True):
        if prev:
            self.prevs.append([self.options, self.level, self.current])
        paths = []
        for prev_opts, _prev_level, prev_current in self.prevs:
            paths.append(prev_opts[list(prev_opts)[prev_current]][0])
        self.path = ">".join(paths)
        self.level = level
        self.options = options
        self.top = 0
        self.bottom = len(self.options)
        self.current = current
        self.page = self.bottom // self.max_lines

    def init_curses(self):
        self.window = curses.initscr()
        self.window.keypad(True)

        curses.noecho()
        curses.cbreak()

        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_RED)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_WHITE)

        self.window.bkgd(' ', curses.color_pair(3) | curses.A_BOLD)

        self.current = curses.color_pair(2)

        self.height, self.width = self.window.getmaxyx()

    def run(self):
        try:
            self.input_stream()
        except KeyboardInterrupt:
            pass
        finally:
            curses.endwin()

    def input_stream(self):
        while True:
            self.display()

            ch = self.window.getch()
            if ch == curses.KEY_UP:
                self.scroll(self.UP)
            elif ch == curses.KEY_DOWN:
                self.scroll(self.DOWN)
            elif ch == curses.KEY_LEFT or ch == curses.KEY_PPAGE:
                self.paging(self.UP)
            elif ch == curses.KEY_RIGHT or ch == curses.KEY_NPAGE:
                self.paging(self.DOWN)
            elif ch == curses.ascii.LF or ch == curses.KEY_ENTER:
                self.on_select()
            elif ch == curses.KEY_BACKSPACE:
                if self.prevs:
                    self.back()
            elif ch == curses.ascii.ESC:
                if not self.prevs:
                    break
                self.back()

    def scroll(self, direction):
        next_line = self.current + direction
        if (direction == self.UP) and (self.top > 0 and self.current == 0):
            self.top += direction
            return
        if (direction == self.UP) and (self.top > 0 or self.current > 0):
            self.current = next_line
            return
        if (direction == self.DOWN) and (next_line < self.max_lines) and (self.top + next_line < self.bottom):
            self.current = next_line
            return
        if (direction == self.DOWN) and (next_line == self.max_lines) and (self.top + self.max_lines < self.bottom):
            self.top += direction
            return

    def paging(self, direction):
        current_page = (self.top + self.current) // self.max_lines
        next_page = current_page + direction
        if next_page == self.page:
            self.current = min(self.current, self.bottom % self.max_lines - 1)

        if (direction == self.UP) and (current_page > 0):
            self.top = max(0, self.top - self.max_lines)
            return

        if (direction == self.DOWN) and (current_page < self.page):
            self.top += self.max_lines
            return

    def display(self):
        self.height, self.width = self.window.getmaxyx()
        self.window.erase()
        row = 0
        for _key, (optname, _opt) in self.options.items():
            if row < self.top or row >= self.top + self.max_lines:
                continue
            self.headers[1] = f"{self.path} "
            self.on_active()
            val = optname
            if row == self.current:
                self.window.addstr(row + len(self.headers), 0, val, curses.color_pair(2))
            else:
                self.window.addstr(row + len(self.headers), 0, val, curses.color_pair(1))
            row += 1
        for row, header in enumerate(self.headers):
            self.window.addstr(row, 0, header + " " * (self.width - len(header)), curses.color_pair(4))
        self.window.refresh()
