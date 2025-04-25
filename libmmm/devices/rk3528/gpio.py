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

from libmmm.model import Device
from libmmm.devices.rockchip.gpio import GPIO


class GPIO0(GPIO, Device):
    devname = "GPIO0"
    start = 0xFF610000


class GPIO1(GPIO, Device):
    devname = "GPIO1"
    start = 0xFFAF0000


class GPIO2(GPIO, Device):
    devname = "GPIO2"
    start = 0xFFB00000


class GPIO3(GPIO, Device):
    devname = "GPIO3"
    start = 0xFEB10000


class GPIO4(GPIO, Device):
    devname = "GPIO4"
    start = 0xFFB20000
