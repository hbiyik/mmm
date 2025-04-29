'''
Created on Mar 19, 2023

@author: boogie
'''
from libmmm.devices.rockchip import grf


class GPU_GRF(grf.GRF):
    devname = "GPU_GRF"
    start = 0xFF310000
