'''
Created on Mar 19, 2023

@author: boogie
'''
from libmmm.model import Device, Reg32, Datapoint, Validator
from libmmm.devices.rockchip import RK_Reg32_16bitMasked


class BIGCORE_GRF(Device):
    devname = ""
    start = 0

    def grfcommon(self):
        PVTPLL_CON0_L = RK_Reg32_16bitMasked("PVTPLL_CON0_L", 0x0)
        PVTPLL_CON0_H = RK_Reg32_16bitMasked("PVTPLL_CON0_H", 0x4)
        PVTPLL_CON1 = Reg32("PVTPLL_CON1", 0x8)
        PVTPLL_CON2 = Reg32("PVTPLL_CON2", 0xC)
        PVTPLL_CON3 = Reg32("PVTPLL_CON3", 0x10)
        PVTPLL_STATUS0 = Reg32("PVTPLL_STATUS0", 0x14)
        PVTPLL_STATUS1 = Reg32("PVTPLL_STATUS1", 0x18)

        self.block(PVTPLL_CON0_L)
        PVTPLL_CON0_L.register(0, 1, Datapoint("START", default=0, validity=Validator(0, 1)))
        PVTPLL_CON0_L.register(1, 1, Datapoint("OSC_EN", default=0, validity=Validator(0, 1)))
        PVTPLL_CON0_L.register(2, 1, Datapoint("OUT_POLAR", default=0, validity=Validator(0, 1, "ACTIVE_LOW", "ACTIVE_HIGH")))
        PVTPLL_CON0_L.register(3, 5, Datapoint("reserved", default=0, validity=Validator(0, 1)))
        PVTPLL_CON0_L.register(8, 3, Datapoint("OSC_RING_SEL", default=0, validity=Validator(0, 2 ** 3 - 1)))
        PVTPLL_CON0_L.register(11, 2, Datapoint("CLK_DIV_REF", default=0, validity=Validator(0, 2 ** 2 - 1)))
        PVTPLL_CON0_L.register(13, 2, Datapoint("CLK_DIV_OSC", default=0, validity=Validator(0, 2 ** 2 - 1)))
        PVTPLL_CON0_L.register(15, 1, Datapoint("BYPASS", default=0, validity=Validator(0, 1)))

        self.block(PVTPLL_CON0_H)
        PVTPLL_CON0_H.register(0, 6, Datapoint("RING_LENGTH_SEL", default=0, validity=Validator(0, 2 ** 6 - 1)))
        PVTPLL_CON0_H.register(6, 10, Datapoint("reserved", default=0, validity=Validator(0, 2 ** 10 - 1)))

        self.block(PVTPLL_CON1)
        PVTPLL_CON1.register(0, 32, Datapoint("CAL_CNT", default=0x18, validity=Validator(0, 2 ** 32 - 1)))

        self.block(PVTPLL_CON2)
        PVTPLL_CON2.register(0, 16, Datapoint("THRESHOLD", default=0x0, validity=Validator(0, 2 ** 16 - 1)))
        PVTPLL_CON2.register(16, 16, Datapoint("CKG_VAL", default=0x4, validity=Validator(0, 2 ** 16 - 1)))

        self.block(PVTPLL_CON3)
        PVTPLL_CON3.register(0, 32, Datapoint("REF_CNT", default=0x18, validity=Validator(0, 2 ** 32 - 1)))

        self.block(PVTPLL_STATUS0)
        PVTPLL_STATUS0.register(0, 32, Datapoint("OSC_CNT", default=0x0, validity=Validator(0, 2 ** 32 - 1)))
        PVTPLL_STATUS0.allowwrite = False
        self.block(PVTPLL_STATUS1)
        PVTPLL_STATUS1.register(0, 32, Datapoint("OSC_CNT_AVG", default=0x0, validity=Validator(0, 2 ** 32 - 1)))
        PVTPLL_STATUS1.allowwrite = False

        self.addgroup("PVTPLL_CON", "PVTPLL_CON0_L")
        self.addgroup("PVTPLL_CON", "PVTPLL_CON0_H")
        self.addgroup("PVTPLL_CON", "PVTPLL_CON1")
        self.addgroup("PVTPLL_CON", "PVTPLL_CON2")
        self.addgroup("PVTPLL_CON", "PVTPLL_CON3")
        self.addgroup("PVTPLL_STATUS", "PVTPLL_STATUS0")
        self.addgroup("PVTPLL_STATUS", "PVTPLL_STATUS1")

    def memcfg1(self, name, offset):
        MEM_CFG = RK_Reg32_16bitMasked(name, offset)
        self.block(MEM_CFG)
        MEM_CFG.register(0, 1, Datapoint("TEST1", default=0x0, validity=Validator(0, 1)))
        MEM_CFG.register(1, 1, Datapoint("TEST_RNM", default=0x0, validity=Validator(0, 1)))
        MEM_CFG.register(2, 3, Datapoint("RM", default=0x2, validity=Validator(0, 8)))
        MEM_CFG.register(5, 1, Datapoint("WMD", default=0x0, validity=Validator(0, 1)))
        MEM_CFG.register(6, 1, Datapoint("reserved", default=0x0, validity=Validator(0, 1)))
        MEM_CFG.register(7, 1, Datapoint("LS", default=0x0, validity=Validator(0, 1)))
        MEM_CFG.register(8, 4, Datapoint("reserved", default=0x0, validity=Validator(0, 16)))
        MEM_CFG.register(12, 2, Datapoint("RA", default=0x0, validity=Validator(0, 4)))
        MEM_CFG.register(14, 2, Datapoint("reserved", default=0x2, validity=Validator(0, 4)))
        self.addgroup("MEMCFG", name)

    def memcfg2(self, name, offset):
        MEM_CFG = RK_Reg32_16bitMasked(name, offset)

        self.block(MEM_CFG)
        MEM_CFG.register(0, 1, Datapoint("reserved", default=0x0, validity=Validator(0, 1)))
        MEM_CFG.register(1, 1, Datapoint("TEST1B", default=0x0, validity=Validator(0, 1)))
        MEM_CFG.register(2, 4, Datapoint("RMB", default=0x3, validity=Validator(0, 16)))
        MEM_CFG.register(6, 9, Datapoint("reserved", default=0x0, validity=Validator(0, 2**9)))
        self.addgroup("MEMCFG", name)

    def memcfg3(self, name, offset):
        MEM_CFG = RK_Reg32_16bitMasked(name, offset)

        self.block(MEM_CFG)
        MEM_CFG.register(0, 1, Datapoint("TEST1", default=0x0, validity=Validator(0, 1)))
        MEM_CFG.register(1, 1, Datapoint("TEST_RNM", default=0x0, validity=Validator(0, 1)))
        MEM_CFG.register(2, 3, Datapoint("RM", default=0x2, validity=Validator(0, 8)))
        MEM_CFG.register(5, 1, Datapoint("WMD", default=0x0, validity=Validator(0, 1)))
        MEM_CFG.register(6, 1, Datapoint("reserved", default=0x0, validity=Validator(0, 1)))
        MEM_CFG.register(7, 1, Datapoint("LS", default=0x0, validity=Validator(0, 1)))
        self.addgroup("MEMCFG", name)

    def bigcore_cfg(self):
        self.memcfg1("MEM_CFG_HSSPRF_L", 0x20)
        self.memcfg1("MEM_CFG_HDSPRF_L", 0x28)
        self.memcfg2("MEM_CFG_HDSPRF_H", 0x2c)

        CPU_CON0 = RK_Reg32_16bitMasked("CPU_CON0", 0x30)
        self.block(CPU_CON0)
        for i in range(4):
            CPU_CON0.register(0 + i, 1, Datapoint("CORE%d_MEM_CTRL_FROM_PMU" % i, default=0, validity=Validator(0, 1)))
        CPU_CON0.register(4, 1, Datapoint("MEM_CFG_IDLE_EN", default=0, validity=Validator(0, 1)))
        CPU_CON0.register(5, 1, Datapoint("MEM_CFG_IDLE_TRIG", default=0, validity=Validator(0, 1)))
        CPU_CON0.register(6, 10, Datapoint("reserved", default=0, validity=Validator(0, 2**10)))

    def gpu_conf(self):
        self.memcfg1("MEMCFG0", 0x24)
        self.memcfg1("MEMCFG1", 0x28)

        CON1 = RK_Reg32_16bitMasked("CON1", 0x40)
        self.block(CON1)
        CON1.register(0, 4, Datapoint("stripping_granule", default=0, validity=Validator(0, 2 ** 4 - 1)))
        CON1.register(4, 1, Datapoint("ckg_en", default=0, validity=Validator(0, 1)))
        CON1.register(5, 1, Datapoint("halted_en", default=0, validity=Validator(0, 1)))
        CON1.register(6, 1, Datapoint("protmode_en", default=0, validity=Validator(0, 1)))

        STATUS = RK_Reg32_16bitMasked("STATUS", 0x44)
        self.block(STATUS)
        STATUS.register(0, 1, Datapoint("dormantstate", default=0, validity=Validator(0, 1)))
        STATUS.register(1, 1, Datapoint("swactive", default=0, validity=Validator(0, 1)))

    def __init__(self, start=None):
        start = start or self.start
        super(BIGCORE_GRF, self).__init__(self.devname, start)
        self.grfcommon()

        if self.name.startswith("BIGCORE"):
            self.bigcore_cfg()

        if self.name.startswith("GPU"):
            self.gpu_conf()


class BIGCORE0_GRF(BIGCORE_GRF):
    devname = "BIGCORE0_GRF"
    start = 0xFD590000


class BIGCORE1_GRF(BIGCORE_GRF):
    devname = "BIGCORE1_GRF"
    start = 0xFD592000


class GPU_GRF(BIGCORE_GRF):
    devname = "GPU_GRF"
    start = 0xFD5A0000
