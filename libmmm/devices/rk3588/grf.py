'''
Created on Mar 19, 2023

@author: boogie
'''
from libmmm.devices.rockchip import grf


class GRF_BIGCORE0(grf.GRF):
    devname = "GRF_BIGCORE0"
    start = 0xFD590000

    def __init__(self, start=None):
        start = start or self.start
        super(GRF_BIGCORE0, self).__init__(self.devname, start)
        self.grfcommon()
        self.bigcore_cfg()


class GRF_BIGCORE1(GRF_BIGCORE0):
    devname = "GRF_BIGCORE1"
    start = 0xFD592000


class GRF_GPU(grf.GRF):
    devname = "GRF_GPU"
    start = 0xFD5A0000

    def __init__(self, start=None):
        start = start or self.start
        super(GRF_GPU, self).__init__(self.devname, start)
        self.grfcommon()
        self.gpu_conf()
