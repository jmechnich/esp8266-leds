from esp8266leds.Effect_Rainbow import Rainbow
from esp8266leds.RainbowCommon  import iterate_lin, clamp

import colorsys

class RainbowMirror(Rainbow):
    def __init__(self,args):
        super(RainbowMirror,self).__init__(args)

    def iterate(self):
        val = iterate_lin(self.hue,self.stepsize,self.nled/2)
        self.step_hue()
        msg = []
        msg_mirror = []
        for i in val:
            rgb = [ int((j*self.max)+0.5)
                    for j in colorsys.hsv_to_rgb(i, 1, 1) ]
            msg += [ rgb[0], rgb[1], rgb[2] ]
            msg_mirror = [ rgb[0], rgb[1], rgb[2] ] + msg_mirror
        return clamp(msg+msg_mirror)
    
def create_parser():
    from esp8266leds.RainbowCommon import create_parser as cp
    return cp()

def instance(args):
    return RainbowMirror(args)
