'''
Created on Nov 4, 2022

@author: boogie
'''
import os
import mmap
import binascii
from libmmm.helper import logger


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


class Memory(Io):
    def init(self):
        # PAGESIZE ALIGN
        self.startoffset = self.start % self.pagesize
        start = int(self.start / self.pagesize) * self.pagesize
        startoffset = self.start - start
        size = (int((self.size + startoffset) / self.pagesize) + 1) * self.pagesize
        logger.debug("%s binding: [%d (%s), %d (%s)]", self.dev, start, hex(start), start + size, hex(start + size))
        # MAP physical memory
        if self.flag_r and self.flag_w:
            flags = os.O_RDWR | os.O_SYNC
        else:
            flags = os.O_RDONLY | os.O_CLOEXEC
        self.f = os.open(self.dev, flags)
        flags = 0
        if self.flag_r:
            flags |= mmap.PROT_READ
        if self.flag_w:
            flags |= mmap.PROT_WRITE
        self.mmap = mmap.mmap(self.f, size, mmap.MAP_SHARED, flags, offset=start)
        self.bindstart = start
        self.bindsize = size
        super(Memory, self).init()

    def readio(self, start, size):
        self.mmap.seek(self.startoffset + start)
        logger.debug("%s read start: %s, size: %d",
                     self.dev, hex(self.start + self.startoffset + start), size)
        val = self.mmap.read(size)
        logger.debug("%s read end: %s, size: %d, val: 0x%s",
                     self.dev, hex(self.start + self.startoffset + start), size, binascii.hexlify(val).decode())
        return val

    def writeio(self, start, data):
        logger.debug("%s write start: %s data: 0x%s", self.dev, hex(self.start + self.startoffset + start), binascii.hexlify(data).decode())
        self.mmap.seek(self.startoffset + start)
        retval = self.mmap.write(data)
        logger.debug("%s is written with %d length", self.dev, retval)
        return retval

    def close(self):
        if self.isinited:
            logger.debug("%s unbinding: [%d (%s), %d (%s)]", self.dev,
                         self.bindstart, hex(self.bindstart),
                         self.bindsize, hex(self.bindsize))
            self.mmap.close()
            os.close(self.f)
