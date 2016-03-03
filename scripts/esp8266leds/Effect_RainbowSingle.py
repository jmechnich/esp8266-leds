from esp8266leds.Effect_Rainbow import Rainbow
from esp8266leds.RainbowCommon  import iterate_lin, clamp

import colorsys

class RainbowSingle(Rainbow):
    def __init__(self,args):
        super(RainbowSingle,self).__init__(args)

    def iterate(self):
        self.step_hue()
        rgb = [ int((j*self.max)+0.5)
                for j in colorsys.hsv_to_rgb(self.hue,1,1) ]
        return clamp(rgb*self.nled)

def create_parser():
    from esp8266leds.RainbowCommon import create_parser as cp
    return cp()

def instance(args):
    return RainbowSingle(args)
