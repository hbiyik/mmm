'''
Created on Nov 4, 2022

@author: boogie
'''
from libmmm.helper import logger
from libmmm import common
from libmmm.io import Memory
import struct


class Device(metaclass=common.Singleton):
    @staticmethod
    def closeall():
        for cls, ins in common.Singleton.instances.items():
            if isinstance(ins, Device):
                ins.close()

    def __init__(self, name, start, io=None):
        self.name = name
        self.start = start
        self.size = 0
        self.iotype = io or Memory
        self.__io = None
        self.__blocks = []
        self.groups = {}

    def addgroup(self, groupname, blockname):
        block = self.getblock(blockname)
        if not block:
            return
        if groupname not in self.groups:
            self.groups[groupname] = []
        self.groups[groupname].append(block)
        return True

    def itergroups(self):
        blocks = []
        for groupname, blocklist in self.groups.items():
            blocks.extend([block.name for block in blocklist])
            yield groupname, blocklist
        for block in self:
            if block.name in blocks:
                continue
            yield block.name, [block]

    @property
    def io(self):
        if not self.__io and self.iotype:
            logger.debug("Device: %s, Binding IO to [%d (%s), %d (%s)]",
                         self.name, self.start, hex(self.start),
                         self.start + self.size, hex(self.start + self.size))
            self.__io = self.iotype(self.start, self.size)
        return self.__io

    def getblock(self, name):
        for block in self.__blocks:
            if block.name == name:
                return block

    def block(self, block):
        block.device = self
        self.__blocks.append(block)
        maxlen = block.start + block.size
        if maxlen > self.size:
            self.size = maxlen
        # logger.debug("Device: %s. Block added name=%s, start=%d, size=%d", self.name, block.name, block.start, block.size)

    def __iter__(self):
        for block in self.__blocks:
            yield block

    def close(self):
        if self.__io:
            logger.debug("Device: %s, Unbinding IO to [%d (%s), %d (%s)]",
                         self.name, self.start, hex(self.start),
                         self.start + self.size, hex(self.start + self.size))
            self.__io.close()


class Block:
    def __init__(self, name, start, size):
        self.device = None
        self.name = name
        self.start = start
        self.size = size

    def read(self):
        logger.debug("Block: %s reading" % self.name)
        return Datapoint("data", self.device.io.read(self.start, self.size))

    def write(self, data):
        logger.debug("Block: %s writing" % self.name)
        self.device.io.write(self.start, data)

    def __iter__(self):
        yield Datapoint("block", self.read())


class VirtualReg(Block):
    def __init__(self, name):
        self.device = None
        self.name = name
        self.start = 0
        self.size = 0
        self.__datapoints = []
        self.allowread = True
        self.allowwrite = False

    def read(self):
        pass

    def write(self, name, value):
        dp = self.get(name)
        if dp is None:
            raise IndexError(f"Datapoint {name} doesn't exist in register {self.name}")
        if not dp.allowwrite:
            raise RuntimeError("Read only datapoint, writing is not supported")
        dp.value = value

    def register(self, datapoint):
        if not self.allowwrite:
            datapoint.allowwrite = self.allowwrite
        if not self.allowread:
            datapoint.allowread = self.allowread
        datapoint.reg = self
        self.__datapoints.append(datapoint)

    def __iter__(self):
        for dp in self.__datapoints:
            yield dp

    def get(self, name):
        for dp in self:
            if dp.name == name:
                return dp


class Reg32(Block):
    def __init__(self, name, start):
        super(Reg32, self).__init__(name, start, 4)
        self.endian = "<"
        self.bitsize = self.size * 8
        self.__regs = []
        self.maxbits = self._maxnbit(self.bitsize)
        self.allowread = True
        self.allowwrite = True

    def _maxnbit(self, size):
        return ((2 ** size) - 1)

    def register(self, start, size, datapoint):
        if not self.allowwrite:
            datapoint.allowwrite = self.allowwrite
        if not self.allowread:
            datapoint.allowread = self.allowread
        datapoint.reg = self
        self.__regs.append((start, size, datapoint))

    def readraw(self):
        buffer = super(Reg32, self).read()
        return struct.unpack("%sI" % self.endian, buffer.value)[0]

    def read(self):
        if not self.allowread:
            raise RuntimeError("Write only register, reading is not supported")
        buffer = self.readraw()
        for start, size, datapoint in self.iterdatapoints():
            if start is None or size is None:
                continue
            value = (buffer >> (start)) & self._maxnbit(size)
            logger.debug("Reg32: reading %s bit value=%d from register %s start=%d, length=%d, data=%s",
                         datapoint.name, value, self.name, start, size, bin(buffer))
            datapoint.int = value
        return list(self)

    def _setbit(self, data32bit, start, size, value, buf=True):
        # reset the related bits to 0
        data32bit = data32bit & ~((self.maxbits << (start + size)) ^ (self.maxbits << start)) & self.maxbits
        # set the new bits
        newval = (data32bit | (value << start)) & self.maxbits
        if not buf:
            return newval
        return struct.pack("%sI" % self.endian, newval)

    def writedatapoint(self, oldval, start, size, value):
        super(Reg32, self).write(self._setbit(oldval, start, size, value))

    def sync(self):
        bufi = self.readraw()
        for start, size, datapoint in self.iterdatapoints():
            bufi = self._setbit(bufi, start, size, datapoint.int, buf=False)
        super(Reg32, self).write(struct.pack("%sI" % self.endian, bufi))

    def write(self, name, value, sync=True, zero=False):
        if not self.allowwrite:
            raise RuntimeError("Read only register, writing is not supported")
        for start, size, datapoint in self.iterdatapoints():
            if datapoint.name == name:
                if not datapoint.allowwrite:
                    raise RuntimeError("Read only datapoint, writing is not supported")
                datapoint.value = value
                if isinstance(datapoint, VirtualDatapoint) or not sync:
                    return True
                prev = 0 if zero else self.readraw()
                self.writedatapoint(prev, start, size, datapoint.int)
                return True

    def iterdatapoints(self):
        for start, size, datapoint in self.__regs:
            yield start, size, datapoint

    def __iter__(self):
        for _start, _size, datapoint in self.iterdatapoints():
            yield datapoint

    def get(self, name):
        for _start, _size, dp in self.iterdatapoints():
            if dp.name == name:
                return dp


class Datapoint:
    def __init__(self, name, value=None, validity=None, unit=None, default=None):
        self.name = name
        self.validity = validity
        self.unit = unit
        self.__int = value
        self.__default = default
        self.allowwrite = True
        self.allowread = True
        self.reg = None

    @property
    def int(self):
        return self.__int

    @property
    def value(self):
        if self.validity:
            return self.validity.getvalue(self.int)
        return self.int

    @int.setter
    def int(self, intval):
        if self.validity and self.validity.checkint(intval):
            self.__int = intval
        elif isinstance(intval, int):
            self.__int = intval
        else:
            raise ValueError(f"Datapoint {self.name} value {intval} is not accepted")

    @value.setter
    def value(self, value):
        if self.validity and self.validity.checkvalue(value):
            self.int = self.validity.getint(value)
        else:
            self.int = int(value)

    @property
    def default(self):
        if self.__default is not None and self.validity and self.validity.checkint(self.__default):
            return self.validity.getvalue(self.__default)
        return self.__default

    def __repr__(self):
        txt = "%s = %s" % (self.name, self.value)
        if self.unit is not None:
            txt += " %s" % self.unit
        if self.default is not None:
            txt += ", (default=%s)" % self.default
        if self.validity:
            txt += ", (values=%s)" % self.validity.help()
        return txt


class VirtualDatapoint(Datapoint):
    def __init__(self, name, value=None, validity=None, unit=None, default=None):
        Datapoint.__init__(self, name, value, validity, unit, default)
        self.allowwrite = False

    @property
    def int(self):
        return self.get()

    @int.setter
    def int(self, intval):
        super(VirtualDatapoint, type(self)).int.fset(self, intval)
        self.set(super().int)

    def get(self):
        raise NotImplementedError

    def set(self, value):
        raise NotImplementedError


class Validator:
    def __init__(self, intfrom, intto, *valuemap):
        self.intfrom = intfrom
        self.intto = intto
        self.valuemap = [str(x).upper() for x in valuemap]

    def checkint(self, intval):
        if self.intfrom and self.intto:
            if intval > self.intfrom or intval < self.intfrom:
                raise ValueError("%s <= %s <= %s value not in range" % (self.intfrom,
                                                                        intval,
                                                                        self.valuefrom))
        return True

    def checkvalue(self, mapped):
        if self.valuemap:
            mapped = str(mapped).upper()
            if mapped not in self.valuemap:
                raise ValueError("%s value not in %s" % (mapped, self.help()))
        return self.checkint(self.getint(mapped))

    def getint(self, mapped):
        if self.valuemap:
            return self.valuemap.index(str(mapped).upper()) + self.intfrom
        else:
            return int(mapped)

    def getvalue(self, intval):
        if self.valuemap:
            try:
                return self.valuemap[self.intfrom + intval]
            except TypeError:
                raise TypeError
        else:
            return intval

    def help(self):
        if self.valuemap:
            return ",".join(self.valuemap)
        else:
            return "[%d~%d]" % (self.intfrom, self.intto)
