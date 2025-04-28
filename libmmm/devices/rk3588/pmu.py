'''
Created on Apr 6, 2023

@author: z0042jww
'''
from libmmm.model import Device, Datapoint, Validator, Reg32
from libmmm.devices.rockchip import RK_Reg32_16bitMasked


STATUS_LISTS = [["PD_BUS", "VD_DDR23", "VD_DDR01", "PD_CENTER", "PD_CRYPTO", "PD_SDMMC",
                 "PD_USB", "PD_SDIO", "PD_NVM0", "PD_PCIE", "PD_GMAC", "PD_PHP",
                 "PD_AUDIO", "PD_VO1", "PD_VO0", "PD_VOP", "PD_RGA31", "PD_ISP1",
                 "PD_FEC", "PD_VI", "PD_AV1", "PD_RGA30", "PD_VDPU",
                 "PD_RKVDEC1", "PD_RKVDEC0", "PD_VENC1", "PD_VENC0", "PD_NPU2", "PD_NPU1",
                 "PD_NPUTOP", "VD_GPU"],
                ["PCIEPHY", "HDMIRXPHY", "PD_VOPESMAKRT", "PD_VOPDSC4K", "PD_VOPDSC8K", "PD_VOPCLUSTER3",
                 "PD_VOPCLUSTER2", "PD_VOPCLUSTER1", "PD_VOPCLUSTER0", "PD_CPU0", "PD_CPU1", "PD_CPU3",
                 "PD_CPU3", "PD_CPU4", "PD_CPU5", "PD_CPU6", "PD_CPU7", "PD_DSU"]]

GATE_LISTS = ["VD_GPU", "VD_NPU", "VD_VCODEC", "PD_NPUTOP", "PD_NPU1", "PD_NPU2",
              "PD_VEND0", "PD_VENC1", "PD_RKDEC0", "PD_RKVEDC1", "PD_VPU", "PD_RGA30",
              "PD_AV1", "PD_VI", "PD_FEC", "PD_ISP1", "PD_RGA31", "PD_VOP",
              "PD_VO0", "PD_VO1", "PD_AUDIO", "PD_PHP", "PD_GMAC", "PD_PCIE",
              "PD_NVM", "PD_NVM0", "PD_SDIO", "PD_USB", "PD_SECURE", "PD_SDMMC",
              "PD_CRYPTO", "PD_CENTER",
              "VD_DDR01", "VD_DDR23"]


def iterlistchunks(arr, size):
    count = int(len(arr) / size)
    left = len(arr) % size
    for i in range(count):
        yield arr[i * size: (i + 1) * size]
    if left:
        yield arr[(i + 1) * size:]


class PMU(Device):
    devname = "PMU"
    start = 0xFD8D0000

    def __init__(self, start=None):
        start = start or self.start
        super(PMU, self).__init__(self.devname, start)

        PWR_CON2 = RK_Reg32_16bitMasked("PWR_CON2", 0x8000)
        PWR_CON2.register(0, 1, Datapoint("cpu0_lp_bypass", default=0, validity=Validator(0, 1)))
        PWR_CON2.register(1, 1, Datapoint("cpu1_lp_bypass", default=0, validity=Validator(0, 1)))
        PWR_CON2.register(2, 1, Datapoint("cpu2_lp_bypass", default=0, validity=Validator(0, 1)))
        PWR_CON2.register(3, 1, Datapoint("cpu3_lp_bypass", default=0, validity=Validator(0, 1)))
        PWR_CON2.register(4, 1, Datapoint("cpu4_lp_bypass", default=0, validity=Validator(0, 1)))
        PWR_CON2.register(5, 1, Datapoint("cpu5_lp_bypass", default=0, validity=Validator(0, 1)))
        PWR_CON2.register(6, 1, Datapoint("cpu6_lp_bypass", default=0, validity=Validator(0, 1)))
        PWR_CON2.register(7, 1, Datapoint("cpu7_lp_bypass", default=0, validity=Validator(0, 1)))
        self.block(PWR_CON2)

        DSU_PWR_CON = RK_Reg32_16bitMasked("DSU_PWR_CON", 0x8004)
        DSU_PWR_CON.register(0, 1, Datapoint("dsu_pwrdn_ena", default=0, validity=Validator(0, 1)))
        DSU_PWR_CON.register(1, 1, Datapoint("dsu_pwroff_ena", default=0, validity=Validator(0, 1)))
        DSU_PWR_CON.register(2, 1, Datapoint("dsu_clusterpactive_bit_full_flag", default=0, validity=Validator(0, 1)))
        DSU_PWR_CON.register(3, 1, Datapoint("dsu_funcret_ena", default=0, validity=Validator(0, 1)))
        DSU_PWR_CON.register(5, 5, Datapoint("dsu_mem_dwn_ack_bypass", default=0, validity=Validator(0, 2 ** 5 - 1)))
        DSU_PWR_CON.register(10, 1, Datapoint("dsu_mem_dwn_ack_clamp_ena", default=0, validity=Validator(0, 1)))
        self.block(DSU_PWR_CON)

        regname = "PWR_GATE_STATUS"
        offset = 0x8180
        for i, domainlist in enumerate(iterlistchunks(GATE_LISTS, 32)):
            _regname = f"{regname}{i}"
            reg = Reg32(_regname, offset)
            reg.allowwrite = False
            for j, domain in enumerate(domainlist):
                reg.register(j, 1, Datapoint(domain, default=0, validity=Validator(0, 1, "ON", "OFF")))
            self.block(reg)
            self.addgroup(regname, _regname)
            offset += 4

        regname = "REPAIR_STATUS"
        offset = 0x8280
        for prefix, validmap in {"PGDONE": ["NOTCOMPLETE", "COMPLETE"], "CED": ["READY", "BUSY"], "POWER": ["ON", "OFF"]}.items():
            for i, domainlist in enumerate(STATUS_LISTS):
                _regname = f"{regname}_{prefix}{i}"
                reg = Reg32(_regname, offset)
                reg.allowwrite = False
                for j, domain in enumerate(domainlist):
                    reg.register(j, 1, Datapoint(domain, default=0, validity=Validator(0, 1, *validmap)))
                self.block(reg)
                self.addgroup(f"{regname}_{prefix}", _regname)
                offset += 4

        offset = 0x8140
        for regname in ["PWR_GATE_HARDCON", "PWR_GATE_SOFTCON"]:
            for i, domainlist in enumerate(iterlistchunks(GATE_LISTS, 16)):
                _regname = f"{regname}{i}"
                reg = RK_Reg32_16bitMasked(_regname, offset)
                reg.allowwrite = False
                for j, domain in enumerate(domainlist):
                    reg.register(j, 1, Datapoint(domain, default=0, validity=Validator(0, 1, "ON", "OFF")))
                self.block(reg)
                self.addgroup(regname, _regname)
                offset += 4
