from libmmm.model import Device, Reg32, Datapoint


class PVTM:
    suffix = ""
    start = 0
    def __init__(self, start=None):
        start = start or self.start
        super(PVTM, self).__init__(self.suffix + "_PVTM", start)
        
        VERSION_REG = Reg32("VERSION", 0x0000)
        self.block(VERSION_REG)
        VERSION_REG.register(0, 16, Datapoint("reserved", default=0))
        VERSION_REG.register(16, 16, Datapoint("VERSION", default=0x203))
        
        CON0_REG = Reg32("CON0", 0x0004)
        self.block(CON0_REG)
        CON0_REG.register(0, 1, Datapoint("START", default=0))
        CON0_REG.register(1, 1, Datapoint("OSC_EN", default=0))
        CON0_REG.register(2, 3, Datapoint("OSC_SEL", default=0))
        CON0_REG.register(5, 1, Datapoint("SEED_EN", default=0))
        CON0_REG.register(6, 10, Datapoint("reserved", default=0))
        CON0_REG.register(16, 16, Datapoint("WRITE_ENABLE", default=0))
            
class GPIO:
    suffix = ""
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
        super(GPIO, self).__init__("GPIO" + self.suffix, start)
        
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

class GPIO0(GPIO, Device):
    suffix = "0"
    start = 0xFD8A0000

class GPIO1(GPIO, Device):
    suffix = "1"
    start = 0xFEC20000

class GPIO2(GPIO, Device):
    suffix = "2"
    start = 0xFEC30000

class GPIO3(GPIO, Device):
    suffix = "3"
    start = 0xFEC40000
    
class GPIO4(GPIO, Device):
    suffix = "4"
    start = 0xFEC50000

#class PVTM_PMU(PVTM, Device):
#    suffix = "PMU"
#    start = 0xFD8C0000

class PVTM_CORE_B0(PVTM, Device):
    suffix = "CORE_B0"
    start = 0xFDA40000
   
#class PVTM_CORE_B1(PVTM, Device):
#    suffix = "CORE_B1"
#    start = 0xFDA50000
    
#class PVTM_CORE_L(PVTM, Device):
#    suffix = "CORE_L"
#    start = 0xFDA60000
    
#class PVTM_CORE_NPU(PVTM, Device):
#    suffix = "CORE_NPU"
#    start = 0xFDAF0000
    
#class PVTM_CORE_GPU(PVTM, Device):
#    suffix = "CORE_GPU"
#    start = 0xFDB30000