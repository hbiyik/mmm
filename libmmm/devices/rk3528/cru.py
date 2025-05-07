'''
Created on Mar 19, 2023

@author: boogie
'''
from libmmm.devices.rk3588.cru import CRU as Rk3588CRU
from libmmm.model import Device, Datapoint, Validator
from libmmm import common

# FIX-ME: This is actually a divided clock with mux to c/gpll
F500M = "F500M"
F300M = "F300M"
F100M = "F100M"
CLOCK_F100M = 100
CLOCK_F300M = 300
CLOCK_F500M = 500

XIN = "XIN"
CLOCK_XIN = 24


class CRU(Rk3588CRU):
    devname = "CRU"
    start = 0xff4a0000

    def __init__(self, start=None):
        start = start or self.start
        Device.__init__(self, self.devname, start)

        clksel_gpu = self.regfromoffset(0x300 + 4 * 76, base=0x300, prefix="CLKSEL_")
        clksel_gpu.register(0, 2, datapoint=Datapoint("aclk_gpu_root_mux", validity=Validator(0, 3, F500M, F300M, F100M, XIN)))
        clksel_gpu.register(2, 3, datapoint=Datapoint("unk2_3", validity=Validator(0, 3)))
        clksel_gpu.register(4, 2, datapoint=Datapoint("pclk_gpu_root_mux", validity=Validator(0, 3, F500M, F300M, F100M, XIN)))
        clksel_gpu.register(6, 1, datapoint=Datapoint("gpu_clock_source", validity=Validator(0, 1, "MUX", "PVTPLL")))
        clksel_gpu.register(7, 1, datapoint=Datapoint("unk7", validity=Validator(0, 1)))
        clksel_gpu.register(8, 1, datapoint=Datapoint("unk8", validity=Validator(0, 1)))
        clksel_gpu.register(9, 1, datapoint=Datapoint("unk9", validity=Validator(0, 1)))
        clksel_gpu.register(10, 1, datapoint=Datapoint("unk10", validity=Validator(0, 1)))
        clksel_gpu.register(11, 1, datapoint=Datapoint("unk11", validity=Validator(0, 1)))
        clksel_gpu.register(12, 1, datapoint=Datapoint("unk12", validity=Validator(0, 1)))
        clksel_gpu.register(13, 1, datapoint=Datapoint("unk13", validity=Validator(0, 1)))
        clksel_gpu.register(14, 1, datapoint=Datapoint("unk14", validity=Validator(0, 1)))
        clksel_gpu.register(15, 1, datapoint=Datapoint("unk15", validity=Validator(0, 1)))
        self.block(clksel_gpu)

        gpu_clks = [None] * 16
        gpu_clks[0] = "aclk_gpu_root"
        gpu_clks[2] = "pclk_gpu_root"
        gpu_clks[7] = "aclk_gpu"
        gpu_clks[8] = "aclk_gpu_mali"
        clkgate_gpu = self.clkgate(0x800 + 34 * 4, *gpu_clks)
        self.block(clkgate_gpu)

        self.addgroup("GPU", clksel_gpu.name)
        self.addgroup("GPU", clkgate_gpu.name)
