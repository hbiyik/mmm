'''
Created on Nov 4, 2022

@author: boogie
'''
from libmmm.helper import logger
import struct


class Device:
    def __init__(self, name, start):
        self.name = name
        self.start = start
        self.size = 0
        self.__blocks = []
        self.__io = None
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
        return self.__io

    @io.setter
    def io(self, io):
        if io is None and self.__io:
            logger.debug("Device: %s, Uninding IO to [%d (%s), %d (%s)]",
                         self.name, self.start, hex(self.start),
                         self.start + self.size, hex(self.start + self.size))
            self.__io.close()
            self.__io = None
        else:
            logger.debug("Device: %s, Binding IO to [%d (%s), %d (%s)]",
                         self.name, self.start, hex(self.start),
                         self.start + self.size, hex(self.start + self.size))
            self.__io = io(self.start, self.size)

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


class Reg32(Block):
    def __init__(self, name, start):
        super(Reg32, self).__init__(name, start, 4)
        self.endian = "<"
        self.bitsize = self.size * 8
        self.__regs = []
        self.maxbits = self._maxnbit(self.bitsize)

    def _maxnbit(self, size):
        return ((2 ** size) - 1)

    def register(self, start, size, datapoint):
        self.__regs.append((start, size, datapoint))

    def readraw(self):
        buffer = super(Reg32, self).read()
        return struct.unpack("%sI" % self.endian, buffer.value)[0]

    def read(self):
        buffer = self.readraw()
        for start, size, datapoint in self.iterdatapoints():
            if start is None or size is None:
                continue
            value = (buffer >> (start)) & self._maxnbit(size)
            logger.debug("Reg32: reading %s bit value=%d from register %s start=%d, length=%d, data=%s",
                         datapoint.name, value, self.name, start, size, bin(buffer))
            datapoint.value = value
        return list(self)

    def _setbit(self, data32bit, start, size, value):
        # reset the related bits to 0
        data32bit = data32bit & ~((self.maxbits << (start + size)) ^ (self.maxbits << start)) & self.maxbits
        # set the new bits
        newval = (data32bit | (value << start)) & self.maxbits
        return struct.pack("%sI" % self.endian, newval)

    def _checkvalidity(self, datapoint, value):
        if datapoint.validity and datapoint.validity.checkvalue(value):
            return datapoint.validity.getraw(value)
        else:
            return int(value)

    def write(self, name, value):
        oldval = self.readraw()
        for start, size, datapoint in self.iterdatapoints():
            if datapoint.name == name:
                value = self._checkvalidity(datapoint, value)
                super(Reg32, self).write(self._setbit(oldval, start, size, value))
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
        self.__value = value
        self.__default = default

    @property
    def value(self):
        if self.validity and self.validity.checkraw(self.__value):
            return self.validity.getvalue(self.__value)
        return self.__value

    @value.setter
    def value(self, value):
        if self.validity and self.validity.checkraw(value):
            self.__value = value
        else:
            self.__value = value

    @property
    def default(self):
        if self.__default is not None and self.validity and self.validity.checkraw(self.__default):
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
    def __init__(self, name, validity=None, unit=None, default=None):
        Datapoint.__init__(self, name, None, validity, unit, default)

    @property
    def value(self):
        return self.get()

    @value.setter
    def value(self, value):
        self.set(value)

    def get(self, register):
        raise NotImplementedError

    def set(self, register):
        raise NotImplementedError


class Io:
    def __init__(self, start, size, dev="/dev/mem", pagesize=4096, read=True, write=True):
        self.flag_r = read
        self.flag_w = write
        self.dev = dev
        self.pagesize = pagesize
        self.start = start
        self.size = size
        self.isinited = False

    def init(self):
        self.isinited = True

    def read(self, start, size):
        if not self.isinited:
            self.init()
        return self.readio(start, size)

    def write(self, start, data):
        if not self.isinited:
            self.init()
        return self.writeio(start, data)

    def close(self):
        pass

    def writeio(self, start, size, data):
        raise NotImplementedError

    def readio(self, start, size):
        raise NotImplementedError


class Validator:
    def __init__(self, intfrom, intto, *valuemap):
        self.intfrom = intfrom
        self.intto = intto
        self.valuemap = [str(x).upper() for x in valuemap]

    def checkraw(self, value):
        if self.intfrom and self.intto:
            if value > self.intfrom or value < self.intfrom:
                raise ValueError("%s <= %s <= %s value not in range" % (self.intfrom,
                                                                        value,
                                                                        self.valuefrom))
        return True

    def checkvalue(self, value):
        if self.valuemap:
            value = str(value).upper()
            if value not in self.valuemap:
                raise ValueError("%s value not in %s" % (value, self.help()))
        else:
            return self.checkraw(value)
        return True

    def getraw(self, value):
        if self.valuemap:
            return self.valuemap.index(str(value).upper()) + self.intfrom
        else:
            return int(value)

    def getvalue(self, rawvalue):
        if self.valuemap:
            return self.valuemap[self.intfrom + rawvalue]
        else:
            return rawvalue

    def help(self):
        if self.valuemap:
            return ",".join(self.valuemap)
        else:
            return "[%d~%d]" % (self.intfrom, self.intto)
