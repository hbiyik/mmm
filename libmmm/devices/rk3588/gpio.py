'''
Created on Mar 19, 2023

@author: boogie
'''
from libmmm.model import Device, Reg32, Datapoint, Validator
from libmmm.devices.rockchip import RK_Reg32_16bitMasked

class GPIO:
    devname = ""
    start = 0
    
    def interleave16bits(self, addr, *REGS):
        for REG, VALIDATOR in REGS:
                for col in ["A", "B", "C", "D"]:
                    if col in ["A", "C"]:
                        suffix = "_L" if col == "A" else "_H"
                        reg = RK_Reg32_16bitMasked(REG + suffix, addr)
                        self.block(reg)
                        addr += 4
                        gpio = 0
                    for row in range(8):
                        reg.register(gpio + row, 1, Datapoint("%s%s" % (col, row), validity=VALIDATOR, default=0))
                    gpio += 8
                    
    def bits32(self, addr, *REGS):
        for REG in REGS:
            reg = Reg32(REG, addr)
            self.block(reg)
            gpio = 0
            for col in ["A", "B", "C", "D"]:
                for row in range(8):
                    reg.register(gpio, 1, Datapoint("%s%s" % (col, row), default=0, validity=Validator(0, 1)))
                    gpio += 1
            addr +=8
   
    def __init__(self, start=None):
        start = start or self.start
        super(GPIO, self).__init__(self.devname, start)
        
        self.interleave16bits(0x0, ("DATA", Validator(0, 1)),
                              ("DIRECTION", Validator(0, 1, "INPUT", "OUTPUT")),
                              ("INT_ENANBLE", Validator(0, 1)),
                              ("INT_MASK", Validator(0, 1)),
                              ("INT_TYPE", Validator(0, 1, "LEVEL", "EDGE")),
                              ("INT_POLARITY", Validator(0, 1, "ACTIVE_LOW", "ACTIVE_HIGH")),
                              ("INT_BOTHEDGE", Validator(0, 1)),
                              ("DEBOUNCE", Validator(0, 1)),
                              ("DBCLK_DIV_EN", Validator(0, 1)))
        
        reg = Reg32("DBCLK_DIV_CON", 0x48)
        self.block(reg)
        reg.register(0, 24, Datapoint("VALUE", default=1, validity=Validator(0, 2**24)))
        reg.register(24, 8, Datapoint("reserved", default=0, validity=Validator(0, 2**8)))
        
        self.bits32(0x50, "INT_STATUS", "INT_RAW_STATUS")
        self.interleave16bits(0x60, ("PORT_EOI", Validator(0, 1, "NOTHING", "CLEAREDGEINT")))
        self.bits32(0x70, "EXT_PORT")
        
        reg = Reg32("VERSION", 0x78)
        self.block(reg)
        reg.register(0, 32, Datapoint("ID", default=0x101157c, validity=Validator(0, 2**32)))
        
        self.interleave16bits(0x100, ("REG_REGORUP", None))
        
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