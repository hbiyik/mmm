"""
 Copyright (C) 2025 boogie

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

PLLCLOCKNAME = "clock"
PVTCLOCKNAME = "pvtclock"
MHZ = "Mhz"

ON = "ON"
OFF = "OFF"
ENABLED = "ENABLED"
DISABLED = "DISABLED"
COMPLETE = "COMPLETE"
NOTCOMPLETE = "NOTCOMPLETE"
READY = "READY"
BUSY = "BUSY"
IDLE = "IDLE"


def iterlistchunks(arr, size):
    count = int(len(arr) / size)
    left = len(arr) % size
    for i in range(count):
        yield arr[i * size: (i + 1) * size]
    if left:
        yield arr[(i + 1) * size:]


class Singleton(type):
    instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.instances:
            cls.instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls.instances[cls]
