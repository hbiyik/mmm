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
from libmmm.model import Device, Reg32, Datapoint, Validator
from libmmm.devices.rockchip import RK_Reg32_16bitMasked


class GPIO(Device):
    devname = ""
    start = 0

    def interleave16bits(self, addr, *REGS):
        for REG, VALIDATOR in REGS:
                for col in ["A", "B", "C", "D"]:
                    if col in ["A", "C"]:
                        suffix = "_L" if col == "A" else "_H"
                        reg = RK_Reg32_16bitMasked(REG + suffix, addr)
                        self.block(reg)
                        addr += 4
                        gpio = 0
                    for row in range(8):
                        reg.register(gpio + row, 1, Datapoint("%s%s" % (col, row), validity=VALIDATOR, default=0))
                    gpio += 8
                self.addgroup(REG, REG + "_L")
                self.addgroup(REG, REG + "_H")

    def bits32(self, addr, *REGS):
        for REG in REGS:
            reg = Reg32(REG, addr)
            self.block(reg)
            gpio = 0
            for col in ["A", "B", "C", "D"]:
                for row in range(8):
                    reg.register(gpio, 1, Datapoint("%s%s" % (col, row), default=0, validity=Validator(0, 1)))
                    gpio += 1
            addr += 8

    def __init__(self, start=None):
        start = start or self.start
        super(GPIO, self).__init__(self.devname, start)

        self.interleave16bits(0x0, ("DATA", Validator(0, 1)),
                              ("DIRECTION", Validator(0, 1, "INPUT", "OUTPUT")),
                              ("INT_ENANBLE", Validator(0, 1)),
                              ("INT_MASK", Validator(0, 1)),
                              ("INT_TYPE", Validator(0, 1, "LEVEL", "EDGE")),
                              ("INT_POLARITY", Validator(0, 1, "ACTIVE_LOW", "ACTIVE_HIGH")),
                              ("INT_BOTHEDGE", Validator(0, 1)),
                              ("DEBOUNCE", Validator(0, 1)),
                              ("DBCLK_DIV_EN", Validator(0, 1)))

        reg = Reg32("DBCLK_DIV_CON", 0x48)
        self.block(reg)
        reg.register(0, 24, Datapoint("VALUE", default=1, validity=Validator(0, 2**24)))
        reg.register(24, 8, Datapoint("reserved", default=0, validity=Validator(0, 2**8)))

        self.bits32(0x50, "INT_STATUS", "INT_RAW_STATUS")
        self.interleave16bits(0x60, ("PORT_EOI", Validator(0, 1, "NOTHING", "CLEAREDGEINT")))
        self.bits32(0x70, "EXT_PORT")

        reg = Reg32("VERSION", 0x78)
        self.block(reg)
        reg.register(0, 32, Datapoint("ID", default=0x101157c, validity=Validator(0, 2**32)))

        self.interleave16bits(0x100, ("REG_REGORUP", Validator(0, 1)))

        reg = RK_Reg32_16bitMasked("VIRTUAL_EN", 0x108)
        self.block(reg)
        reg.register(0, 1, Datapoint("EN", default=0, validity=Validator(0, 1)))
        reg.register(1, 15, Datapoint("reserved", default=0, validity=Validator(0, 2**15)))
