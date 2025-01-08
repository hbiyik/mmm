'''
Created on Mar 19, 2023

@author: boogie
'''
from libmmm.model import Device, Datapoint, Validator, VirtualDatapoint
from libmmm.devices.rockchip import RK_Reg32_16bitMasked


def _divided_freqs(*clocks, minfreq=100, maxdiv=32):
    freqs = []
    for clock in clocks:
        div = int(clock / minfreq)
        while div:
            freq = (clock / div)
            freqs.append([int(freq), clock, div])
            div -= 1
    return sorted(freqs)


def divided_freqs(*base_regs, minfreq=100, maxdiv=32):
    return _divided_freqs(*[x.get("clock").value for x in base_regs if x],
                          minfreq=minfreq,
                          maxdiv=maxdiv)


class ClkSel(VirtualDatapoint):
    def __init__(self, reg, gpll, cpll, aupll, npll, spll, name="clock"):
        VirtualDatapoint.__init__(self, name, unit="Mhz")
        self.reg = reg
        self.clockregs = {"GPLL": gpll,
                          "CPLL": cpll,
                          "AUPLL": aupll,
                          "NPLL": npll,
                          "SPLL": spll}

    def get(self):
        self.reg.read()
        mux = self.reg.get("mux").value
        if mux == "PLL":
            sel = self.reg.get("sel").value
            div = self.reg.get("div").value
            source_clock = self.clockregs[sel].get("clock").value
            return int(source_clock / (div + 1))
        return 0


class FracPLL(VirtualDatapoint):
    def __init__(self, con0, con1, con2, basef=24, factor=1, name="clock"):
        VirtualDatapoint.__init__(self, name, unit="Mhz")
        self.con0 = con0
        self.con1 = con1
        self.con2 = con2
        self.basef = basef
        self.factor = factor

    def get(self):
        self.con0.read()
        self.con1.read()
        self.con2.read()
        m = self.con0.get("m").value
        p = self.con1.get("p").value
        s = self.con1.get("s").value
        k = self.con2.get("k").value
        return int(((m + k / 65536) * self.basef * self.factor) / (p * (2 ** s)))

    def set(self, value):
        pass


class IntPLL(VirtualDatapoint):
    def __init__(self, con0, con1, basef=24, name="clock"):
        VirtualDatapoint.__init__(self, name, unit="Mhz")
        self.con0 = con0
        self.con1 = con1
        self.basef = basef

    def get(self):
        self.con0.read()
        self.con1.read()
        m = self.con0.get("m").value
        p = self.con1.get("p").value
        s = self.con1.get("s").value
        try:
            return int((m * self.basef) / (p * (2 ** s)))
        except ZeroDivisionError:
            return 0

    def set(self, value):
        pass


class CRU(Device):
    devname = "CRU"
    start = 0xFD7C0000

    def clksel(self, offset, name):
        CLKSEL_CON = RK_Reg32_16bitMasked(f"{name}_CLKSEL", offset)
        self.block(CLKSEL_CON)
        CLKSEL_CON.register(0, 5, Datapoint("div", default=0, validity=Validator(0, 2 ** 5 - 1)))
        CLKSEL_CON.register(5, 3, Datapoint("sel", default=0, validity=Validator(0, 7, "GPLL", "CPLL", "AUPLL", "NPLL", "SPLL")))
        CLKSEL_CON.register(8, 5, Datapoint("testout_div", default=0, validity=Validator(0, 2 ** 5 - 1)))
        CLKSEL_CON.register(13, 1, Datapoint("testout_mux", default=0, validity=Validator(0, 1, "PLL", "PVTM")))
        CLKSEL_CON.register(14, 1, Datapoint("mux", default=0, validity=Validator(0, 1, "PLL", "PVTM")))
        CLKSEL_CON.register(15, 1, Datapoint("reserved", default=0))
        CLKSEL_CON.register(None, None, ClkSel(CLKSEL_CON, self.reg_gpll, self.reg_cpll, self.reg_aupll, self.reg_npll, None))

    def pll_concommon(self, offset, name):
        PLL_CON0 = RK_Reg32_16bitMasked(f"{name}_CON0", offset)
        offset += 4
        PLL_CON1 = RK_Reg32_16bitMasked(f"{name}_CON1", offset)
        offset += 4
        self.block(PLL_CON0)
        self.block(PLL_CON1)
        PLL_CON0.register(0, 9, Datapoint("m", default=0, validity=Validator(0, 2 ** 10 - 1)))
        PLL_CON0.register(10, 5, Datapoint("reserved", default=0))
        PLL_CON0.register(15, 1, Datapoint("bypass", default=0, validity=Validator(0, 1)))

        PLL_CON1.register(0, 6, Datapoint("p", default=0, validity=Validator(0, 2**6 - 1)))
        PLL_CON1.register(6, 3, Datapoint("s", default=0, validity=Validator(0, 6)))
        PLL_CON1.register(9, 4, Datapoint("reserved", default=0))
        PLL_CON1.register(13, 1, Datapoint("reset", default=0, validity=Validator(0, 1)))
        PLL_CON1.register(14, 2, Datapoint("reserved", default=0))

        return PLL_CON0, PLL_CON1, offset

    def fracpll_con(self, offset, name):
        PLL_CON0, PLL_CON1, offset = self.pll_concommon(offset, name)
        PLL_CON2 = RK_Reg32_16bitMasked(f"{name}_CON2", offset)
        offset += 4
        PLL_CON3 = RK_Reg32_16bitMasked(f"{name}_CON3", offset)
        offset += 4
        PLL_CON4 = RK_Reg32_16bitMasked(f"{name}_CON4", offset)
        offset += 4
        PLL_CON5 = RK_Reg32_16bitMasked(f"{name}_CON5", offset)
        offset += 4
        PLL_CON6 = RK_Reg32_16bitMasked(f"{name}L_CON6", offset)
        offset += 4

        self.block(PLL_CON2)
        self.block(PLL_CON3)
        self.block(PLL_CON4)
        self.block(PLL_CON5)
        self.block(PLL_CON6)

        PLL_CON2.register(0, 16, Datapoint("k", default=0, validity=Validator(0, 2**16 - 1)))

        PLL_CON3.register(0, 8, Datapoint("mfr", default=0, validity=Validator(0, 2**8 - 1)))
        PLL_CON3.register(8, 6, Datapoint("mrr", default=0, validity=Validator(0, 2**6 - 1)))
        PLL_CON3.register(14, 2, Datapoint("selpf", default=0, validity=Validator(0, 2**2 - 1)))

        PLL_CON4.register(0, 1, Datapoint("sscg_en", default=0, validity=Validator(0, 1)))
        PLL_CON4.register(1, 2, Datapoint("reserved", default=0))
        PLL_CON4.register(3, 1, Datapoint("afc_en", default=0, validity=Validator(0, 1)))
        PLL_CON4.register(4, 5, Datapoint("ext_afc", default=0, validity=Validator(0, 2**5 - 1)))
        PLL_CON4.register(9, 5, Datapoint("reserved", default=0))
        PLL_CON4.register(14, 1, Datapoint("feed_en", default=0, validity=Validator(0, 1)))
        PLL_CON4.register(15, 1, Datapoint("fsel", default=0, validity=Validator(0, 1)))

        PLL_CON5.register(0, 1, Datapoint("fout_mask", default=0, validity=Validator(0, 1)))
        PLL_CON5.register(1, 15, Datapoint("reserved", default=0))

        PLL_CON6.register(0, 10, Datapoint("reserved", default=0))
        PLL_CON6.register(10, 5, Datapoint("afc_code", default=0, validity=Validator(0, 2**5 - 1)))
        PLL_CON6.register(15, 1, Datapoint("lock", default=0, validity=Validator(0, 1)))
        PLL_CON0.register(None, None, FracPLL(PLL_CON0, PLL_CON1, PLL_CON2))
        return PLL_CON0

    def intpll_con(self, offset, name):
        PLL_CON0, PLL_CON1, offset = self.pll_concommon(offset, name)
        PLL_CON0.register(None, None, IntPLL(PLL_CON0, PLL_CON1))

        offset += 8
        PLL_CON4 = RK_Reg32_16bitMasked(f"{name}_CON4", offset)
        offset += 4
        PLL_CON5 = RK_Reg32_16bitMasked(f"{name}_CON5", offset)
        offset += 4
        PLL_CON6 = RK_Reg32_16bitMasked(f"{name}_CON6", offset)
        offset += 4

        self.block(PLL_CON4)
        self.block(PLL_CON5)
        self.block(PLL_CON6)

        PLL_CON4.register(0, 1, Datapoint("reserved", default=0, validity=Validator(0, 1)))
        PLL_CON4.register(1, 2, Datapoint("icp", default=0, validity=Validator(0, 3)))
        PLL_CON4.register(3, 1, Datapoint("afc_en", default=0, validity=Validator(0, 1)))
        PLL_CON4.register(4, 5, Datapoint("ext_afc", default=0, validity=Validator(0, 2**5 - 1)))
        PLL_CON4.register(9, 5, Datapoint("reserved", default=0))
        PLL_CON4.register(14, 1, Datapoint("feed_en", default=0, validity=Validator(0, 1)))
        PLL_CON4.register(15, 1, Datapoint("fsel", default=0, validity=Validator(0, 1)))

        PLL_CON5.register(0, 1, Datapoint("fout_mask", default=0, validity=Validator(0, 1)))
        PLL_CON5.register(1, 4, Datapoint("reserved", default=0))
        PLL_CON5.register(5, 2, Datapoint("loc_con_in", default=0, validity=Validator(0, 3)))
        PLL_CON5.register(7, 2, Datapoint("loc_con_out", default=0, validity=Validator(0, 3)))
        PLL_CON5.register(9, 2, Datapoint("loc_con_dly", default=0, validity=Validator(0, 3)))
        PLL_CON5.register(11, 5, Datapoint("reserved", default=0))

        PLL_CON6.register(0, 10, Datapoint("reserved", default=0))
        PLL_CON6.register(10, 5, Datapoint("afc_code", default=0, validity=Validator(0, 2**5 - 1)))
        PLL_CON6.register(15, 1, Datapoint("lock", default=0, validity=Validator(0, 1)))

        return PLL_CON0

    def __init__(self, start=None):
        start = start or self.start
        super(CRU, self).__init__(self.devname, start)

        self.reg_v0pll = self.fracpll_con(0x160, "V0PLL")
        self.reg_aupll = self.fracpll_con(0x180, "AUPLL")
        self.reg_cpll = self.fracpll_con(0x1a0, "CPLL")
        self.reg_gpll = self.fracpll_con(0x1c0, "GPLL")
        self.reg_npll = self.intpll_con(0x1e0, "NPLL")
        self.clksel(0x578, "GPU")


class SBUSCRU(CRU):
    devname = "SBUSCRU"
    start = 0xFD7D8000

    def __init__(self, start=None):
        start = start or self.start
        Device.__init__(self, self.devname, start)

        self.reg_spll = self.intpll_con(0x220, "SPLL")
