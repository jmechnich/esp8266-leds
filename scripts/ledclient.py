#!/usr/bin/env python

import math, time, argparse, sys, os

from esp8266leds.Common     import arg_range, arg_positive
from esp8266leds.LEDClient  import LEDClient
from esp8266leds            import Effect
from esp8266leds.Conversion import convert, toNonLinear, toByte, clamp

def read_configfile(args):
    # Look for configuration file
    cmdargs = []
    try:
        with open(args.config) as f:
            if args.verbose:
                print "Reading configuration from file '%s'" % args.config
            for line in f.readlines():
                line = line.strip()
                if len(line) == 0 or line.startswith('#'): continue
                arg = [ a.strip() for a in line.split('=') ]
                if len(arg) != 2:
                    print "Error parsing command line argument from configfile:", line
                    continue
                cmdargs.append('--' + arg[0])
                cmdargs.append(arg[1])
    except IOError, e:
        pass
    cmdargs += sys.argv[1:]
    return cmdargs

if __name__ == "__main__":
    effects = Effect.list_all()
    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument("-h", "--host", default="localhost", type=str,
                        nargs="?",
                        help="host (default: %(default)s)")
    parser.add_argument("-p", "--port", default=1883, type=int, nargs="?",
                        help="port (default: %(default)s)")
    parser.add_argument("-c", "--color", default=0, type=arg_range(0,1,float),
                        help="set start color/hue, range 0-1" \
                        " (default: %(default)s)")
    parser.add_argument("--config",
                        default=os.path.join( os.path.expanduser('~'),
                                              '.esp8266leds'),
                        type=str, help="set config file path" \
                        " (default: %(default)s)")
    parser.add_argument("-d", "--device", default="huzzah", type=str,
                        help="device name (default: %(default)s)")
    parser.add_argument("-e", "--effect", default="Rainbow", choices=effects,
                        help="effect name (default: %(default)s)")
    parser.add_argument("-g", "--grb", action="store_true",
                        help="use GRB order")
    parser.add_argument("--mirror", action="store_true",
                        help="mirror effect at half of the strip")
    parser.add_argument("-n", "--nled", default=120, type=arg_positive(),
                        help="set number of leds (default: %(default)s)")
    parser.add_argument("-o", "--off", action="store_true",
                        help="set leds off and exit")
    parser.add_argument("--pin", default=1, type=int,
                        help="set led pin number (default: %(default)s)")
    parser.add_argument("-r", "--rtype", default="mqtt", type=str,
                        choices=["mqtt","udp"],
                        help="set remote host type")
    parser.add_argument("-t", "--time", default=1., type=arg_positive(float),
                        help="time between changes in seconds" \
                        " (default: %(default)s)")
    parser.add_argument("-v", "--verbose", help="verbose output",
                        action="store_true")
    parser.add_argument("--help", action="store_true")

    args, unparsed_args = parser.parse_known_args()
    args, unparsed_args = parser.parse_known_args(read_configfile(args))
    if args.effect:
        argparse.ArgumentParser(add_help=False)
        effect_module = Effect.load(args.effect)
        effect_parser = effect_module.create_parser()
        effect_args, unparsed_effect_args = effect_parser.parse_known_args(
            unparsed_args)
        if args.verbose and len(unparsed_effect_args):
            print "Ignoring arguments", unparsed_effect_args
        args.__dict__.update(vars(effect_args))
    
    if args.help:
        parser.print_help()
        if args.effect:
            print
            effect_parser.print_help()
        sys.exit(0)

    if args.verbose:
        print "Settings:"
        for i in sorted(vars(args).iteritems()):
            print "  %10s: %s" % i
        print
            
    l = LEDClient(args)
    if args.mirror:
        args.nled /= 2
    e = effect_module.instance(args)
    try:
        if args.off:
            if args.verbose:
                print "Switching LEDs off"
            l.off()
            sys.exit(0)
            
        if args.verbose:
            print "Starting effect '%s'" % args.effect
        while True:
            data = e.iterate()
            convert(data,[toNonLinear,toByte,clamp(0,255)])
            if args.mirror:
                data = data + [ i for i in reversed(data) ]
                for i in xrange(args.nled*3,6*args.nled,3):
                    data[i], data[i+2] = data[i+2], data[i]
            l.send_raw(bytearray(data))
            time.sleep(args.time)
            
    except KeyboardInterrupt:
        pass
    print
