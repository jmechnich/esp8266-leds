# Adapted from http://pastebin.com/xYEpxqgq
# Fire2012: a basic fire simulation for a one-dimensional string of LEDs
# Mark Kriegsman, July 2012.

# Fire2012 by Mark Kriegsman, July 2012
# as part of "Five Elements" shown here: http://youtu.be/knWiGsmgycY
#
# This basic one-dimensional 'fire' simulation works roughly as follows:
# There's a underlying array of 'heat' cells, that model the temperature
# at each point along the line.  Every cycle through the simulation, 
# four steps are performed:
#  1) All cells cool down a little bit, losing heat to the air
#  2) The heat from each cell drifts 'up' and diffuses a little
#  3) Sometimes randomly new 'sparks' of heat are added at the bottom
#  4) The heat from each cell is rendered as a color into the leds array
#     The heat-to-color mapping uses a black-body radiation approximation.

# Temperature is in arbitrary units from 0 (cold black) to 255 (white hot).

# This simulation scales it self a bit depending on NUM_LEDS; it should look
# "OK" on anywhere from 20 to 100 LEDs without too much tweaking. 

# I recommend running this simulation at anywhere from 30-100 frames per second,
# meaning an interframe delay of about 10-35 milliseconds.

# There are two main parameters you can play with to control the look and
# feel of your fire: COOLING and SPARKING.

# COOLING: How much does the air cool as it rises?
# Less cooling = taller flames.  More cooling = shorter flames.
# Default 55, suggested range 20-100 

# SPARKING: What chance (out of 255) is there that a new spark will be lit?
# Higher chance = more roaring fire.  Lower chance = more flickery fire.
# Default 120, suggested range 50-200.

from esp8266leds.Conversion     import convert, toUnit

class Fire2012(object):
    def __init__(self,args):
        self.nled     = args.nled
        self.cooling  = args.cooling
        self.sparking = args.sparking
        self.heat     = [0] * args.nled

    def iterate(self):
        import random
        for i in xrange(self.nled):
            self.heat[i] = max(0, self.heat[i]-random.randint(
                0,((self.cooling * 10) / self.nled) + 2))

        for k in xrange(self.nled-3,1,-1):
            self.heat[k] = (self.heat[k-1] + self.heat[k-2] + self.heat[k-2]) / 3

        if random.randint(0,255) < self.sparking:
            y = random.randint(0,6)
            self.heat[y] = min(255,self.heat[y]+random.randint(160,254))

        leds = []
        for j in xrange(self.nled):
            leds += [ (255*i)>>8 for i in HeatColor(self.heat[j]) ]
        convert( leds, [toUnit] )
        return leds

def HeatColor(temperature):
    t192 = (temperature*192)>>8
    
    heatramp = t192 & 0x3F  # 0..63
    heatramp <<= 2          # scale up to 0..252
 
    # now figure out which third of the spectrum we're in:
    if t192 & 0x80:
        # we're in the hottest third
        r = 255      # full red
        g = 255      # full green
        b = heatramp # ramp up blue
    elif t192 & 0x40:
        # we're in the middle third
        r = 255      # full red
        g = heatramp # ramp up green
        b = 0        # no blue
    else:
        # we're in the coolest third
        r = heatramp # ramp up red
        g = 0        # no green
        b = 0        # no blue
    return [r,g,b]

def create_parser():
    from argparse import ArgumentParser, SUPPRESS
    from esp8266leds.Common import arg_range, arg_positive
    parser = ArgumentParser(add_help=False, usage=SUPPRESS,
                            description="Effect options:")
    parser.add_argument("--cooling", default=55,
                        type=arg_range(20,100),
                        help="less cooling = taller flames (default: %(default)s)")
    parser.add_argument("--sparking", default=120,
                        type=arg_range(50,200),
                        help="probability of creating new sparks (default: %(default)s)")
    return parser

def instance(args):
    return Fire2012(args)
