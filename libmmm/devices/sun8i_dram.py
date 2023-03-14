'''
Created on Nov 8, 2022

@author: boogie
'''
from libmmm.model import Device, Reg32, Datapoint

# based on:
# https://github.com/u-boot/u-boot/blob/master/arch/arm/include/asm/arch-sunxi/dram_sun8i_a33.h
# https://github.com/allwinner-zh/bootloader/blob/master/basic_loader/bsp/bsp_for_a33/init_dram/mctl_reg.h
# https://www.xilinx.com/htmldocs/registers/ug1087/ug1087-zynq-ultrascale-registers.html#mod___ddrc.html

class DRAM_COM(Device):
        def __init__(self, start=0x01C62000):
            super(DRAM_COM, self).__init__("DRAM_COM" , start)
            CTRL_REG = Reg32("CTRL_REG", 0x0)
            CTRL_REG.register(0, 2, Datapoint("RANK"))
            CTRL_REG.register(2, 2, Datapoint("BANK"))
            CTRL_REG.register(4, 4, Datapoint("ROW"))
            CTRL_REG.register(8, 4, Datapoint("PAGE_SIZE"))
            CTRL_REG.register(12, 3, Datapoint("BUS_WIDTH"))
            CTRL_REG.register(15, 1, Datapoint("SEQUENCE"))
            CTRL_REG.register(16, 2, Datapoint("DDR3"))
            CTRL_REG.register(19, 1, Datapoint("CHANNEL"))
            self.block(CTRL_REG)

class DRAM_CTL(Device):
        def __init__(self, start=0x01C63000):
            super(DRAM_CTL, self).__init__("DRAM_CTL" , start)
            DRAM_TMG0 = Reg32("DRAM_TMG0", 0x58)
            DRAM_TMG0.register(0, 8, Datapoint("tRASMIN"))
            DRAM_TMG0.register(8, 8, Datapoint("tRASMAX"))
            DRAM_TMG0.register(16, 8, Datapoint("tFAW"))
            DRAM_TMG0.register(24, 8, Datapoint("tWR2PRE"))
            self.block(DRAM_TMG0)
            DRAM_TMG1 = Reg32("DRAM_TMG1", 0x5c)
            DRAM_TMG1.register(0, 8, Datapoint("tRC"))
            DRAM_TMG1.register(8, 8, Datapoint("tRD2PRE"))
            DRAM_TMG1.register(16, 8, Datapoint("tXP"))
            self.block(DRAM_TMG1)
            DRAM_TMG2 = Reg32("DRAM_TMG2", 0x60)
            DRAM_TMG2.register(0, 8, Datapoint("tWR2RD"))
            DRAM_TMG2.register(8, 8, Datapoint("tRD2WR"))
            DRAM_TMG2.register(16, 8, Datapoint("tCL"))
            DRAM_TMG2.register(24, 8, Datapoint("tCWL"))
            self.block(DRAM_TMG2)
            DRAM_TMG3 = Reg32("DRAM_TMG3", 0x64)
            DRAM_TMG3.register(0, 8, Datapoint("tMOD"))
            DRAM_TMG3.register(8, 8, Datapoint("tMRD"))
            DRAM_TMG3.register(16, 8, Datapoint("tMRW"))
            self.block(DRAM_TMG3)
            DRAM_TMG4 = Reg32("DRAM_TMG4", 0x68)
            DRAM_TMG4.register(0, 8, Datapoint("tRP"))
            DRAM_TMG4.register(8, 8, Datapoint("tRRD"))
            DRAM_TMG4.register(16, 8, Datapoint("tCCD"))
            DRAM_TMG4.register(24, 8, Datapoint("tRCD"))
            self.block(DRAM_TMG4)
            DRAM_TMG5 = Reg32("DRAM_TMG5", 0x6c)
            DRAM_TMG5.register(0, 8, Datapoint("tCKE"))
            DRAM_TMG5.register(8, 8, Datapoint("tCKESR"))
            DRAM_TMG5.register(16, 8, Datapoint("tCKSRE"))
            DRAM_TMG5.register(24, 8, Datapoint("tCKSRX"))
            self.block(DRAM_TMG5)
