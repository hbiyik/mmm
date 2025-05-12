'''
Created on Mar 19, 2023

@author: boogie
'''
from libmmm.devices.rk3588.cru import CRU as Rk3588CRU
from libmmm.model import Device, Datapoint, Validator

# FIX-ME: This is actually a divided clock with mux to c/gpll
F500M = "F500M"
F300M = "F300M"
F100M = "F100M"
CLOCK_F100M = 100
CLOCK_F300M = 300
CLOCK_F500M = 500

XIN = "XIN"
CLOCK_XIN = 24


aclk_gpu_root = "aclk_gpu_root"
pclk_gpu_root = "pclk_gpu_root"
aclk_gpu = "aclk_gpu"
clk_gpu_pvtpll = "clk_gpu_pvtpll"
aclk_gpu_mali = "aclk_gpu_mali"

pclk_pwm0 = "pclk_pwm0"
clk_pwm0 = "clk_pwm0"
clk_capture_pwm0 = "clk_capture_pwm0"
pclk_pwm1 = "pclk_pwm1"
clk_pwm1 = "clk_pwm1"
clk_capture_pwm1 = "clk_capture_pwm1"


class CRU(Rk3588CRU):
    devname = "CRU"
    start = 0xff4a0000

    def __init__(self, start=None):
        start = start or self.start
        Device.__init__(self, self.devname, start)

        clksel_gpu = self.regfromoffset(0x300 + 4 * 76, base=0x300, prefix="CLKSEL_")
        clksel_gpu.register(0, 2, datapoint=Datapoint(f"{aclk_gpu_root}_mux", validity=Validator(0, 3, F500M, F300M, F100M, XIN)))
        clksel_gpu.register(4, 2, datapoint=Datapoint(f"{pclk_gpu_root}_mux", validity=Validator(0, 3, F500M, F300M, F100M, XIN)))
        clksel_gpu.register(6, 1, datapoint=Datapoint(f"{aclk_gpu}_mux", validity=Validator(0, 1, "MUX", "PVTPLL")))
        clksel_gpu.register(7, 1, datapoint=Datapoint(f"{clk_gpu_pvtpll}_mux", validity=Validator(0, 1, "MUX", "PVTPLL")))
        self.block(clksel_gpu)

        gpu_clks = [None] * 16
        gpu_clks[0] = aclk_gpu_root
        gpu_clks[2] = pclk_gpu_root
        gpu_clks[7] = aclk_gpu
        gpu_clks[8] = aclk_gpu_mali
        clkgate_gpu = self.clkgate(0x800 + 34 * 4, *gpu_clks)
        self.block(clkgate_gpu)

        self.addgroup("GPU", clksel_gpu.name)
        self.addgroup("GPU", clkgate_gpu.name)

        pwm_clks = [None] * 16
        pwm_clks[4] = pclk_pwm0
        pwm_clks[5] = clk_pwm0
        pwm_clks[6] = clk_capture_pwm0
        pwm_clks[7] = pclk_pwm1
        pwm_clks[8] = clk_pwm1
        pwm_clks[9] = clk_capture_pwm1
        clkgate_pwm = self.clkgate(0x800 + 11 * 4, *pwm_clks)
        self.block(clkgate_pwm)
