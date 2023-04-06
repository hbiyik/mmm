'''
Created on Apr 6, 2023

@author: z0042jww
'''
from libmmm.model import Device, Reg32, Datapoint, Validator

class DDRCTL:
    devname = ""
    start = 0
    def __init__(self, start=None):
        start = start or self.start
        super(DDRCTL, self).__init__(self.devname, start)
        
        TMG0 = Reg32("TMG0", 0x0)
        TMG0.register(0, 8, Datapoint("TRAS_MIN", default=0xf, validity=Validator(0, 2 ** 8)))
        TMG0.register(8, 8, Datapoint("TRAS_MAX", default=0x1b, validity=Validator(0, 2 ** 8)))
        TMG0.register(16, 8, Datapoint("TFAW", default=0x10, validity=Validator(0, 2 ** 8)))
        TMG0.register(24, 8, Datapoint("WR2PRE", default=0xf, validity=Validator(0, 2 ** 8)))

        TMG1 = Reg32("TMG1", 0x4)
        TMG1.register(0, 8, Datapoint("TRC", default=0x14, validity=Validator(0, 2 ** 8)))
        TMG1.register(8, 8, Datapoint("TRTP", default=0x4, validity=Validator(0, 2 ** 8)))
        TMG1.register(16, 6, Datapoint("TXP", default=0x10, validity=Validator(0, 2 ** 6)))

        TMG2 = Reg32("TMG2", 0x8)
        TMG2.register(0, 8, Datapoint("WR2RD", default=0xd, validity=Validator(0, 2 ** 8)))
        TMG2.register(8, 8, Datapoint("RD2WR", default=0x6, validity=Validator(0, 2 ** 8)))
        TMG2.register(16, 7, Datapoint("RL", default=0x10, validity=Validator(0, 2 ** 7)))
        
        TMG3 = Reg32("TMG3", 0x8)
        TMG3.register(0, 8, Datapoint("WR2MR", default=0x4, validity=Validator(0, 2 ** 8)))
        TMG3.register(8, 8, Datapoint("RD2MR", default=0x4, validity=Validator(0, 2 ** 8)))
        TMG3.register(16, 7, Datapoint("TMR", default=0x4, validity=Validator(0, 2 ** 7)))
        
        TMG4 = Reg32("TMG4", 0x10)
        TMG4.register(0, 7, Datapoint("TRP", default=0x5, validity=Validator(0, 2 ** 8)))
        TMG4.register(8, 6, Datapoint("TRRD", default=0x4, validity=Validator(0, 2 ** 8)))
        TMG4.register(16, 6, Datapoint("TCCD", default=0x4, validity=Validator(0, 2 ** 7)))
        TMG4.register(24, 6, Datapoint("TRCD", default=0x5, validity=Validator(0, 2 ** 7)))