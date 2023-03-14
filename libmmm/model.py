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
    
    @property
    def io(self):
        if not self.__io:
            raise RuntimeError("IO backend is not yet attached")
        return self.__io
    
    @io.setter
    def io(self, io):
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
        
    def maxnbit(self, size):
        return ((2 ** size) - 1)

    def register(self, start, size, datapoint):
        # logger.debug("Reg32: %s. Register added name=%s, start=%d, size=%d", self.name,
        #             datapoint.name, start, size)
        self.__regs.append((start, size, datapoint))
        
    def readraw(self):
        buffer = super(Reg32, self).read()
        return struct.unpack("%sI" % self.endian, buffer.value)[0]
        
    def read(self):
        buffer = self.readraw()
        for start, size, datapoint in self.__regs:
            if start is None or size is None:
                continue
            value = (buffer >> (start)) & self.maxnbit(size)
            logger.debug("Reg32: reading %s bit value=%d from register %s start=%d, length=%d, data=%s",
                         datapoint.name, value, self.name, start, size, bin(buffer))
            datapoint.value = value
        return [x[2] for x in self.__regs]
    
    def write(self, name, value):
        oldval = self.readraw()
        for start, size, datapoint in self.__regs:
            if start is None or size is None:
                continue
            if datapoint.name == name:
                maxbits = self.maxnbit(self.bitsize)
                # reset the related bits to 0
                oldval = oldval & ~((maxbits << (start + size)) ^ (maxbits << start)) & maxbits
                # hint: no need to mask the new value, be careful about input validation though
                newval = (oldval | (value << start)) & maxbits
                newval = struct.pack("%sI" % self.endian, newval)
                super(Reg32, self).write(newval)
                return True
        
    def __iter__(self):
        for reg in self.__regs:
            yield reg[2]
            
class Datapoint:
    def __init__(self, name, value=None, validity=None, unit=None, default=None):
        self.name = name
        self.value = value
        self.validity = validity
        self.unit = unit
        self.default = default
        
    def __repr__(self):
        txt = "%s = %s" % (self.name, self.value)
        if self.unit is not None:
            txt += " %s" % self.unit
        if self.default is not None:
            txt += ", (default=%s)" % self.default
        return txt
    
class VirtualDatapoint(Datapoint):
    def __init__(self, name, register, validity=None, unit=None, default=None):
        self.name = name
        self.register = register
        self.validity = validity
        self.unit = unit
        self.default = default

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
