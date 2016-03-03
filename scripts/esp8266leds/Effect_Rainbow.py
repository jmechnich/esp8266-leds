import math, colorsys

from esp8266leds.RainbowCommon import clamp, iterate_lin

class Rainbow(object):
    def __init__(self,args):
        self.max      = int(args.max)
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
        val = iterate_lin(self.hue,self.stepsize,self.nled)
        self.step_hue()
        msg = []
        for i in val:
            msg += [ int((j*self.max)+0.5)
                     for j in colorsys.hsv_to_rgb(i, 1, 1) ]
        return clamp(msg)

def create_parser():
    from esp8266leds.RainbowCommon import create_parser as cp
    return cp()

def instance(args):
    return Rainbow(args)
