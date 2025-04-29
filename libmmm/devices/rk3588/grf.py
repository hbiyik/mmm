'''
Created on Mar 19, 2023

@author: boogie
'''
from libmmm.devices.rockchip import grf


class BIGCORE0_GRF(grf.GRF):
    devname = "BIGCORE0_GRF"
    start = 0xFD590000


class BIGCORE1_GRF(grf.GRF):
    devname = "BIGCORE1_GRF"
    start = 0xFD592000


class GPU_GRF(grf.GRF):
    devname = "GPU_GRF"
    start = 0xFD5A0000
