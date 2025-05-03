'''
Created on Mar 19, 2023

@author: boogie
'''
from libmmm.devices.rockchip import grf


class GRF_BIGCORE0(grf.GRF):
    devname = "GRF_BIGCORE0"
    start = 0xFD590000


class GRF_BIGCORE1(grf.GRF):
    devname = "GRF_BIGCORE1"
    start = 0xFD592000


class GRF_GPU(grf.GRF):
    devname = "GRF_GPU"
    start = 0xFD5A0000
