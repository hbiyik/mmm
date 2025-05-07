'''
Created on Mar 19, 2023

@author: boogie
'''
from libmmm.devices.rk3588.cru import CRU as Rk3588CRU
from libmmm.model import Device


class CRU(Rk3588CRU):
    devname = "CRU"
    start = 0xff4a0000

    def __init__(self, start=None):
        start = start or self.start
        Device.__init__(self, self.devname, start)

        clks = [None] * 16
        clks[0] = "aclk_gpu_root"
        clks[2] = "pclk_gpu_root"
        clks[7] = "aclk_gpu"
        clks[8] = "aclk_gpu_mali"
        reg = self.clkgate(0x800 + 34 * 4, *clks)
        self.block(reg)
