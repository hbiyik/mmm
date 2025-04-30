'''
Created on Mar 19, 2023

@author: boogie
'''

from libmmm import common
from libmmm.model import Device, Datapoint, Validator, VirtualDatapoint
from libmmm.devices.rockchip import RK_Reg32_16bitMasked
from libmmm.devices.rk3588.grf import GPU_GRF


MUX = "MUX"
PVTPLL = "PVTPLL"
CPLL = "CPLL"
GPLL = "GPLL"
AUPLL = "AUPLL"
NPLL = "NPLL"
V0PLL = "V0PLL"
SPLL = "SPLL"
F100M = "100"
F50M = "50"
FXIN = "24"

clk_gpu_mux = "clk_gpu_mux"
clk_testout_gpu = "clk_testout_gpu"
clk_gpu_src = "clk_gpu_src"
clk_gpu = "clk_gpu"
clk_gpu_coregroup = "clk_gpu_coregroup"
clk_gpu_stacks = "clk_gpu_stacks"
aclk_s_gpu_biu = "aclk_s_gpu_biu"
aclk_m0_gpu_biu = "aclk_m0_gpu_biu"
aclk_m1_gpu_biu = "aclk_m1_gpu_biu"
aclk_m2_gpu_biu = "aclk_m2_gpu_biu"
aclk_m3_gpu_biu = "aclk_m3_gpu_biu"
pclk_gpu_root = "pclk_gpu_root"
pclk_gpu_biu = "pclk_gpu_biu"
pclk_pvtm2 = "pclk_pvtm2"
clk_pvtm2 = "clk_pvtm2"
clk_gpu_pvtm = "clk_gpu_pvtm"
pclk_gpu_grf = "pclk_gpu_grf_en"
clk_gpu_pvtpll = "clk_gpu_pvtpll"


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
    return _divided_freqs(*[x.get(common.PLLCLOCKNAME).value for x in base_regs if x],
                          minfreq=minfreq,
                          maxdiv=maxdiv)


class ClkSel(VirtualDatapoint):
    def __init__(self, cru=None,
                 selreg=None, divreg=None, muxreg=None, parentreg=None,
                 name="clock",
                 selname="sel", muxname="mux", divname="div", parentname=None,
                 pvtdev=None, pvtregname=None, pvtname=common.PVTCLOCKNAME):
        VirtualDatapoint.__init__(self, name, unit=common.MHZ)

        self.cru = cru

        self.selreg = selreg
        self.muxreg = muxreg
        self.divreg = divreg
        self.parentreg = parentreg

        self.selname = selname
        self.muxname = muxname
        self.divname = divname
        self.parentname = parentname

        self.pvtdev = pvtdev
        self.pvtregname = pvtregname
        self.pvtname = pvtname

        self.muxmap = {GPLL: cru.reg_gpll,
                       CPLL: cru.reg_cpll,
                       AUPLL: cru.reg_aupll,
                       NPLL: cru.reg_npll}

        self.selmap = {F100M: F100M,
                       F50M: F50M,
                       FXIN: FXIN,
                       PVTPLL: PVTPLL,
                       MUX: MUX}

    def getpvtpll(self):
        if not self.pvtdev:
            return -5
        pdev = self.pvtdev()
        reg = pdev.getblock(self.pvtregname)
        val = int(reg.get(self.pvtname).value)
        return val

    def getmux(self):
        if not self.muxreg:
            return -3
        self.muxreg.read()
        mux = self.muxreg.get(self.muxname).value
        if mux not in self.muxmap:
            return -4
        reg = self.muxmap[mux]
        reg.read()
        return self.getdiv(reg.get(common.PLLCLOCKNAME).value)

    def getdiv(self, clock):
        if not self.divreg:
            return self.clock
        self.divreg.read()
        return int(clock / (self.divreg.get(self.divname).value + 1))

    def get(self):
        if self.parentreg:
            self.parentreg.read()
            return self.getdiv(self.parentreg.get(self.parentname).value)
        if not self.selreg:
            return -1
        self.selreg.read()
        sel = self.selreg.get(self.selname).value
        if sel not in self.selmap:
            return -2
        if sel == MUX:
            return self.getmux()
        elif sel == PVTPLL:
            return self.getpvtpll()
        return self.getdiv(int(sel))


class FracPLL(VirtualDatapoint):
    def __init__(self, con0, con1, con2, basef=24, factor=1, name="clock"):
        VirtualDatapoint.__init__(self, name, unit=common.MHZ)
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
        VirtualDatapoint.__init__(self, name, unit=common.MHZ)
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


class BatchClockGate(VirtualDatapoint):
    def __init__(self, name, regs, points):
        VirtualDatapoint.__init__(self, name, validity=Validator(0, 1, common.OFF, common.ON))
        self.regs = regs
        self.points = points
        self.allowwrite = True

    def getreg(self, point):
        for reg in self.regs:
            dp = reg.get(point)
            if dp:
                return reg, dp

    def get(self):
        for point in self.points:
            _reg, dp = self.getreg(point)
            if not dp:
                return 0
            if dp.value == common.OFF:
                return 0
        return 1

    def set(self, value):
        value = [common.OFF, common.ON][value]
        for point in self.points:
            reg, dp = self.getreg(point)
            if not dp:
                continue
            if not dp.value == value:
                reg.write(dp.name, value)


class CRU(Device):
    devname = "CRU"
    start = 0xFD7C0000

    def __init__(self, start=None):
        start = start or self.start
        super(CRU, self).__init__(self.devname, start)

        self.reg_v0pll = self.fracpll_con(0x160, V0PLL)
        self.reg_aupll = self.fracpll_con(0x180, AUPLL)
        self.reg_cpll = self.fracpll_con(0x1a0, CPLL)
        self.reg_gpll = self.fracpll_con(0x1c0, GPLL)
        self.reg_npll = self.intpll_con(0x1e0, NPLL)
        self.gpu()

    def regfromoffset(self, offset, base=0x300, prefix="CLKSEL_"):
        regnum = int((offset - base) / 4)
        regname = f"{prefix}{regnum}"
        reg = RK_Reg32_16bitMasked(regname, offset)
        self.block(reg)
        return reg

    def clksel_mux_snacg_pll_pvt(self, offset, name, nametest):
        CLKSEL_REG = self.regfromoffset(offset)
        CLKSEL_REG.register(0, 5, Datapoint(f"{name}_div", default=0, validity=Validator(0, 2 ** 5 - 1)))
        CLKSEL_REG.register(5, 3, Datapoint(f"{name}_mux", default=0, validity=Validator(0, 7, GPLL, CPLL, AUPLL, NPLL, SPLL)))
        CLKSEL_REG.register(8, 5, Datapoint(f"{nametest}_div", default=0, validity=Validator(0, 2 ** 5 - 1)))
        CLKSEL_REG.register(13, 1, Datapoint(f"{nametest}_sel", default=0, validity=Validator(0, 1, MUX, PVTPLL)))
        CLKSEL_REG.register(14, 1, Datapoint(f"{name}_sel", default=0, validity=Validator(0, 1, MUX, PVTPLL)))
        CLKSEL_REG.register(15, 1, Datapoint("reserved", default=0))
        CLKSEL_REG.register(None, None, ClkSel(self,
                                               name=f"{name}_{common.PLLCLOCKNAME}",
                                               selreg=CLKSEL_REG,
                                               muxreg=CLKSEL_REG,
                                               divreg=CLKSEL_REG,
                                               selname=f"{name}_sel",
                                               muxname=f"{name}_mux",
                                               divname=f"{name}_div",
                                               pvtdev=GPU_GRF, pvtregname="PVTPLL_STATUS1",
                                               ))
        CLKSEL_REG.register(None, None, ClkSel(self,
                                               name=f"{name}_testout_{common.PLLCLOCKNAME}",
                                               selreg=CLKSEL_REG,
                                               muxreg=CLKSEL_REG,
                                               divreg=CLKSEL_REG,
                                               selname=f"{nametest}_sel",
                                               muxname=f"{name}_mux",
                                               divname=f"{nametest}_div",
                                               pvtdev=GPU_GRF, pvtregname="PVTPLL_STATUS1",
                                               ))
        return CLKSEL_REG

    def clksel_mux3_div(self, offset, name1, name2, name3, parentreg=None, parentname=None):
        regs = []
        reg = self.regfromoffset(offset)
        for i, name in enumerate([name1, name2, name3]):
            reg.register(0 + i * 5, 5, Datapoint(f"{name}_div", default=0, validity=Validator(0, 2 ** 5 - 1)))
            if parentreg:
                reg.register(None, None, ClkSel(cru=self,
                                                name=f"{name}_{common.PLLCLOCKNAME}",
                                                parentreg=parentreg,
                                                divreg=reg,
                                                parentname=parentname,
                                                divname=f"{name}_div"
                                                ))
            regs.append(reg)
        return regs

    def gpu(self):
        gname = "GPU"
        basereg = self.clksel_mux_snacg_pll_pvt(0x578, clk_gpu_src, clk_testout_gpu)
        self.addgroup(gname, basereg.name)
        for reg in self.clksel_mux3_div(0x57C, clk_gpu_stacks, aclk_s_gpu_biu, aclk_m0_gpu_biu,
                                        basereg, f"{clk_gpu_src}_clock"):
            self.addgroup(gname, reg.name)
        for reg in self.clksel_mux3_div(0x580, aclk_m1_gpu_biu, aclk_m2_gpu_biu, aclk_m3_gpu_biu,
                                        basereg, f"{clk_gpu_src}_clock"):
            self.addgroup(gname, reg.name)
        reg = self.regfromoffset(0x584)
        reg.register(0, 2, Datapoint(f"{pclk_gpu_root}_sel", default=0, unit=common.MHZ,
                                     validity=Validator(0, 2 ** 2 - 1, F100M, F50M, FXIN)))
        reg.register(2, 1, Datapoint(f"clk_gpu_pvtpll_sel", default=0, unit=common.MHZ,
                                     validity=Validator(0, 1, "GPU_SRC", FXIN)))
        self.block(reg)
        self.addgroup(gname, reg.name)

        offset = 0x908
        gpu_clocks = [None, clk_gpu_mux, clk_testout_gpu, clk_gpu_src,
                      clk_gpu, None, clk_gpu_coregroup, clk_gpu_stacks,
                      aclk_s_gpu_biu, aclk_m0_gpu_biu, aclk_m1_gpu_biu,
                      aclk_m2_gpu_biu, aclk_m3_gpu_biu, pclk_gpu_root,
                      pclk_gpu_biu, pclk_pvtm2, clk_pvtm2, clk_gpu_pvtm,
                      pclk_gpu_grf, clk_gpu_pvtpll]

        gateregs = []
        for clk_names in common.iterlistchunks(gpu_clocks, 16):
            reg = self.clkgate(offset, *clk_names)
            gateregs.append(reg)
            self.block(reg)
            self.addgroup(gname, reg.name)
            offset += 4

        gateregs[0].register(None, None, BatchClockGate("clk_gpu_all", gateregs,
                                                        [x for x in gpu_clocks if x is not None]))

    def clkgate(self, offset, *clk_names):
        reg = self.regfromoffset(offset, base=0x800, prefix="CLKGATE_")
        for i, clk_name in enumerate(clk_names):
            if clk_name is None:
                continue
            reg.register(i, 1, Datapoint(f"{clk_name}", default=0, validity=Validator(0, 1, common.ON, common.OFF)))
        return reg

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
        PLL_CON6 = RK_Reg32_16bitMasked(f"{name}_CON6", offset)
        offset += 4

        self.block(PLL_CON2)
        self.block(PLL_CON3)
        self.block(PLL_CON4)
        self.block(PLL_CON5)
        self.block(PLL_CON6)

        for i in range(7):
            self.addgroup(name, f"{name}_CON{i}")

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

        self.addgroup(name, f"{name}_CON0")
        self.addgroup(name, f"{name}_CON1")
        self.addgroup(name, f"{name}_CON4")
        self.addgroup(name, f"{name}_CON5")
        self.addgroup(name, f"{name}_CON6")

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


class SBUSCRU(CRU):
    devname = "SBUSCRU"
    start = 0xFD7D8000

    def __init__(self, start=None):
        start = start or self.start
        Device.__init__(self, self.devname, start)

        self.reg_spll = self.intpll_con(0x220, SPLL)
