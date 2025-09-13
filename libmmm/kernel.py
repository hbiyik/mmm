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
import os
import fcntl
import ctypes
from libmmm.helper import logger

NRBITS = 8
TYPEBITS = 8
SIZEBITS = 14
DIRBITS = 2

NRSHIFT = 0
TYPESHIFT = NRSHIFT + NRBITS
SIZESHIFT = TYPESHIFT + TYPEBITS
DIRSHIFT = SIZESHIFT + SIZEBITS

NONE = 0
WRITE = 1
READ = 2
MAGIC = ord("m")


def IOC(direction, magic, number, struct):
    size = ctypes.sizeof(struct)
    return (
        ctypes.c_int32(direction << DIRSHIFT).value |
        ctypes.c_int32(magic << TYPESHIFT).value |
        ctypes.c_int32(number << NRSHIFT).value |
        ctypes.c_int32(size << SIZESHIFT).value
    )


def IOWR(magic, number, struct):
    return IOC(READ | WRITE, magic, number, struct)


class StructRegInfo(ctypes.Structure):
    _fields_ = [
        ('name', ctypes.c_char * 32),
        ('value', ctypes.c_int),
    ]


class StructRegSet(ctypes.Structure):
    _fields_ = [
        ('info', StructRegInfo),
        ('min', ctypes.c_int),
        ('max', ctypes.c_int),
    ]


CMD_GET_REGULATOR = IOWR(MAGIC, 0, StructRegInfo)
CMD_SET_REGULATOR = IOWR(MAGIC, 1, StructRegSet)


class KernelException(Exception):
    pass


class Kernel:
    path = "/dev/mmm"

    def __init__(self):
        self.fd = None
        if not os.path.exists(self.path):
            raise KernelException(f"{self.path} is not available, did you load the mmm kernel module?")

    def open(self):
        self.fd = os.open(self.path, os.O_RDWR | os.O_CLOEXEC)
        logger.debug(f"Opened MMM device {self.path}")

    def close(self):
        if self.fd is not None:
            os.close(self.fd)
        self.fd = None

    def getvoltage(self, regname):
        reginfo = StructRegInfo()
        reginfo.name = regname.encode()
        fcntl.ioctl(self.fd, CMD_GET_REGULATOR, reginfo)
        return reginfo.value

    def setvoltage(self, regname, minuv, maxuv):
        reginfo = StructRegSet()
        reginfo.info.name = regname.encode()
        reginfo.min = minuv
        reginfo.max = maxuv
        fcntl.ioctl(self.fd, CMD_SET_REGULATOR, reginfo)
        return reginfo.info.value
