'''
Created on Mar 19, 2023

@author: boogie
'''
from libmmm.model import Device
from libmmm.devices.rockchip.gpio import GPIO


class GPIO0(GPIO, Device):
    devname = "GPIO0"
    start = 0xFD8A0000


class GPIO1(GPIO, Device):
    devname = "GPIO1"
    start = 0xFEC20000


class GPIO2(GPIO, Device):
    devname = "GPIO2"
    start = 0xFEC30000


class GPIO3(GPIO, Device):
    devname = "GPIO3"
    start = 0xFEC40000


class GPIO4(GPIO, Device):
    devname = "GPIO4"
    start = 0xFEC50000
