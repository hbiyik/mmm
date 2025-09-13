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

from libmmm.io import Io
from libmmm.model import Device, Block, Datapoint
from libmmm import kernel


REG_PATH = "/sys/class/regulator"
REGULATORS = {}

for fname in os.listdir(REG_PATH):
    regnum = fname.split(".")[-1]
    if not regnum.isdigit():
        # weird regulator, should never happen
        continue
    index = int(regnum)
    with open(os.path.join(REG_PATH, fname, "uevent")) as f:
        uevent = f.read().strip()
        if uevent == "":
            # dummy regulator
            continue
        if "regulator-fixed" in uevent:
            # fixed regulator
            continue
    with open(os.path.join(REG_PATH, fname, "type")) as f:
        regtype = f.read().strip()
    with open(os.path.join(REG_PATH, fname, "name")) as f:
        regname = f.read().strip()
    REGULATORS[index] = regname, regtype


class RegulatorIo(Io):
    def __init__(self, start, size):
        self.start = start
        self.size = size
        self.kernel = kernel.Kernel()
        self.kernel.open()
        self.names = {}
        self.init()

    def close(self):
        self.kernel.close()

    def readio(self, start, size):
        try:
            return self.kernel.getvoltage(REGULATORS[start][0])
        except OSError:
            return 0

    def writeio(self, start, data):
        return self.kernel.setvoltage(REGULATORS[start][0], int(data), int(data))


class RegulatorBlock(Block):
    allowwrite = True
    allowread = True

    def __init__(self, name, start):
        Block.__init__(self, name, start, 1)
        self.dp = Datapoint("voltage", unit="uV")

    def get(self, name):
        return self.dp

    def read(self):
        self.dp.value = self.device.io.read(self.start, 1)

    def write(self, name, value):
        self.dp.value = self.device.io.write(self.start, value)

    def __iter__(self):
        yield self.dp


class Regulators(Device):
    name = "regulators"

    def __init__(self):
        super(Regulators, self).__init__(self.name, 0, RegulatorIo)
        for regindex, (regname, regtype) in REGULATORS.items():
            if not regtype == "voltage":
                # handle current regulators later
                continue
            self.block(RegulatorBlock(regname, regindex))
            self.addgroup(regtype, regname)
