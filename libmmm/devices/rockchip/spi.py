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
from libmmm import common


class SPI(Device):
    devname = ""
    start = 0

    def __init__(self, start=None):
        start = start or self.start
        super(SPI, self).__init__(self.devname, start)

        reg_ctrl0 = Reg32("CTRL0", 0)
        reg_ctrl0.register(0, 2, Datapoint("frame_len",
                                           validity=Validator(0, 3, "4bit", "8bit", "16bit", "reserved")))
        reg_ctrl0.register(2, 4, Datapoint("microwire_format",
                                           validity=Validator(0, 2 ** 4 - 1, *[f"reserved{x}" if x < 4 else f"{x + 1}bit" for x in range(16)])))
        reg_ctrl0.register(6, 1, Datapoint("motorola_clock_toggle",
                                           validity=Validator(0, 1, "MIDDLE", "START")))
        reg_ctrl0.register(7, 1, Datapoint("motorola_clock_polarity",
                                           validity=Validator(0, 1, "ACTIVELOW", "ACTIVEHIGH")))
        reg_ctrl0.register(8, 2, Datapoint("motorola_master_csm", validity=Validator(0, 3)))
        reg_ctrl0.register(10, 1, Datapoint("motorola_master_ssd", validity=Validator(0, 1)))
        reg_ctrl0.register(11, 1, Datapoint("endian", validity=Validator(0, 1, "LITTLE", "BIG")))
        reg_ctrl0.register(13, 1, Datapoint("ght", validity=Validator(0, 1)))
        reg_ctrl0.register(14, 2, Datapoint("master_rx_delay_cycles", validity=Validator(0, 3)))
        reg_ctrl0.register(16, 2, Datapoint("frame_format", validity=Validator(0, 3, "MOTOROLA", "TI", "MICROWIRE", "reserved")))
        reg_ctrl0.register(18, 2, Datapoint("mode", validity=Validator(0, 3, "RXTX", "TX", "RX", "reserved")))
        reg_ctrl0.register(20, 1, Datapoint("role", validity=Validator(0, 1, "MASTER", "SLAVE")))
        reg_ctrl0.register(21, 1, Datapoint("microwire_transfermode", validity=Validator(0, 1, "NONSEQ", "SEQ")))
        reg_ctrl0.register(22, 1, Datapoint("sm", validity=Validator(0, 1, common.OFF, common.ON)))
        reg_ctrl0.register(23, 1, Datapoint("loopback", validity=Validator(0, 1.)))
        self.block(reg_ctrl0)

        reg_ctrl1 = Reg32("CTRL1", 4)
        reg_ctrl1.register(0, 32, Datapoint("rx_num_frames", validity=Validator(0, 2 ** 32 - 1)))
        self.block(reg_ctrl1)

        reg_enable = Reg32("ENEABLE", 8)
        reg_enable.register(0, 1, Datapoint("enable", validity=Validator(0, 1)))
        self.block(reg_enable)

        reg_senable = Reg32("SLAVE_ENEABLE", 8)
        reg_senable.register(0, 2, Datapoint("slave_enable", validity=Validator(0, 3)))
        self.block(reg_senable)
