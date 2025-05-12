"""
 Copyright (C) 2025 boogie

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from libmmm import model
from libmmm import common


class PWM(model.Device):
    devname = ""
    start = 0
    num_pwms = 4

    def __init__(self, start=None):
        start = start or self.start
        super(PWM, self).__init__(self.devname, start)

        offset = 0
        for pwm in range(self.num_pwms):
            reg = model.Reg32(f"PWM{pwm}_COUNT", offset)
            reg.register(0, 32, datapoint=model.Datapoint("count", validity=model.Validator(0, 2 ** 32 - 1)))
            reg.allowwrite = False
            self.block(reg)
            self.addgroup(f"PWM{pwm}", f"PWM{pwm}_COUNT")
            offset += 4

            reg = model.Reg32(f"PWM{pwm}_PERIOD", offset)
            reg.register(0, 32, datapoint=model.Datapoint("period", validity=model.Validator(0, 2 ** 32 - 1)))
            self.block(reg)
            self.addgroup(f"PWM{pwm}", f"PWM{pwm}_PERIOD")
            offset += 4

            reg = model.Reg32(f"PWM{pwm}_DUTY", offset)
            reg.register(0, 32, datapoint=model.Datapoint("cycle", validity=model.Validator(0, 2 ** 32 - 1)))
            self.block(reg)
            self.addgroup(f"PWM{pwm}", f"PWM{pwm}_DUTY")
            offset += 4

            reg = model.Reg32(f"PWM{pwm}_CTRL", offset)
            reg.register(0, 1, datapoint=model.Datapoint("enable", validity=model.Validator(0, 1, common.OFF, common.ON)))
            reg.register(1, 2, datapoint=model.Datapoint("mode", validity=model.Validator(0, 3, "once", "cont", "capture", "reserved")))
            reg.register(3, 1, datapoint=model.Datapoint("duty_polarity", validity=model.Validator(0, 1, "negative", "positive")))
            reg.register(4, 1, datapoint=model.Datapoint("inactive_polarity", validity=model.Validator(0, 1, "negative", "positive")))
            reg.register(5, 1, datapoint=model.Datapoint("align", validity=model.Validator(0, 1, "left", "center")))
            reg.register(6, 1, datapoint=model.Datapoint("conlock", validity=model.Validator(0, 1, common.OFF, common.ON)))
            reg.register(7, 1, datapoint=model.Datapoint("ch_ct_enable", validity=model.Validator(0, 1, common.OFF, common.ON)))
            reg.register(8, 1, datapoint=model.Datapoint("force_clk_enable", validity=model.Validator(0, 1, common.OFF, common.ON)))
            reg.register(9, 1, datapoint=model.Datapoint("clk_scale", validity=model.Validator(0, 1, common.OFF, common.ON)))
            reg.register(10, 1, datapoint=model.Datapoint("clk_src_sel", validity=model.Validator(0, 1, "PLL", "XIN")))
            reg.register(12, 3, datapoint=model.Datapoint("prescale", validity=model.Validator(0, 2 ** 3 - 1)))
            reg.register(16, 8, datapoint=model.Datapoint("scale", validity=model.Validator(0, 2 ** 8 - 1)))
            reg.register(24, 8, datapoint=model.Datapoint("repeat", validity=model.Validator(0, 2 ** 8 - 1)))
            self.block(reg)
            self.addgroup(f"PWM{pwm}", f"PWM{pwm}_CTRL")
            offset += 4
