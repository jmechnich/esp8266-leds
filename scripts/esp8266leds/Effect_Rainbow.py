import math
from itertools import chain

from esp8266leds.RainbowCommon import iterate_lin
import esp8266leds.Conversion as cu


class Rainbow(object):
    def __init__(self,args):
        self.max      = float(args.max)
        self.nled     = int(args.nled)
        self.stepsize = float(args.stepsize)
        self.hue      = float(args.color)
        self.norm_hue()
    
    def step_hue(self):
        self.hue += self.stepsize
        self.norm_hue()
        
    def norm_hue(self):
        while self.hue > 1: self.hue -= 1
        while self.hue < 0: self.hue += 1
    
    def iterate(self):
        msg = iterate_lin(self.hue,self.stepsize,self.nled)
        msg = list(chain.from_iterable((hue, 1.0, 1.0) for hue in msg))
        self.step_hue()
        cu.convert(msg,[cu.toRGB])
        return msg

def create_parser():
    from esp8266leds.RainbowCommon import create_parser as cp
    return cp()

def instance(args):
    return Rainbow(args)
