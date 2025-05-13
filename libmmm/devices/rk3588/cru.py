'''
Created on Mar 19, 2023

@author: boogie
'''

from libmmm import common
from libmmm.model import Device, Datapoint, Validator, VirtualDatapoint
from libmmm.devices.rockchip import RK_Reg32_16bitMasked
from libmmm.devices.rk3588.grf import GRF_GPU, GRF_BIGCORE0, GRF_BIGCORE1


MUX = "MUX"
PVTPLL = "PVTPLL"
CPLL = "CPLL"
GPLL = "GPLL"
AUPLL = "AUPLL"
NPLL = "NPLL"
V0PLL = "V0PLL"
APLL = "APLL"
BPLL = "BPLL"
B0PLL = "B0PLL"
B1PLL = "B1PLL"
SPLL = "SPLL"
F100M = "F100M"
F50M = "F50M"
XIN = "XIN"
FDEEP = "FDEEP"

CLOCK_F100M = 100
CLOCK_F50M = 50
CLOCK_XIN = 24
CLOCK_FDEEP = 2


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

pclk_ddr_cru_ch0 = "pclk_ddr_cru_ch0"
pclk_ddrphy_ch0 = "pclk_ddrphy_ch0"
clk_osc_ddrphy_ch0 = "clk_osc_ddrphy_ch0"

clk_core_b0 = "clk_core_b0"
clk_core_b0_clean = "clk_core_b0_clean"
clk_core_b0_uc = "clk_core_b0_uc"
clk_core_b1 = "clk_core_b1"
clk_core_b1_clean = "clk_core_b1_clean"
clk_core_b1_uc = "clk_core_b1_uc"
clk_testout_b0 = "clk_testout_b0"
refclk_bigcore0_pvtpll = "refclk_bigcore0_pvtpll"
clk_bigcore0_pvtm = "clk_bigcore0_pvtm"
clk_core_bigcore0_pvtm = "clk_core_bigcore0_pvtm"
pclk_bigcore0_root = "pclk_bigcore0_root"
pclk_bigcore0_biu = "pclk_bigcore0_biu"
pclk_bigcore0_pvtm = "pclk_bigcore0_pvtm"
pclk_bigcore0_grf = "pclk_bigcore0_grf"
pclk_bigcore0_cru = "pclk_bigcore0_cru"
pclk_bigcore0_cpuboost = "pclk_bigcore0_cpuboost"
clk_24m_bigcore0_cpuboost = "clk_24m_bigcore0_cpuboost"

clk_core_b2 = "clk_core_b2"
clk_core_b2_clean = "clk_core_b2_clean"
clk_core_b2_uc = "clk_core_b2_uc"
clk_core_b3 = "clk_core_b3"
clk_core_b3_clean = "clk_core_b3_clean"
clk_core_b3_uc = "clk_core_b3_uc"
clk_testout_b1 = "clk_testout_b1"
refclk_bigcore1_pvtpll = "refclk_bigcore1_pvtpll"
clk_bigcore1_pvtm = "clk_bigcore1_pvtm"
clk_core_bigcore1_pvtm = "clk_core_bigcore1_pvtm"
pclk_bigcore1_root = "pclk_bigcore1_root"
pclk_bigcore1_biu = "pclk_bigcore1_biu"
pclk_bigcore1_pvtm = "pclk_bigcore1_pvtm"
pclk_bigcore1_grf = "pclk_bigcore1_grf"
pclk_bigcore1_cru = "pclk_bigcore1_cru"
pclk_bigcore1_cpuboost = "pclk_bigcore1_cpuboost"
clk_24m_bigcore1_cpuboost = "clk_24m_bigcore1_cpuboost"

clk_uart8 = "clk_uart8"
clk_uart8_frac = "clk_uart8_frac"
sclk_uart8 = "sclk_uart8"
clk_uart9 = "clk_uart9"
clk_uart9_frac = "clk_uart9_frac"
sclk_uart9 = "sclk_uart9"
pclk_spi0 = "pclk_spi0"
pclk_spi1 = "pclk_spi1"
pclk_spi2 = "pclk_spi2"
pclk_spi3 = "pclk_spi3"
pclk_spi4 = "pclk_spi4"
clk_spi0 = "clk_spi0"
clk_spi1 = "clk_spi1"
clk_spi2 = "clk_spi2"
clk_spi3 = "clk_spi3"
clk_spi4 = "clk_spi4"


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


class MuxDivClk(VirtualDatapoint):
    def __init__(self, name, select, div=None, **datapoints):
        VirtualDatapoint.__init__(self, name, unit=common.MHZ)
        self.select = select
        self.datapoints = datapoints
        self.div = div

    def get(self):
        clk = 0
        nodiv = False
        self.select.reg.read()
        if self.datapoints:
            # pvtplls dont get divided
            if self.select.value == PVTPLL:
                nodiv = True
            clkdp = self.datapoints[self.select.value]
            if isinstance(clkdp, int):
                # fixed frequency
                clk = int(clkdp)
            else:
                # read frequency from datapoint
                clkdp.reg.read()
                clk = clkdp.int
        else:
            clk = self.select.int
        if self.div and not nodiv:
            self.div.reg.read()
            clk /= self.div.int + 1
        return int(clk)


class FracPLL(VirtualDatapoint):
    def __init__(self, con0, con1, con2, basef=24, factor=1, name=common.PLLCLOCKNAME):
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
        if p == 0:
            return 0
        return int(((m + k / 65536) * self.basef * self.factor) / (p * (2 ** s)))

    def set(self, value):
        pass


class IntPLL(VirtualDatapoint):
    def __init__(self, con0, con1, basef=24, name=common.PLLCLOCKNAME):
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
        self.clkgates()

    def clkgates(self):
        clks = [clk_uart8, clk_uart8_frac, sclk_uart8, clk_uart9, clk_uart9_frac, sclk_uart9,
                pclk_spi0, pclk_spi1, pclk_spi2, pclk_spi3, pclk_spi4, clk_spi0, clk_spi1,
                clk_spi2, clk_spi3, clk_spi4]
        reg = self.clkgate(0x838, *clks)
        self.block(reg)

    def regfromoffset(self, offset, base=0x300, prefix="CLKSEL_"):
        regnum = int((offset - base) / 4)
        regname = f"{prefix}{regnum}"
        reg = RK_Reg32_16bitMasked(regname, offset)
        self.block(reg)
        return reg

    def clksel_mux_snacg_pll_pvt(self, offset, name):
        CLKSEL_REG = self.regfromoffset(offset)
        CLKSEL_REG.register(0, 5, Datapoint(f"mux_div", default=0, validity=Validator(0, 2 ** 5 - 1)))
        CLKSEL_REG.register(5, 3, Datapoint(f"mux_pll", default=0, validity=Validator(0, 7, GPLL, CPLL, AUPLL, NPLL, SPLL)))
        CLKSEL_REG.register(None, None, MuxDivClk(f"mux_{common.PLLCLOCKNAME}",
                                                  select=CLKSEL_REG.get(f"mux_pll"),
                                                  div=CLKSEL_REG.get(f"mux_div"),
                                                  GPLL=self.reg_gpll.get(common.PLLCLOCKNAME),
                                                  CPLL=self.reg_cpll.get(common.PLLCLOCKNAME),
                                                  AUPLL=self.reg_aupll.get(common.PLLCLOCKNAME),
                                                  NPLL=self.reg_npll.get(common.PLLCLOCKNAME),
                                                  SPLL=None))
        CLKSEL_REG.register(8, 5, Datapoint(f"test_div", default=0, validity=Validator(0, 2 ** 5 - 1)))
        CLKSEL_REG.register(13, 1, Datapoint(f"test_sel", default=0, validity=Validator(0, 1, MUX, PVTPLL)))
        test_mux_dp = MuxDivClk(f"mux_{common.PLLCLOCKNAME}",
                                select=CLKSEL_REG.get(f"mux_pll"),
                                GPLL=self.reg_gpll.get(common.PLLCLOCKNAME),
                                CPLL=self.reg_cpll.get(common.PLLCLOCKNAME),
                                AUPLL=self.reg_aupll.get(common.PLLCLOCKNAME),
                                NPLL=self.reg_npll.get(common.PLLCLOCKNAME),
                                SPLL=None)
        test_mux_dp.reg = CLKSEL_REG
        CLKSEL_REG.register(None, None, MuxDivClk(f"test_{common.PLLCLOCKNAME}",
                                                  select=CLKSEL_REG.get(f"test_sel"),
                                                  div=CLKSEL_REG.get(f"test_div"),
                                                  MUX=test_mux_dp,
                                                  PVTPLL=GRF_GPU().getblock("PVTPLL_STATUS1").get(common.PVTCLOCKNAME)
                                                  ))
        CLKSEL_REG.register(14, 1, Datapoint(f"{name}_sel", default=0, validity=Validator(0, 1, MUX, PVTPLL)))
        CLKSEL_REG.register(None, None, MuxDivClk(f"{name}_{common.PLLCLOCKNAME}",
                                                  select=CLKSEL_REG.get(f"{name}_sel"),
                                                  div=None,
                                                  MUX=CLKSEL_REG.get(f"mux_{common.PLLCLOCKNAME}"),
                                                  PVTPLL=GRF_GPU().getblock("PVTPLL_STATUS1").get(common.PVTCLOCKNAME)
                                                  ))
        return CLKSEL_REG

    def clksel_mux3_div(self, offset, name1, name2, name3, selectdp=None):
        regs = []
        reg = self.regfromoffset(offset)
        for i, name in enumerate([name1, name2, name3]):
            reg.register(0 + i * 5, 5, Datapoint(f"{name}_div", default=0, validity=Validator(0, 2 ** 5 - 1)))
            if selectdp:
                reg.register(None, None, MuxDivClk(name=f"{name}_{common.PLLCLOCKNAME}",
                                                   select=selectdp,
                                                   div=reg.get(f"{name}_div")))
            regs.append(reg)
        return regs

    def gpu(self):
        gname = "GPU"
        basereg = self.clksel_mux_snacg_pll_pvt(0x578, clk_gpu_src)
        self.addgroup(gname, basereg.name)
        for reg in self.clksel_mux3_div(0x57C, clk_gpu_stacks, aclk_s_gpu_biu, aclk_m0_gpu_biu,
                                        basereg.get(f"mux_{common.PLLCLOCKNAME}")):
            self.addgroup(gname, reg.name)
        for reg in self.clksel_mux3_div(0x580, aclk_m1_gpu_biu, aclk_m2_gpu_biu, aclk_m3_gpu_biu,
                                        basereg.get(f"mux_{common.PLLCLOCKNAME}")):
            self.addgroup(gname, reg.name)
        reg = self.regfromoffset(0x584)
        reg.register(0, 2, Datapoint(f"{pclk_gpu_root}_sel", default=0,
                                     validity=Validator(0, 2 ** 2 - 1, F100M, F50M, XIN)))
        reg.register(None, None, MuxDivClk(f"{pclk_gpu_root}_{common.PLLCLOCKNAME}",
                                           select=reg.get(f"{pclk_gpu_root}_sel"),
                                           div=None,
                                           F100M=CLOCK_F100M,
                                           F50M=CLOCK_F50M,
                                           XIN=CLOCK_XIN
                                           ))

        reg.register(2, 1, Datapoint(f"{clk_gpu_pvtpll}_sel", default=0,
                                     validity=Validator(0, 1, MUX, XIN)))
        reg.register(None, None, MuxDivClk(f"{clk_gpu_pvtpll}_{common.PLLCLOCKNAME}",
                                           select=reg.get(f"{clk_gpu_pvtpll}_sel"),
                                           div=None,
                                           MUX=basereg.get(f"mux_{common.PLLCLOCKNAME}"),
                                           XIN=CLOCK_XIN
                                           ))
        self.block(reg)
        self.addgroup(gname, reg.name)
        GRF_GPU().pvtpll_clkin = reg.get(f"{clk_gpu_pvtpll}_{common.PLLCLOCKNAME}")

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


class CRU_SBUS(CRU):
    devname = "CRU_SBUS"
    start = 0xFD7D8000

    def __init__(self, start=None):
        start = start or self.start
        Device.__init__(self, self.devname, start)

        self.reg_spll = self.intpll_con(0x220, SPLL)


class CRU_DDR0(CRU):
    devname = "CRU_DDR0"
    start = 0xFD800000

    def __init__(self, start=None):
        start = start or self.start
        Device.__init__(self, self.devname, start=start)

        self.reg_apll = self.fracpll_con(0x0, APLL)
        self.reg_bpll = self.fracpll_con(0x20, BPLL)

        gname = "DDR"
        ddr_clocks = [None, None, None, pclk_ddr_cru_ch0, pclk_ddrphy_ch0, clk_osc_ddrphy_ch0]

        reg = self.clkgate(0x800, *ddr_clocks)
        self.block(reg)
        self.addgroup(gname, reg.name)


class CRU_DDR1(CRU_DDR0):
    devname = "CRU_DDR1"
    start = 0xFD804000


class CRU_DDR2(CRU_DDR0):
    devname = "CRU_DDR2"
    start = 0xFD808000


class CRU_DDR3(CRU_DDR0):
    devname = "CRU_DDR3"
    start = 0xFD80C000


class CRU_BIGCORE0(CRU):
    devname = "CRU_BIGCORE0"
    start = 0xFD810000
    clocks = [None, MUX, clk_core_b0_clean, clk_core_b0_uc, None, None, clk_core_b1_clean,
              clk_core_b1_uc, None, None, clk_testout_b0, refclk_bigcore0_pvtpll, clk_bigcore0_pvtm,
              clk_core_bigcore0_pvtm, pclk_bigcore0_root, pclk_bigcore0_biu, pclk_bigcore0_pvtm,
              pclk_bigcore0_grf, pclk_bigcore0_cru, pclk_bigcore0_cpuboost, clk_24m_bigcore0_cpuboost]
    grf_clkin = GRF_BIGCORE0().pvtpll_clkin
    pllname = B0PLL

    def __init__(self, start=None):
        start = start or self.start
        Device.__init__(self, self.devname, start=start)

        self.reg_b0pll = self.intpll_con(0x0, self.pllname)
        gname = "BIGCORE0"

        crublock = CRU()
        con0 = RK_Reg32_16bitMasked("CLKSEL_CON0", 0x300)
        con0.register(0, 1, datapoint=Datapoint(f"mux_slow_sel", validity=Validator(0, 1, FDEEP, XIN)))
        con0.register(None, None, MuxDivClk(f"mux_slow_{common.PLLCLOCKNAME}",
                                            select=con0.get(f"mux_slow_sel"),
                                            FDEEP=CLOCK_FDEEP,
                                            XIN=CLOCK_XIN))
        con0.register(1, 5, datapoint=Datapoint(f"mux_gpll_div", validity=Validator(0, 2 ** 5 - 1)))
        con0.register(None, None, MuxDivClk(f"mux_gpll_{common.PLLCLOCKNAME}",
                                            select=crublock.reg_gpll.get(common.PLLCLOCKNAME),
                                            div=con0.get(f"mux_gpll_div")))
        con0.register(6, 2, datapoint=Datapoint(f"mux_sel", validity=Validator(0, 2,
                                                                               f"SLOW",
                                                                               GPLL,
                                                                               self.pllname)))
        kwargs = {"SLOW": con0.get(f"mux_slow_{common.PLLCLOCKNAME}"),
                  GPLL: con0.get(f"mux_gpll_{common.PLLCLOCKNAME}"),
                  self.pllname: self.reg_b0pll.get(common.PLLCLOCKNAME)
                  }
        con0.register(None, None, MuxDivClk(f"mux_{common.PLLCLOCKNAME}",
                                            select=con0.get(f"mux_sel"),
                                            **kwargs
                                            ))

        con0.register(8, 5, datapoint=Datapoint(f"{clk_core_b0_uc}_div", validity=Validator(0, 2 ** 5 - 1)))
        con0.register(None, None, MuxDivClk(f"{clk_core_b0_uc}_{common.PLLCLOCKNAME}",
                                            select=con0.get(f"mux_{common.PLLCLOCKNAME}"),
                                            div=con0.get(f"{clk_core_b0_uc}_div")))

        con0.register(13, 2, datapoint=Datapoint(f"{clk_core_b0}_sel", validity=Validator(0, 2,
                                                                                          "UC",
                                                                                          "CLEAN",
                                                                                          PVTPLL)))
        con0.register(None, None, MuxDivClk(f"{clk_core_b0}_{common.PLLCLOCKNAME}",
                                            select=con0.get(f"{clk_core_b0}_sel"),
                                            UC=con0.get(f"{clk_core_b0_uc}_{common.PLLCLOCKNAME}"),
                                            CLEAN=None,
                                            PVTPLL=GRF_BIGCORE0().getblock("PVTPLL_STATUS1").get(common.PVTCLOCKNAME)))
        self.block(con0)
        self.addgroup(gname, "CLKSEL_CON0")

        con1 = RK_Reg32_16bitMasked("CLKSEL_CON1", 0x304)
        con1.register(0, 5, datapoint=Datapoint(f"{clk_core_b1_uc}_div", validity=Validator(0, 2 ** 5 - 1)))
        con1.register(None, None, MuxDivClk(f"{clk_core_b1_uc}_{common.PLLCLOCKNAME}",
                                            select=con0.get(f"mux_{common.PLLCLOCKNAME}"),
                                            div=con1.get(f"{clk_core_b1_uc}_div")))
        con1.register(5, 2, datapoint=Datapoint(f"{clk_core_b1}_sel", validity=Validator(0, 2,
                                                                                         "UC",
                                                                                         "CLEAN",
                                                                                         PVTPLL)))
        con1.register(None, None, MuxDivClk(f"{clk_core_b1}_{common.PLLCLOCKNAME}",
                                            select=con1.get(f"{clk_core_b1}_sel"),
                                            UC=con1.get(f"{clk_core_b1_uc}_{common.PLLCLOCKNAME}"),
                                            CLEAN=None,
                                            PVTPLL=GRF_BIGCORE0().getblock("PVTPLL_STATUS1").get(common.PVTCLOCKNAME)))
        con1.register(7, 6, datapoint=Datapoint(f"test_div", validity=Validator(0, 2 ** 5 - 1)))
        con1.register(13, 1, datapoint=Datapoint(f"test_sel", validity=Validator(0, 1, self.pllname, PVTPLL)))
        kwargs = {self.pllname: self.reg_b0pll.get(common.PLLCLOCKNAME),
                  PVTPLL: GRF_BIGCORE0().getblock("PVTPLL_STATUS1").get(common.PVTCLOCKNAME)}
        con1.register(None, None, MuxDivClk(f"test_{common.PLLCLOCKNAME}",
                                            select=con1.get(f"test_sel"),
                                            div=con1.get(f"test_div"),
                                            **kwargs))
        con1.register(14, 1, Datapoint(f"{refclk_bigcore0_pvtpll}_sel", default=0,
                                       validity=Validator(0, 1, MUX, XIN)))
        con1.register(None, None, MuxDivClk(f"{refclk_bigcore0_pvtpll}_{common.PLLCLOCKNAME}",
                                            select=con1.get(f"{refclk_bigcore0_pvtpll}_sel"),
                                            div=None,
                                            MUX=con0.get(f"mux_{common.PLLCLOCKNAME}"),
                                            XIN=CLOCK_XIN
                                            ))
        self.grf_clkin = con1.get(f"{refclk_bigcore0_pvtpll}_{common.PLLCLOCKNAME}")
        self.block(con1)
        self.addgroup(gname, "CLKSEL_CON1")

        offset = 0x800
        for clknames in common.iterlistchunks(self.clocks, 16):
            reg = self.clkgate(offset, *clknames)
            self.block(reg)
            self.addgroup(gname, reg.name)
            offset += 4


class CRU_BIGCORE1(CRU_BIGCORE0):
    devname = "CRU_BIGCORE1"
    start = 0xFD812000
    clocks = [None, MUX, clk_core_b2_clean, clk_core_b2_uc, None, None, clk_core_b3_clean,
              clk_core_b3_uc, None, None, clk_testout_b1, refclk_bigcore1_pvtpll, clk_bigcore1_pvtm,
              clk_core_bigcore1_pvtm, pclk_bigcore1_root, pclk_bigcore1_biu, pclk_bigcore1_pvtm,
              pclk_bigcore1_grf, pclk_bigcore1_cru, pclk_bigcore1_cpuboost, clk_24m_bigcore1_cpuboost]
    grf_clkin = GRF_BIGCORE1().pvtpll_clkin
    pllname = B1PLL
