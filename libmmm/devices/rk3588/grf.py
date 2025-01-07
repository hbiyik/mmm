'''
Created on Mar 19, 2023

@author: boogie
'''
from libmmm.model import Device, Reg32, Datapoint, Validator
from libmmm.devices.rockchip import RK_Reg32_16bitMasked


class BIGCORE_GRF:
    devname = ""
    start = 0

    def __init__(self, start=None):
        start = start or self.start
        super(BIGCORE_GRF, self).__init__(self.devname, start)

        PVTPLL_CON0_L = RK_Reg32_16bitMasked("PVTPLL_CON0_L", 0x0)
        PVTPLL_CON0_H = RK_Reg32_16bitMasked("PVTPLL_CON0_H", 0x4)
        PVTPLL_CON1 = Reg32("PVTPLL_CON1", 0x8)
        PVTPLL_CON2 = Reg32("PVTPLL_CON2", 0xC)
        PVTPLL_CON3 = Reg32("PVTPLL_CON3", 0x10)
        MEM_CFG_HSSPRF_L = RK_Reg32_16bitMasked("MEM_CFG_HSSPRF_L", 0x20)
        MEM_CFG_HSDPRF_L = RK_Reg32_16bitMasked("MEM_CFG_HDSPRF_L", 0x28)
        MEM_CFG_HSDPRF_H = RK_Reg32_16bitMasked("MEM_CFG_HDSPRF_H", 0x2c)
        CPU_CON0 = RK_Reg32_16bitMasked("CPU_CON0", 0x30)

        self.block(PVTPLL_CON0_L)
        PVTPLL_CON0_L.register(0, 1, Datapoint("START", default=0, validity=Validator(0, 1)))
        PVTPLL_CON0_L.register(1, 1, Datapoint("OSC_EN", default=0, validity=Validator(0, 1)))
        PVTPLL_CON0_L.register(2, 1, Datapoint("OUT_POLAR", default=0, validity=Validator(0, 1, "ACTIVE_LOW", "ACTIVE_HIGH")))
        PVTPLL_CON0_L.register(3, 5, Datapoint("reserved", default=0, validity=Validator(0, 1)))
        PVTPLL_CON0_L.register(8, 3, Datapoint("OSC_RING_SEL", default=0, validity=Validator(0, 2**3)))
        PVTPLL_CON0_L.register(11, 2, Datapoint("CLK_DIV_REF", default=0, validity=Validator(0, 4)))
        PVTPLL_CON0_L.register(13, 2, Datapoint("CLK_DIV_OSC", default=0, validity=Validator(0, 4)))
        PVTPLL_CON0_L.register(15, 1, Datapoint("BYPASS", default=0, validity=Validator(0, 1)))

        self.block(PVTPLL_CON0_H)
        PVTPLL_CON0_H.register(0, 6, Datapoint("RING_LENGTH_SEL", default=0, validity=Validator(0, 2**6)))
        PVTPLL_CON0_H.register(6, 10, Datapoint("reserved", default=0, validity=Validator(0, 2**10)))

        self.block(PVTPLL_CON1)
        PVTPLL_CON1.register(0, 32, Datapoint("CAL_CNT", default=0x18, validity=Validator(0, 2**32)))

        self.block(PVTPLL_CON2)
        PVTPLL_CON2.register(0, 16, Datapoint("THRESHOLD", default=0x0, validity=Validator(0, 2**16)))
        PVTPLL_CON2.register(16, 16, Datapoint("CKG_CNT", default=0x4, validity=Validator(0, 2**16)))

        self.block(PVTPLL_CON3)
        PVTPLL_CON3.register(0, 32, Datapoint("REF_CNT", default=0x18, validity=Validator(0, 2**32)))

        self.block(MEM_CFG_HSSPRF_L)
        MEM_CFG_HSSPRF_L.register(0, 1, Datapoint("TEST1", default=0x0, validity=Validator(0, 1)))
        MEM_CFG_HSSPRF_L.register(1, 1, Datapoint("TEST_RNM", default=0x0, validity=Validator(0, 1)))
        MEM_CFG_HSSPRF_L.register(2, 3, Datapoint("RM", default=0x2, validity=Validator(0, 8)))
        MEM_CFG_HSSPRF_L.register(5, 1, Datapoint("WMD", default=0x0, validity=Validator(0, 1)))
        MEM_CFG_HSSPRF_L.register(6, 1, Datapoint("reserved", default=0x0, validity=Validator(0, 1)))
        MEM_CFG_HSSPRF_L.register(7, 1, Datapoint("LS", default=0x0, validity=Validator(0, 1)))
        MEM_CFG_HSSPRF_L.register(8, 4, Datapoint("reserved", default=0x0, validity=Validator(0, 16)))
        MEM_CFG_HSSPRF_L.register(12, 2, Datapoint("RA", default=0x0, validity=Validator(0, 4)))
        MEM_CFG_HSSPRF_L.register(14, 2, Datapoint("reserved", default=0x2, validity=Validator(0, 4)))

        self.block(MEM_CFG_HSDPRF_L)
        MEM_CFG_HSDPRF_L.register(0, 1, Datapoint("TEST1A", default=0x0, validity=Validator(0, 1)))
        MEM_CFG_HSDPRF_L.register(1, 1, Datapoint("TEST_RNMA", default=0x0, validity=Validator(0, 1)))
        MEM_CFG_HSDPRF_L.register(2, 4, Datapoint("RMA", default=0x1, validity=Validator(0, 16)))
        MEM_CFG_HSDPRF_L.register(6, 1, Datapoint("WMDA", default=0x0, validity=Validator(0, 1)))
        MEM_CFG_HSDPRF_L.register(8, 1, Datapoint("LS", default=0x0, validity=Validator(0, 1)))
        MEM_CFG_HSDPRF_L.register(9, 4, Datapoint("reserved", default=0x0, validity=Validator(0, 16)))
        MEM_CFG_HSDPRF_L.register(13, 2, Datapoint("RA", default=0x0, validity=Validator(0, 4)))
        MEM_CFG_HSDPRF_L.register(15, 1, Datapoint("reserved", default=0x0, validity=Validator(0, 1)))

        self.block(MEM_CFG_HSDPRF_H)
        MEM_CFG_HSDPRF_H.register(0, 1, Datapoint("reserved", default=0x0, validity=Validator(0, 1)))
        MEM_CFG_HSDPRF_H.register(1, 1, Datapoint("TEST1B", default=0x0, validity=Validator(0, 1)))
        MEM_CFG_HSDPRF_H.register(2, 4, Datapoint("RMB", default=0x3, validity=Validator(0, 16)))
        MEM_CFG_HSDPRF_H.register(6, 9, Datapoint("reserved", default=0x0, validity=Validator(0, 2**9)))

        self.block(CPU_CON0)
        for i in range(4):
            CPU_CON0.register(0 + i, 1, Datapoint("CORE%d_MEM_CTRL_FROM_PMU" % i, default=0, validity=Validator(0, 1)))
        CPU_CON0.register(4, 1, Datapoint("MEM_CFG_IDLE_EN", default=0, validity=Validator(0, 1)))
        CPU_CON0.register(5, 1, Datapoint("MEM_CFG_IDLE_TRIG", default=0, validity=Validator(0, 1)))
        CPU_CON0.register(6, 10, Datapoint("reserved", default=0, validity=Validator(0, 2**10)))


class BIGCORE0_GRF(BIGCORE_GRF, Device):
    devname = "BIGCORE0_GRF"
    start = 0xFD590000


class BIGCORE1_GRF(BIGCORE_GRF, Device):
    devname = "BIGCORE1_GRF"
    start = 0xFD592000
