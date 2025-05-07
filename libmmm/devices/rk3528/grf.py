'''
Created on Mar 19, 2023

@author: boogie
'''
from libmmm.devices.rockchip import grf


class GRF_CORE(grf.GRF):
    devname = "GRF_CORE"
    start = 0xFF300000

    def __init__(self, start=None):
        start = start or self.start
        super(GRF_CORE, self).__init__(self.devname, start)
        self.grfcommon()


class GRF_GPU(GRF_CORE):
    devname = "GRF_GPU"
    start = 0xFF310000
