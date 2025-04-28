'''
Created on Apr 18, 2025

@author: boogie
'''

import time
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
        self.headers = [header, []]
        self.msg = ""

        self.width = 0
        self.height = 0
        self.delay = 1
        self.keydelay = 0.025
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

    def updateheader(self):
        optkey = self.getoptkey()
        headers = [optkey]
        if self.level == LEVEL_POINT:
            register = self.getopt()
            pointname = optkey.split(".")[1]
            datapoint = register.get(pointname)
            if datapoint.unit is not None:
                headers.append(f"unit: {datapoint.unit}")
            if datapoint.default is not None:
                headers.append(f"default={datapoint.default}")
            if datapoint.validity:
                headers.append(f"validity={datapoint.validity.help()}")
        self.headers[1] += headers

    def on_display(self, optname, opt):
        val = optname
        if self.level == LEVEL_POINT:
            register = opt
            register.read()
            datapoint = register.get(optname.split(".")[1])
            val = f"{optname} = {datapoint.value}"
            if datapoint.unit:
                val += f" {datapoint.unit}"
        if optname == self.getoptkey():
            self.updateheader()
        return val

    def on_edit(self):
        optname = self.getoptkey()
        register = self.getopt()
        datapoint = register.get(optname.split(".")[1])
        curses.echo()
        row = self.current - self.top + len(self.headers)
        col = len(optname) + 3
        self.window.nodelay(False)
        # reset previous strings
        self.window.addstr(row, col, " " * (self.width - col), curses.color_pair(2))
        # get input
        value = self.window.getstr(row, col)
        self.window.nodelay(True)
        curses.noecho()
        try:
            value = value.decode()
            register.write(datapoint.name, value)
        except Exception as e:
            self.msg = f"ERROR: {e}"
            return
        self.msg = f"SUCCESS: {optname} is set to {value}"

    def on_select(self):
        options = {}
        if self.level is None:
            for catname, Devices in devices.catalogs.items():
                options[catname] = Devices
            self.init(options, level=LEVEL_CATALOG, prev=False)
        elif self.level == LEVEL_CATALOG:
            Devices = self.getopt()
            for Device in Devices:
                device = Device()
                options[device.name] = device
            self.init(options, LEVEL_DEVICE)
        elif self.level == LEVEL_DEVICE:
            device = self.getopt()
            if not device.io:
                device.io = io.Memory
            self.init(dict(device.itergroups()), LEVEL_REGISTER)
        elif self.level == LEVEL_REGISTER:
            for register in self.getopt():
                register.read()
                for point in register:
                    if "reserved" in point.name.lower():
                        continue
                    options[f"{register.name}.{point.name}"] = register
            self.init(options, LEVEL_POINT)
        elif self.level == LEVEL_POINT:
            self.on_edit()

    def init(self, options, level=None, current=0, prev=True):
        if prev:
            self.prevs.append([self.options, self.level, self.current])
        paths = []
        for prev_opts, _prev_level, prev_current in self.prevs:
            paths.append(list(prev_opts)[prev_current])
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
        curses.set_escdelay(int(self.keydelay * 1000))
        self.window.nodelay(True)

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
            if ch == -1:
                time.sleep(self.keydelay)
            if ch == curses.KEY_UP:
                self.scroll(self.UP)
                self.msg = None
            elif ch == curses.KEY_DOWN:
                self.scroll(self.DOWN)
                self.msg = None
            elif ch == curses.KEY_LEFT or ch == curses.KEY_PPAGE:
                self.paging(self.UP)
                self.msg = None
            elif ch == curses.KEY_RIGHT or ch == curses.KEY_NPAGE:
                self.paging(self.DOWN)
                self.msg = None
            elif ch == curses.ascii.LF or ch == curses.KEY_ENTER:
                self.on_select()
            elif ch == curses.KEY_BACKSPACE:
                self.msg = None
                if self.prevs:
                    self.back()
            elif ch == curses.ascii.ESC:
                self.msg = None
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
        self.headers[1] = [f"{self.path} "] if self.path else []
        for index, (optname, opt) in enumerate(self.options.items()):
            if index < self.top or index >= self.top + self.max_lines:
                continue
            row = index - self.top
            val = self.on_display(optname, opt)
            if row == self.current:
                self.window.addstr(row + len(self.headers), 0, val, curses.color_pair(2))
            else:
                self.window.addstr(row + len(self.headers), 0, val, curses.color_pair(1))
            row += 1
        if self.msg:
            self.headers[1].append(self.msg)
        self.headers[1] = " ".join(self.headers[1])
        for row, header in enumerate(self.headers):
            self.window.addstr(row, 0, header + " " * (self.width - len(header)), curses.color_pair(4))
        self.window.refresh()
