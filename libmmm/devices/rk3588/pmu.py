'''
Created on Apr 6, 2023

@author: z0042jww
'''
from libmmm.model import Device, Datapoint, Validator, Reg32
from libmmm.devices.rockchip import RK_Reg32_16bitMasked
from libmmm import common

# pd/vd domains
PD_PMU1 = "PD_PMU1"
VD_GPU = "VD_GPU"
PD_NPUTOP = "PD_NPUTOP"
PD_NPU1 = "PD_NPU1"
PD_NPU2 = "PD_NPU2"
VD_NPU = "VD_NPU"
PD_VENC0 = "PD_VENC0"
PD_VENC1 = "PD_VENC1"
PD_RKVDEC0 = "PD_RKVDEC0"
PD_RKVDEC1 = "PD_RKVDEC1"
VD_VCODEC = "VD_VCODEC"
PD_VPU = "PD_VPU"
PD_RGA30 = "PD_RGA30"
PD_AV1 = "PD_AV1"
PD_VI = "PD_VI"
PD_FEC = "PD_FEC"
PD_ISP1 = "PD_ISP1"
PD_RGA31 = "PD_RGA31"
PD_VOP = "PD_VOP"
PD_VO0 = "PD_VO0"
PD_VO1 = "PD_VO1"
PD_AUDIO = "PD_AUDIO"
PD_PHP = "PD_PHP"
PD_GMAC = "PD_GMAC"
PD_PCIE = "PD_PCIE"
PD_NVM0 = "PD_NVM0"
PD_NVM = "PD_NVM"
PD_SDIO = "PD_SDIO"
PD_USB = "PD_USB"
PD_SDMMC = "PD_SDMMC"
PD_CRYPTO = "PD_CRYPTO"
PD_SECURE = "PD_SECURE"
PD_CENTER = "PD_CENTER"
PD_DDR01 = "PD_DDR01"
PD_DDR23 = "PD_DDR23"
VD_DDR01 = "VD_DDR01"
VD_DDR23 = "VD_DDR23"
PD_BUS = "PD_BUS"
PD_DSU = "PD_DSU"
PD_CPU7 = "PD_CPU7"
PD_CPU6 = "PD_CPU6"
PD_CPU5 = "PD_CPU5"
PD_CPU4 = "PD_CPU4"
PD_CPU3 = "PD_CPU3"
PD_CPU2 = "PD_CPU2"
PD_CPU1 = "PD_CPU1"
PD_CPU0 = "PD_CPU0"
PD_VOPCLUSTER0 = "PD_VOPCLUSTER0"
PD_VOPCLUSTER1 = "PD_VOPCLUSTER1"
PD_VOPCLUSTER2 = "PD_VOPCLUSTER2"
PD_VOPCLUSTER3 = "PD_VOPCLUSTER3"
PD_VOPDSC8K = "PD_VOPDSC8K"
PD_VOPDSC4K = "PD_VOPDSC4K"
PD_VOPESMAKRT = "PD_VOPESMAKRT"

HDMIRXPHY = "HDMIRXPHY"
PCIEPHY = "PCIEPHY"

# bius
BIU_GPU = "BIU_GPU"
BIU_NPUTOP = "BIU_NPUTOP"
BIU_NPU1 = "BIU_NPU1"
BIU_NPU2 = "BIU_NPU2"
BIU_VENC0 = "BIU_VENC0"
BIU_VENC1 = "BIU_VENC1"
BIU_RKVDEC0 = "BIU_RKVDEC0"
BIU_RKVDEC1 = "BIU_RKVDEC1"
BIU_VDPU = "BIU_VDPU"
BIU_AV1 = "BIU_AV1"
BIU_VI = "BIU_VI"
BIU_ISP1 = "BIU_ISP1"
BIU_RGA31 = "BIU_RGA31"
BIU_VOP = "BIU_VOP"
BIU_VOP_CHANNEL = "BIU_VOP_CHANNEL"
BIU_VO0 = "BIU_VO0"
BIU_VO1 = "BIU_VO1"
BIU_AUDIO = "BIU_AUDIO"
BIU_NVM = "BIU_NVM"
BIU_SDIO = "BIU_SDIO"
BIU_USB = "BIU_USB"
BIU_PHP = "BIU_PHP"
BIU_VO1USBTOP = "BIU_VO1USBTOP"
BIU_SECURE = "BIU_SECURE"
BIU_SECURE_CENTER_CHANNEL = "BIU_SECURE_CENTER_CHANNEL"
BIU_SECURE_VO1USB_CHANNEL = "BIU_SECURE_VO1USB_CHANNEL"
BIU_CENTER = "BIU_CENTER"
BIU_CENTER_CHANNEL = "BIU_CENTER_CHANNEL"
BIU_DDRSCH0 = "BIU_DDRSCH0"
BIU_DDRSCH1 = "BIU_DDRSCH1"
BIU_CENTER_DDRSCH = "BIU_CENTER_DDRSCH"
BIU_BUS = "BIU_BUS"
BIU_TOP = "BIU_TOP"
BIU_DDRSCH2 = "BIU_DDRSCH2"
BIU_DDRSCH3 = "BIU_DDRSCH3"


STATUS_LIST = [PD_PMU1, VD_GPU, PD_NPUTOP, PD_NPU1, PD_NPU2, PD_VENC0, PD_VENC1, PD_RKVDEC0, PD_RKVDEC1, PD_VPU,
               PD_RGA30, PD_AV1, PD_VI, PD_FEC, PD_ISP1, PD_RGA31, PD_VOP, PD_VO0, PD_VO1, PD_AUDIO, PD_PHP, PD_GMAC, PD_PCIE,
               PD_NVM0, PD_SDIO, PD_USB, PD_SDMMC, PD_CRYPTO, PD_CENTER, PD_DDR01, PD_DDR23, PD_BUS,
               PD_DSU, PD_CPU7, PD_CPU6, PD_CPU5, PD_CPU4, PD_CPU3, PD_CPU2, PD_CPU1, PD_CPU0, PD_VOPCLUSTER0, PD_VOPCLUSTER1,
               PD_VOPCLUSTER2, PD_VOPCLUSTER3, PD_VOPDSC8K, PD_VOPDSC4K, PD_VOPESMAKRT, HDMIRXPHY, PCIEPHY]

GATE_LIST = [VD_GPU, VD_NPU, VD_VCODEC, PD_NPUTOP, PD_NPU1, PD_NPU2,
             PD_VENC0, PD_VENC1, PD_RKVDEC0, PD_RKVDEC1, PD_VPU, PD_RGA30,
             PD_AV1, PD_VI, PD_FEC, PD_ISP1, PD_RGA31, PD_VOP,
             PD_VO0, PD_VO1, PD_AUDIO, PD_PHP, PD_GMAC, PD_PCIE,
             PD_NVM, PD_NVM0, PD_SDIO, PD_USB, PD_SECURE, PD_SDMMC,
             PD_CRYPTO, PD_CENTER,
             VD_DDR01, VD_DDR23]

BIU_LIST = [BIU_GPU, BIU_NPUTOP, BIU_NPU1, BIU_NPU2, BIU_VENC0, BIU_VENC1, BIU_RKVDEC0, BIU_RKVDEC1, BIU_VDPU, BIU_AV1,
            BIU_VI, BIU_ISP1, BIU_RGA31, BIU_VOP, BIU_VOP_CHANNEL, BIU_VO0, BIU_VO1, BIU_AUDIO, BIU_NVM, BIU_SDIO, BIU_USB,
            BIU_PHP, BIU_VO1USBTOP, BIU_SECURE, BIU_SECURE_CENTER_CHANNEL, BIU_SECURE_VO1USB_CHANNEL, BIU_CENTER, BIU_CENTER_CHANNEL,
            BIU_DDRSCH0, BIU_DDRSCH1, BIU_DDRSCH2, BIU_DDRSCH3, BIU_CENTER_DDRSCH, BIU_BUS, BIU_TOP]

PD_MEM_LIST = [None, None, None, PD_NPUTOP, PD_NPU1, PD_NPU2, PD_VENC0, PD_VENC1, PD_RKVDEC0, PD_RKVDEC1, None,
               PD_RGA30, PD_AV1, PD_VI, PD_FEC, PD_ISP1, PD_RGA31, PD_VOP, PD_VO0, PD_VO1, PD_AUDIO, PD_PHP, PD_GMAC, PD_PCIE, None,
               PD_NVM0, PD_SDIO, PD_USB, None, PD_SDMMC, PD_CRYPTO, PD_CENTER, PD_DDR01, PD_DDR23]


class PMU(Device):
    devname = "PMU"
    start = 0xFD8D0000

    def __init__(self, start=None):
        start = start or self.start
        super(PMU, self).__init__(self.devname, start)

        PWR_CON2 = RK_Reg32_16bitMasked("PWR_CON2", 0x8000)
        for i in range(8):
            PWR_CON2.register(i, 1, Datapoint(f"cpu{i}_lp_bypass", default=0, validity=Validator(0, 1)))
        self.block(PWR_CON2)

        DSU_PWR_CON = RK_Reg32_16bitMasked("DSU_PWR_CON", 0x8004)
        DSU_PWR_CON.register(0, 1, Datapoint("dsu_pwrdn_ena", default=0, validity=Validator(0, 1)))
        DSU_PWR_CON.register(1, 1, Datapoint("dsu_pwroff_ena", default=0, validity=Validator(0, 1)))
        DSU_PWR_CON.register(2, 1, Datapoint("dsu_clusterpactive_bit_full_flag", default=0, validity=Validator(0, 1)))
        DSU_PWR_CON.register(3, 1, Datapoint("dsu_funcret_ena", default=0, validity=Validator(0, 1)))
        DSU_PWR_CON.register(5, 5, Datapoint("dsu_mem_dwn_ack_bypass", default=0, validity=Validator(0, 2 ** 5 - 1)))
        DSU_PWR_CON.register(10, 1, Datapoint("dsu_mem_dwn_ack_clamp_ena", default=0, validity=Validator(0, 1)))
        self.block(DSU_PWR_CON)

        offset = 0x8100
        for regname in ["BIU_IDLE_REQUEST_HARD_CON", "BIU_IDLE_REQUEST_SOFT_CON"]:
            for i, domainlist in enumerate(common.iterlistchunks(BIU_LIST, 16)):
                _regname = f"{regname}{i}"
                reg = RK_Reg32_16bitMasked(_regname, offset)
                for j, domain in enumerate(domainlist):
                    reg.register(j, 1, Datapoint(domain, default=0, validity=Validator(0, 1, common.DISABLED, common.ENABLED)))
                self.block(reg)
                self.addgroup(regname, _regname)
                offset += 4

        offset = 0x8118
        regname = "BIU_IDLE_ACK_STATUS"
        for i, domainlist in enumerate(common.iterlistchunks(BIU_LIST, 32)):
            _regname = f"{regname}{i}"
            reg = Reg32(_regname, offset)
            reg.allowwrite = False
            for j, domain in enumerate(domainlist):
                reg.register(j, 1, Datapoint(domain, default=0, validity=Validator(0, 1, "NACK", "ACK")))
            self.block(reg)
            self.addgroup(regname, _regname)
            offset += 4

        offset = 0x8120
        regname = "BIU_IDLE_STATUS"
        for i, domainlist in enumerate(common.iterlistchunks(BIU_LIST, 32)):
            _regname = f"{regname}{i}"
            reg = Reg32(_regname, offset)
            reg.allowwrite = False
            for j, domain in enumerate(domainlist):
                reg.register(j, 1, Datapoint(domain, default=0, validity=Validator(0, 1, "BUSY", "IDLE")))
            self.block(reg)
            self.addgroup(regname, _regname)
            offset += 4

        offset = 0x8140
        for regname in ["PWR_GATE_HARD_CON", "PWR_GATE_SOFT_CON"]:
            for i, domainlist in enumerate(common.iterlistchunks(GATE_LIST, 16)):
                _regname = f"{regname}{i}"
                reg = RK_Reg32_16bitMasked(_regname, offset)
                for j, domain in enumerate(domainlist):
                    reg.register(j, 1, Datapoint(domain, default=0, validity=Validator(0, 1, common.ON, common.OFF)))
                self.block(reg)
                self.addgroup(regname, _regname)
                offset += 4

        regname = "PWR_GATE_STATUS"
        offset = 0x8180
        for i, domainlist in enumerate(common.iterlistchunks(GATE_LIST, 32)):
            _regname = f"{regname}{i}"
            reg = Reg32(_regname, offset)
            reg.allowwrite = False
            for j, domain in enumerate(domainlist):
                reg.register(j, 1, Datapoint(domain, default=0, validity=Validator(0, 1, common.ON, common.OFF)))
            self.block(reg)
            self.addgroup(regname, _regname)
            offset += 4

        offset = 0x81A0
        regname = "PWR_GATE_MEM_SOFT_CON"
        for i, domainlist in enumerate(common.iterlistchunks(PD_MEM_LIST, 16)):
            _regname = f"{regname}{i}"
            reg = RK_Reg32_16bitMasked(_regname, offset)
            for j, domain in enumerate(domainlist):
                if domain is None:
                    continue
                reg.register(j, 1, Datapoint(domain, default=0, validity=Validator(0, 1, common.DISABLED, common.ENABLED)))
            self.block(reg)
            self.addgroup(regname, _regname)
            offset += 4

        regname = "REPAIR_STATUS"
        offset = 0x8280
        for prefix, validmap in {"PGDONE": ["NOTCOMPLETE", "COMPLETE"], "CED": ["READY", "BUSY"], "POWER": [common.OFF, common.ON]}.items():
            for i, domainlist in enumerate(common.iterlistchunks(STATUS_LIST, 32)):
                _regname = f"{regname}_{prefix}{i}"
                reg = Reg32(_regname, offset)
                reg.allowwrite = False
                for j, domain in enumerate(domainlist):
                    reg.register(j, 1, Datapoint(domain, default=0, validity=Validator(0, 1, *validmap)))
                self.block(reg)
                self.addgroup(f"{regname}_{prefix}", _regname)
                offset += 4
