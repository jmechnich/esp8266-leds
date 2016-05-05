from esp8266leds.Effect_Rainbow import Rainbow
from esp8266leds.RainbowCommon  import iterate_lin, clamp
import esp8266leds.Conversion as cu

class RainbowSingle(Rainbow):
    def __init__(self,args):
        super(RainbowSingle,self).__init__(args)

    def iterate(self):
        self.step_hue()
        rgb = [self.hue,1,self.max/255.0]
        cu.convert(rgb,[cu.toRGB ,cu.toByte])
        return clamp(rgb*self.nled)

def create_parser():
    from esp8266leds.RainbowCommon import create_parser as cp
    return cp()

def instance(args):
    return RainbowSingle(args)
