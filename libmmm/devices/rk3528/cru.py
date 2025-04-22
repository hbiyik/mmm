'''
Created on Mar 19, 2023

@author: boogie
'''
from libmmm.devices.rk3588.cru import CRU as Rk3588CRU
from libmmm.model import Device


class CRU(Rk3588CRU):
    start = 0xff4a0000

    def __init__(self, start=None):
        start = start or self.start
        Device.__init__(self, self.devname, start)

        self.reg_v0pll = self.fracpll_con(0x160, "V0PLL")
        self.reg_aupll = self.fracpll_con(0x180, "AUPLL")
        self.reg_cpll = self.fracpll_con(0x1a0, "CPLL")
        self.reg_gpll = self.fracpll_con(0x1c0, "GPLL")
        self.reg_npll = self.intpll_con(0x1e0, "NPLL")
        self.clksel(0x578, "GPU")
