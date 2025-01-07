import struct
from libmmm.model import Reg32


class RK_Reg32_16bitMasked(Reg32):
    def write(self, name, value):
        oldval = self.readraw()
        for start, size, datapoint in self.iterdatapoints():
            if datapoint.name == name:
                value = self._checkvalidity(datapoint, value)
                # set both the the sart and start + 16 with write mask set to true
                newval = struct.unpack("%sI" % self.endian, self._setbit(oldval, start, size, value))[0]
                super(Reg32, self).write(self._setbit(newval, 16 + start, size, 2 ** size - 1))
                return True
