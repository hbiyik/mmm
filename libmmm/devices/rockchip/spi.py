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
        reg_ctrl0.register(12, 1, Datapoint("bitorder", validity=Validator(0, 1, "MSB", "LSB")))
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

        reg_enable = Reg32("ENABLE", 8)
        reg_enable.register(0, 1, Datapoint("enable", validity=Validator(0, 1)))
        self.block(reg_enable)

        reg_senable = Reg32("SLAVE_ENABLE", 0xc)
        reg_senable.register(0, 2, Datapoint("slave_enable", validity=Validator(0, 3)))
        self.block(reg_senable)

        reg_baudrate = Reg32("BAUDRATE", 0x10)
        reg_baudrate.register(0, 15, Datapoint("clk_div", validity=Validator(0, 2 ** 15 - 1)))
        self.block(reg_baudrate)

        reg = Reg32("TXFTLR", 0x14)
        reg.register(0, 5, Datapoint("int_tx_min_entries", validity=Validator(0, 2 ** 5 - 1)))
        self.block(reg)

        reg = Reg32("RXFTLR", 0x18)
        reg.register(0, 5, Datapoint("int_rx_min_entries", validity=Validator(0, 2 ** 5 - 1)))
        self.block(reg)

        reg = Reg32("TXFLR", 0x1c)
        reg.allowwrite = False
        reg.register(0, 6, Datapoint("tx_num_entries", validity=Validator(0, 2 ** 6 - 1)))
        self.block(reg)

        reg = Reg32("RXFLR", 0x20)
        reg.allowwrite = False
        reg.register(0, 6, Datapoint("rx_num_entries", validity=Validator(0, 2 ** 6 - 1)))
        self.block(reg)

        reg = Reg32("STATUS", 0x24)
        reg.allowwrite = False
        reg.register(0, 1, Datapoint("tx_busy", validity=Validator(0, 1)))
        reg.register(1, 1, Datapoint("tx_full", validity=Validator(0, 1)))
        reg.register(2, 1, Datapoint("tx_empty", validity=Validator(0, 1)))
        reg.register(3, 1, Datapoint("rx_empty", validity=Validator(0, 1)))
        reg.register(4, 1, Datapoint("rx_full", validity=Validator(0, 1)))
        reg.register(5, 1, Datapoint("slave_tx_busy", validity=Validator(0, 1)))
        reg.register(6, 1, Datapoint("ssi", validity=Validator(0, 1)))
        self.block(reg)

        reg = Reg32("INT_POLARITY", 0x28)
        reg.register(0, 1, Datapoint("int_polarity", validity=Validator(0, 1)))
        self.block(reg)

        offset = 0x2c
        for regname in ["INT_MASK", "INT_STATUS_MASKED", "INT_STATUS_UNMASKED"]:
            reg = Reg32(regname, offset)
            reg.register(0, 1, Datapoint("tx_error", validity=Validator(0, 1)))
            reg.register(1, 1, Datapoint("tx_overflow", validity=Validator(0, 1)))
            reg.register(2, 1, Datapoint("rx_underflow", validity=Validator(0, 1)))
            reg.register(3, 1, Datapoint("rx_overflow", validity=Validator(0, 1)))
            reg.register(4, 1, Datapoint("rxf", validity=Validator(0, 1)))
            reg.register(5, 1, Datapoint("timeout", validity=Validator(0, 1)))
            reg.register(6, 1, Datapoint("ss_in", validity=Validator(0, 1)))
            reg.register(7, 1, Datapoint("tx_finish", validity=Validator(0, 1)))
            self.block(reg)
            offset += 4

        reg = Reg32("INT_CLEAR", 0x38)
        reg.register(0, 1, Datapoint("combined", validity=Validator(0, 1)))
        reg.register(1, 1, Datapoint("rx_underflow", validity=Validator(0, 1)))
        reg.register(2, 1, Datapoint("rx_overflow", validity=Validator(0, 1)))
        reg.register(3, 1, Datapoint("tx_overflow", validity=Validator(0, 1)))
        reg.register(4, 1, Datapoint("timeout", validity=Validator(0, 1)))
        reg.register(5, 1, Datapoint("ss_in", validity=Validator(0, 1)))
        reg.register(6, 1, Datapoint("tx_finish", validity=Validator(0, 1)))
        self.block(reg)

        reg = Reg32("DMACR", 0x3c)
        reg.register(0, 1, Datapoint("rx_enable", validity=Validator(0, 1)))
        reg.register(1, 1, Datapoint("tx_enable", validity=Validator(0, 1)))
        self.block(reg)

        reg = Reg32("DMATDLR", 0x40)
        reg.register(0, 5, Datapoint("dma_tx_min_entries", validity=Validator(0, 2 ** 5 - 1)))
        self.block(reg)

        reg = Reg32("DMARDLR", 0x44)
        reg.register(0, 5, Datapoint("dma_rx_min_entries", validity=Validator(0, 2 ** 5 - 1)))
        self.block(reg)

        reg = Reg32("VERSION", 0x48)
        reg.allowwrite = False
        reg.register(0, 32, Datapoint("version", validity=Validator(0, 2 ** 32 - 1)))
        self.block(reg)

        reg = Reg32("TIMEOUT", 0x4c)
        reg.register(0, 16, Datapoint("threshold", validity=Validator(0, 2 ** 16 - 1)))
        reg.register(16, 1, Datapoint("enable", validity=Validator(0, 1)))
        self.block(reg)

        reg = Reg32("BYPASS", 0x50)
        reg.register(0, 1, Datapoint("enable", validity=Validator(0, 1)))
        reg.register(1, 1, Datapoint("bitorder", validity=Validator(0, 1, "LSB", "MSB")))
        reg.register(2, 1, Datapoint("endian", validity=Validator(0, 1, "LITTLE", "BIG")))
        reg.register(3, 1, Datapoint("rx_ploarity", validity=Validator(0, 1, "RAW", "INVERTED")))
        reg.register(4, 1, Datapoint("tx_ploarity", validity=Validator(0, 1, "RAW", "INVERTED")))
        self.block(reg)

        reg = Reg32("TXDR", 0x400)
        reg.register(0, 16, Datapoint("txdr", validity=Validator(0, 1)))
        self.block(reg)

        reg = Reg32("RXDR", 0x800)
        reg.register(0, 16, Datapoint("rxdr", validity=Validator(0, 1)))
        reg.allowwrite = False
        self.block(reg)

        self.addgroup("FIFO", "TXDR")
        self.addgroup("FIFO", "RXDR")

        self.addgroup("CONTROL", "CTRL0")
        self.addgroup("CONTROL", "CTRL1")
        self.addgroup("CONTROL", "ENABLE")
        self.addgroup("CONTROL", "SLAVE_ENABLE")
        self.addgroup("CONTROL", "BAUDRATE")
        self.addgroup("CONTROL", "TIMEOUT")
        self.addgroup("CONTROL", "BYPASS")

        self.addgroup("DMA", "DMACR")
        self.addgroup("DMA", "DMATDLR")
        self.addgroup("DMA", "DMARDLR")

        self.addgroup("STATUS", "STATUS")
        self.addgroup("STATUS", "VERSION")
        self.addgroup("STATUS", "TXFLR")
        self.addgroup("STATUS", "RXFLR")

        self.addgroup("INTERRUPT", "TXFTLR")
        self.addgroup("INTERRUPT", "RXFTLR")
        self.addgroup("INTERRUPT", "INT_POLARITY")
        self.addgroup("INTERRUPT", "INT_MASK")
        self.addgroup("INTERRUPT", "INT_STATUS_MASKED")
        self.addgroup("INTERRUPT", "INT_STATUS_UNMASKED")
        self.addgroup("INTERRUPT", "INT_CLEAR")
