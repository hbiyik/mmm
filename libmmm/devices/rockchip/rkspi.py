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
from libmmm.devices.rk3588.spi import SPI2
from libmmm.devices.rk3588.cru import CRU
from libmmm import common

import time


SPI_CMD_WRITE = 1
SPI_CMD_READ = 0

cru = CRU()
clkgate = cru.getblock("CLKGATE_14")


class MotorolaSlave:
    spidev = None
    clocks = []

    frame_len = "8bit"
    motorola_master_ssd = 1
    endian = "big"
    ght = 1
    clk_div = 198
    cs = 2
    timeout = 1

    def __init__(self, spidev=None, *clocks):
        self.clocks = clocks or self.clocks
        self.spidev = spidev or self.spidev
        self.ctrl_reg = self.spidev.getblock("CTRL0")
        self.ctrl1_reg = self.spidev.getblock("CTRL1")
        self.en_reg = self.spidev.getblock("ENABLE")
        self.bd_reg = self.spidev.getblock("BAUDRATE")
        self.txdr_reg = self.spidev.getblock("TXDR")
        self.rxdr_reg = self.spidev.getblock("RXDR")
        self.sen_reg = self.spidev.getblock("SLAVE_ENABLE")
        self.sta_reg = self.spidev.getblock("STATUS")
        self.intc_reg = self.spidev.getblock("INT_CLEAR")
        self.intm_reg = self.spidev.getblock("INT_CLEAR")
        self.rxflr_reg = self.spidev.getblock("RXFLR")
        self.config = ((self.ctrl_reg, "frame_len", self.frame_len),
                       (self.ctrl_reg, "motorola_master_ssd", self.motorola_master_ssd),
                       (self.ctrl_reg, "ght", self.ght),
                       (self.bd_reg, "clk_div", self.clk_div),
                       (self.sen_reg, "slave_enable", self.cs),
                       )

    def setmode(self, mode):
        self.en_reg.write("enable", 0)
        self.ctrl_reg.write("mode", mode)
        self.en_reg.write("enable", 1)

    def waitreg(self, reg, dpname, dpval):
        startt = time.time()
        while True:
            reg.read()
            if reg.get(dpname).int == dpval:
                break
            if (time.time() - startt) > self.timeout:
                raise RuntimeError(f"{self.spidev.name} is busy")

    def __enter__(self):
        self.en_reg.read()
        if self.en_reg.get("enable").int == 1:
            self.waitreg(self.en_reg, "enable", 0)

        for clock in self.clocks:
            clock.reg.write(clock.name, common.ON)
        for reg, dpname, dpval in self.config:
            reg.read()
            reg.write(dpname, dpval)
        self.en_reg.write("enable", 1)
        return self

    def read(self):
        buf = []
        self.sta_reg.read()
        self.rxflr_reg.read()
        if self.sta_reg.get("rx_empty").int == 1:
            self.waitreg(self.sta_reg, "rx_empty", 0)
        while self.rxflr_reg.get("rx_num_entries").int:
            if self.sta_reg.get("rx_empty").int == 1:
                self.waitreg(self.sta_reg, "rx_empty", 0)
            self.rxdr_reg.read()
            buf.append(self.rxdr_reg.get("rxdr").int)
            self.sta_reg.read()
            self.rxflr_reg.read()
        return buf

    def write(self, buf):
        self.sta_reg.read()
        if self.sta_reg.get("slave_tx_busy").int == 1:
            self.waitreg(self.sta_reg, "slave_tx_busy", 0)
        self.txdr_reg.write("txdr", buf, zero=True)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.en_reg.write("enable", 0)


class Rk806:
    spidev = SPI2()
    clocks = [clkgate.get("clk_spi2"), clkgate.get("pclk_spi2")]

    def __init__(self, spidev=None, *clocks):
        clocks = clocks or self.clocks
        spidev = spidev or self.spidev
        self.slave = MotorolaSlave(spidev, *clocks)

    def spi_cmds_write_reg(self, addr, data):
        if data > 255:
            raise ValueError(f"Registers are only 8bit but received data is {data}")
        yield (1 | SPI_CMD_WRITE << 7 | addr << 8) & 0xff
        yield (addr | data << 8) & 0xff

    def spi_cmds_read_reg(self, addr, count=1):
        yield (count - 1) | SPI_CMD_READ << 7
        yield addr
        yield 0

    def read(self, addr):
        with self.slave as slave:
            for cmd in self.spi_cmds_read_reg(addr):
                print(cmd)
                slave.write(cmd)
            return slave.read()


REMOTE_DBG = "192.168.2.10"
REMOTE_DBG = None

if REMOTE_DBG:
    import pydevd  # @UnresolvedImport
    pydevd.settrace(REMOTE_DBG, stdoutToServer=True, stderrToServer=True, suspend=False)

test = Rk806()

while True:
    print(test.read(0x5a))
    print(test.read(0x5b))
    print(test.read(0x5c))
    break
