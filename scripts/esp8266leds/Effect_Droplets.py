import random, scipy.signal, colorsys

class Droplet(object):
    def __init__(self,args):
        self.nled = args.nled
        self.hue = random.random() * args.huespread + args.color
        self.center = random.random() * 0.1
        self.radius = random.randint(2, 8)
        self.time_to_live = random.randint(80, 150)
        self.speed = random.random() / 80
        self.valid = True
        self.values = list(scipy.signal.gaussian(self.radius * 2 + 1, self.radius / 2.0))
        self.iteration = 0
        
    def fade(self):
        v = float(self.iteration) / self.time_to_live
        scaling = (0.5 - abs(v - 0.5))*2.0
        
        if not self.valid:
            scaling = 0
            
        values = [x * scaling for x in self.values]
        
        self.center = (self.center + self.speed) % 1
        
        self.iteration += 1
        if self.iteration == self.time_to_live:
            self.valid = False
        return values

    def begin(self):
        return int(self.center * self.nled) - self.radius
    
    def end(self):
        return int(self.center * self.nled) + self.radius + 1
    
class Droplets(object):
    def __init__(self,args):
        self.args = args
        self.nled        = int(args.nled)
        self.probability = float(args.probability)
        self.max         = int(args.max_droplets)
        self.droplets = []

    def iterate(self):

        colors = [0, 0, 0] * self.nled

        if len(self.droplets) < self.max and \
           random.random() < self.probability:
            self.droplets.append(Droplet(self.args))
        
        garbage = list()
        for idx, droplet in enumerate(self.droplets):
            if not droplet.valid:
                garbage.append(idx)
            
            values = droplet.fade()
            pos = droplet.begin()
            if pos < 0:
                values = values[abs(pos):]
                pos = 0
            if droplet.end() > self.nled:
                values = values[:-(droplet.end() - self.nled)]

            for i, val in enumerate(values):
                rgb = colorsys.hsv_to_rgb(droplet.hue, 1, val)
                idx = (pos + i) * 3
                colors[idx  ] += rgb[0]
                colors[idx+1] += rgb[1]
                colors[idx+2] += rgb[2]

        for idx in sorted(garbage, reverse=True):
            self.droplets.pop(idx)
        msg = list(colors) 
        return msg

def create_parser():
    from argparse import ArgumentParser, SUPPRESS
    from esp8266leds.Common import arg_range, arg_positive
    parser = ArgumentParser(add_help=False, usage=SUPPRESS,
                            description="Effect options:")
    parser.add_argument("--huespread", default=0.12, type=arg_positive(float),
                        help="spread of random hue values around 'color'" \
                        " (default: %(default)s)")
    parser.add_argument("--max_droplets", default=3, type=arg_positive(),
                        help="maximum number of droplets" \
                        " (default: %(default)s)")
    parser.add_argument("--probability", default=0.5,
                        type=arg_positive(float),
                        help="probability of creating a new droplet" \
                        " (default: %(default)s)")
    return parser

def instance(args):
    return Droplets(args)
