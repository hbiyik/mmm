import struct
from libmmm.model import Reg32

class RK_Reg32_16bitMasked(Reg32):
    def write(self, name, value):
        oldval = self.readraw()
        for start, size, datapoint in self.iterdatapoints():
            if datapoint.name == name:
                # set bot the the sart and start + 16 with write mask set to true
                newval = struct.unpack("%sI" % self.endian, self.setbit(oldval, start, size, value))[0]
                super(Reg32, self).write(self.setbit(newval, 16 + start, 2 ** size, value))
                return True
