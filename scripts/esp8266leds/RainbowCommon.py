import math

def clamp(l):
    return [ max(0,min(255,i)) for i in l ]

def iterate_lin(hue,stepsize,n):
    return [ hue+i*stepsize for i in xrange(n) ]

def iterate_sin(hue,stepsize,n):
    return [ (math.sin(hue+i*stepsize)*0.5)+1
             for i in xrange(n) ]

def iterate_sin2(hue,stepsize,n):
    return [ math.pow(math.sin(hue+i*stepsize), 2)
             for i in xrange(n) ]

def create_parser():
    from argparse import ArgumentParser, SUPPRESS
    from esp8266leds.Common import arg_range, arg_positive
    parser = ArgumentParser(add_help=False, usage=SUPPRESS,
                            description="Effect options:")
    parser.add_argument("-m", "--max", default=50, type=arg_range(0,255),
                        help="maximum brightness, range 0-255" \
                        " (default: %(default)s)")
    parser.add_argument("-s", "--stepsize", default=math.pi/1024.,
                        type=arg_positive(float),
                        help="rainbow color stepsize (default: math.pi/1024)")
    return parser
