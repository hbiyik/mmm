from libmmm.model import Device, Reg32, Datapoint


class PVTM:
    devname = ""
    start = 0
    def __init__(self, start=None):
        start = start or self.start
        super(PVTM, self).__init__(self.devname, start)
        
        VERSION_REG = Reg32("VERSION", 0x0)
        self.block(VERSION_REG)
        VERSION_REG.register(0, 16, Datapoint("reserved", default=0))
        VERSION_REG.register(16, 16, Datapoint("VERSION", default=0x203))
        
        CON0_REG = Reg32("CON0", 0x4)
        self.block(CON0_REG)
        CON0_REG.register(0, 1, Datapoint("START", default=0))
        CON0_REG.register(1, 1, Datapoint("OSC_EN", default=0))
        CON0_REG.register(2, 3, Datapoint("OSC_SEL", default=0))
        CON0_REG.register(5, 1, Datapoint("SEED_EN", default=0))
        CON0_REG.register(6, 10, Datapoint("reserved", default=0))
        for i in range(16):
            CON0_REG.register(16 + i, 1, Datapoint("WRITE_EN_%d" % i, default=0))
        
        CON1_REG = Reg32("CON1", 0x8)
        self.block(CON1_REG)
        CON1_REG.register(0, 32, Datapoint("CAL_CNT", default=0))

        CON2_REG = Reg32("CON2", 0xC)
        self.block(CON2_REG)
        CON2_REG.register(0, 1, Datapoint("START_AUTO", default=0))
        CON2_REG.register(1, 1, Datapoint("OSC_EN_AUTO", default=0))
        CON2_REG.register(2, 3, Datapoint("OSC_SEL_AUTO", default=0))
        CON2_REG.register(5, 1, Datapoint("START_AUTO_MODE", default=0))
        CON2_REG.register(6, 1, Datapoint("AVR_UPDATE_MODE", default=0))
        CON2_REG.register(7, 1, Datapoint("AVR_CAL_MODE", default=0))
        CON2_REG.register(8, 8, Datapoint("OSC_RING_AUTOSEL_EN", default=0))
        for i in range(16):
            CON2_REG.register(16 + i, 1, Datapoint("WRITE_EN_%d" % i, default=0))

        CON3_REG = Reg32("CON3", 0x10)
        self.block(CON3_REG)
        CON3_REG.register(0, 32, Datapoint("CAL_CNT_AUTO", default=0))

        CON4_REG = Reg32("CON4", 0x14)
        self.block(CON4_REG)
        CON4_REG.register(0, 16, Datapoint("CAL_PERIOD", default=0))
        CON4_REG.register(16, 16, Datapoint("AVR_PERIOD", default=0))
        
        CON5_REG = Reg32("CON5", 0x18)
        self.block(CON5_REG)
        CON5_REG.register(0, 32, Datapoint("MIN_TRESHOLD", default=0))

        CON6_REG = Reg32("CON6", 0x1c)
        self.block(CON6_REG)
        CON6_REG.register(0, 32, Datapoint("AVR_TRESHOLD", default=0))
        
        INT_EN_REG = Reg32("INT_EN", 0x70)
        self.block(INT_EN_REG)
        INT_EN_REG.register(0, 1, Datapoint("MIN_VALUE", default=0))
        INT_EN_REG.register(1, 1, Datapoint("AVR_VALUE", default=0))
        INT_EN_REG.register(2, 1, Datapoint("CAL_DONE", default=0))
        INT_EN_REG.register(3, 29, Datapoint("reserved", default=0))

        INT_EN_REG = Reg32("INT_STAT", 0x74)
        self.block(INT_EN_REG)
        INT_EN_REG.register(0, 1, Datapoint("MIN_VALUE", default=0))
        INT_EN_REG.register(1, 1, Datapoint("AVR_VALUE", default=0))
        INT_EN_REG.register(2, 1, Datapoint("CAL_DONE", default=0))
        INT_EN_REG.register(3, 29, Datapoint("reserved", default=0))

        STATUS0_REG = Reg32("STATUS0", 0x80)
        self.block(STATUS0_REG)
        STATUS0_REG.register(0, 1, Datapoint("FREQ_DONE", default=0))
        STATUS0_REG.register(1, 31, Datapoint("reserved", default=0))
        
        addr = 0x84
        for reg, val in [("STATUS1", "freq_cnt"),
                         ("STATUS2", "rnd_seed_low_bits"),
                         ("STATUS3", "rnd_seed_hi_bits"),
                         ("STATUS4", "min_value"),
                         ("STATUS5", "avr_value"),
                         ("STATUS6", "max_value")]:
            REG = Reg32(reg, addr)
            self.block(REG)
            REG.register(0, 32, Datapoint(val, default=0))
            addr += 4
            
        STATUS7_REG = Reg32("STATUS7", 0x9c)
        self.block(STATUS7_REG)
        STATUS7_REG.register(0, 16, Datapoint("CAL_CNT", default=0))
        STATUS7_REG.register(16, 16, Datapoint("AVR_CNT", default=0))


class GPIO:
    devname = ""
    start = 0
    
    def interleave16bits(self, addr, *REGS):
        for REG in REGS:
                for col in ["A", "B", "C", "D"]:
                    if col in ["A", "C"]:
                        suffix = "_L" if col == "A" else "_H"
                        reg = Reg32(REG + suffix, addr)
                        self.block(reg)
                        addr += 4
                        gpio = 0
                    for row in range(8):
                        reg.register(gpio + row, 1, Datapoint("%s%s" % (col, row), default=0))
                    for row in range(8):
                        reg.register(gpio + row + 16, 1, Datapoint("%s%s_MASK" % (col, row), default=0))
                    gpio += 8
                    
    def bits32(self, addr, *REGS):
        for REG in REGS:
            reg = Reg32(REG, addr)
            self.block(reg)
            gpio = 0
            for col in ["A", "B", "C", "D"]:
                for row in range(8):
                    reg.register(gpio, 1, Datapoint("%s%s" % (col, row), default=0))
                    gpio += 1
            addr +=8
   
    def __init__(self, start=None):
        start = start or self.start
        super(GPIO, self).__init__(self.devname, start)
        
        self.interleave16bits(0x0, "DATA", "DIRECTION", "INT_ENANBLE", "INT_MASK",
                                    "INT_TYPE", "INT_POLARITY", "INT_BOTHEDGE",
                                    "DEBOUNCE", "DBCLK_DIV_EN")
        
        reg = Reg32("DBCLK_DIV_CON", 0x48)
        self.block(reg)
        reg.register(0, 24, Datapoint("VALUE", default=1))
        reg.register(24, 8, Datapoint("reserved", default=0))
        
        self.bits32(0x50, "INT_STATUS", "INT_RAW_STATUS")
        self.interleave16bits(0x60, "PORT_EOI")
        self.bits32(0x70, "EXT_PORT")
        
        reg = Reg32("VERSION", 0x78)
        self.block(reg)
        reg.register(0, 32, Datapoint("ID", default=0x101157c))
        
        self.interleave16bits(0x100, "REG_REGORUP")
        
        reg = Reg32("VIRTUAL_EN", 0x108)
        self.block(reg)
        reg.register(0, 1, Datapoint("EN", default=0))
        reg.register(1, 15, Datapoint("reserved", default=0))
        gpio = 16
        for col in ["A", "B"]:
            for row in range(8):
                reg.register(gpio, 1, Datapoint("%s%s" % (col, row), default=0))
                gpio += 1

class BIGCORE_GRF:
    devname = ""
    start = 0
    def __init__(self, start=None):
        start = start or self.start
        super(BIGCORE_GRF, self).__init__(self.devname, start)
        
        PVTPLL_CON0_L = Reg32("PVTPLL_CON0_L", 0x0)
        PVTPLL_CON0_H = Reg32("PVTPLL_CON0_H", 0x4)
        PVTPLL_CON1 = Reg32("PVTPLL_CON1", 0x8)
        PVTPLL_CON2 = Reg32("PVTPLL_CON2", 0xC)
        PVTPLL_CON3 = Reg32("PVTPLL_CON3", 0x10)
        MEM_CFG_HSSPRF_L = Reg32("MEM_CFG_HSSPRF_L", 0x20)
        MEM_CFG_HSDPRF_L = Reg32("MEM_CFG_HDSPRF_L", 0x28)
        MEM_CFG_HSDPRF_H = Reg32("MEM_CFG_HDSPRF_H", 0x2c)
        CPU_CON0 = Reg32("CPU_CON0", 0x30)
        
        self.block(PVTPLL_CON0_L)
        PVTPLL_CON0_L.register(0, 1, Datapoint("START", default=0))
        PVTPLL_CON0_L.register(1, 1, Datapoint("OSC_EN", default=0))
        PVTPLL_CON0_L.register(2, 1, Datapoint("OUT_POLAR", default=0))
        PVTPLL_CON0_L.register(3, 5, Datapoint("reserved", default=0))
        PVTPLL_CON0_L.register(8, 3, Datapoint("OSC_RING_SEL", default=0))
        PVTPLL_CON0_L.register(11, 2, Datapoint("CLK_DIV_REF", default=0))
        PVTPLL_CON0_L.register(13, 2, Datapoint("CLK_DIV_OSC", default=0))
        PVTPLL_CON0_L.register(15, 1, Datapoint("BYPASS", default=0))
        for i in range(16):
            PVTPLL_CON0_L.register(16 + i, 1, Datapoint("WRITE_MASK_%d" % i, default=0))
            
        self.block(PVTPLL_CON0_H)
        PVTPLL_CON0_H.register(0, 6, Datapoint("RING_LENGTH_SEL", default=0))
        PVTPLL_CON0_H.register(6, 10, Datapoint("reserved", default=0))
        for i in range(16):
            PVTPLL_CON0_H.register(16 + i, 1, Datapoint("WRITE_MASK_%d" % i, default=0))
            
        self.block(PVTPLL_CON1)
        PVTPLL_CON1.register(0, 32, Datapoint("CAL_CNT", default=0x18))
        
        self.block(PVTPLL_CON2)
        PVTPLL_CON2.register(0, 16, Datapoint("THRESHOLD", default=0x0))
        PVTPLL_CON2.register(16, 16, Datapoint("CKG_CNT", default=0x4))
        
        self.block(PVTPLL_CON3)
        PVTPLL_CON3.register(0, 32, Datapoint("REF_CNT", default=0x18))
        
        self.block(MEM_CFG_HSSPRF_L)
        MEM_CFG_HSSPRF_L.register(0, 1, Datapoint("TEST1", default=0x0))
        MEM_CFG_HSSPRF_L.register(1, 1, Datapoint("TEST_RNM", default=0x0))
        MEM_CFG_HSSPRF_L.register(2, 3, Datapoint("RM", default=0x2))
        MEM_CFG_HSSPRF_L.register(5, 1, Datapoint("WMD", default=0x0))
        MEM_CFG_HSSPRF_L.register(6, 1, Datapoint("reserved", default=0x0))
        MEM_CFG_HSSPRF_L.register(7, 1, Datapoint("LS", default=0x0))
        MEM_CFG_HSSPRF_L.register(8, 4, Datapoint("reserved", default=0x0))
        MEM_CFG_HSSPRF_L.register(12, 2, Datapoint("RA", default=0x0))
        MEM_CFG_HSSPRF_L.register(14, 2, Datapoint("reserved", default=0x2))
        for i in range(16):
            MEM_CFG_HSSPRF_L.register(16 + i, 1, Datapoint("WRITE_MASK_%d" % i, default=0))

        self.block(MEM_CFG_HSDPRF_L)
        MEM_CFG_HSDPRF_L.register(0, 1, Datapoint("TEST1A", default=0x0))
        MEM_CFG_HSDPRF_L.register(1, 1, Datapoint("TEST_RNMA", default=0x0))
        MEM_CFG_HSDPRF_L.register(2, 4, Datapoint("RMA", default=0x1))
        MEM_CFG_HSDPRF_L.register(6, 1, Datapoint("WMDA", default=0x0))
        MEM_CFG_HSDPRF_L.register(8, 1, Datapoint("LS", default=0x0))
        MEM_CFG_HSDPRF_L.register(9, 4, Datapoint("reserved", default=0x0))
        MEM_CFG_HSDPRF_L.register(13, 2, Datapoint("RA", default=0x0))
        MEM_CFG_HSDPRF_L.register(15, 1, Datapoint("reserved", default=0x0))
        for i in range(16):
            MEM_CFG_HSDPRF_L.register(16 + i, 1, Datapoint("WRITE_MASK_%d" % i, default=0))
        
        self.block(MEM_CFG_HSDPRF_H)
        MEM_CFG_HSDPRF_H.register(0, 0, Datapoint("reserved", default=0x0))
        MEM_CFG_HSDPRF_H.register(1, 1, Datapoint("TEST1B", default=0x0))
        MEM_CFG_HSDPRF_H.register(2, 4, Datapoint("RMB", default=0x3))
        MEM_CFG_HSDPRF_H.register(6, 9, Datapoint("reserved", default=0x0))
        for i in range(16):
            MEM_CFG_HSDPRF_H.register(16 + i, 1, Datapoint("WRITE_MASK_%d" % i, default=0))
            
        self.block(CPU_CON0)
        for i in range(4):
            CPU_CON0.register(0 + i, 1, Datapoint("CORE%d_MEM_CTRL_FROM_PMU" % i, default=0))
        CPU_CON0.register(4, 1, Datapoint("MEM_CFG_IDLE_EN", default=0))
        CPU_CON0.register(5, 1, Datapoint("MEM_CFG_IDLE_TRIG", default=0))
        CPU_CON0.register(6, 10, Datapoint("reserved", default=0))
        for i in range(16):
            CPU_CON0.register(16 + i, 1, Datapoint("WRITE_MASK_%d" % i, default=0))

class GPIO0(GPIO, Device):
    devname = "GPIO0"
    start = 0xFD8A0000

class GPIO1(GPIO, Device):
    devname = "GPIO1"
    start = 0xFEC20000

class GPIO2(GPIO, Device):
    devname = "GPIO2"
    start = 0xFEC30000

class GPIO3(GPIO, Device):
    devname = "GPIO3"
    start = 0xFEC40000
    
class GPIO4(GPIO, Device):
    devname = "GPIO4"
    start = 0xFEC50000

#class PMU_PVTM(PVTM, Device):
#    devname = "PMU_PVTM"
#    start = 0xFD8C0000

class BIGCORE0_GRF(BIGCORE_GRF, Device):
    devname = "BIGCORE0_GRF"
    start = 0xFD590000

class BIGCORE1_GRF(BIGCORE_GRF, Device):
    devname = "BIGCORE1_GRF"
    start = 0xFD592000

class CORE_B0_PVTM(PVTM, Device):
    devname = "CORE_B0_PVTM"
    start = 0xFDA40000
   
#class CORE_B1_PVTM(PVTM, Device):
#    devname = "CORE_B1_PVTM"
#    start = 0xFDA50000
    
#class CORE_L_PVTM(PVTM, Device):
#    devname = "CORE_L_PVTM"
#    start = 0xFDA60000
    
#class CORE_NPU_PVTM(PVTM, Device):
#    devname = "CORE_NPU_PVTM"
#    start = 0xFDAF0000
    
#class CORE_GPU_PVTM(PVTM, Device):
#    devname = "CORE_GPU_PVTM"
#    start = 0xFDB30000