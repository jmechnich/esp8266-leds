#!/usr/bin/env python

import math, time, argparse, sys, os

from esp8266leds.Common     import arg_range, arg_positive
from esp8266leds.LEDClient  import LEDClient
from esp8266leds            import Effect
from esp8266leds.Conversion import convert, gamma, toByte, clamp, toHSV, toRGB, multiply

def read_configfile(filename,verbose=False):
    cmdargs = []
    if not os.path.exists(filename):
        if verbose:
            print "Could not open configfile '%s', skipping" % filename
        return cmdargs
    
    if verbose:
        print "Reading configuration from file '%s'" % filename

    with open(filename) as f:
        for line in f.readlines():
            line = line.strip()
            if len(line) == 0 or line.startswith('#'): continue
            arg = [ a.strip() for a in line.split('=') ]
            cmdargs.append('--' + arg[0])
            cmdargs.append(arg[1])
    return cmdargs

if __name__ == "__main__":
    progname = os.path.splitext(os.path.basename(sys.argv[0]))[0]
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
                        type=str, help="set config file path")
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
    parser.add_argument("-o", "--off", default=None, const=True, nargs='?',
                        type=bool, help="set leds off and exit")
    parser.add_argument("--offatexit", default=None, const=True, nargs='?',
                        type=bool, help="set leds off at exit")
    parser.add_argument("--pin", default=1, type=int,
                        help="set led pin number (default: %(default)s)")
    parser.add_argument("-r", "--rtype", default="mqtt", type=str,
                        choices=["mqtt","udp"],
                        help="set remote host type")
    parser.add_argument("-m", "--max", default=0.4, type=arg_range(0,1,arg_type=float),
                        help="maximum brightness, range 0-1" \
                        " (default: %(default)s)")
    parser.add_argument("--gamma", default=2.2, type=float,
                        help="gamma value" \
                        " (default: %(default)s)")
    parser.add_argument("-t", "--time", default=1., type=arg_positive(float),
                        help="time between changes in seconds" \
                        " (default: %(default)s)")
    parser.add_argument("-v", "--verbose", default=None, const=True, nargs='?',
                        type=bool, help="verbose output")
    parser.add_argument("--help", action="store_true")

    
    args, unparsed_args = parser.parse_known_args()
    if args.config:
        cmdargs = read_configfile(args.config,verbose=args.verbose)
    else:
        cmdargs = read_configfile('/etc/%s.conf' % progname, verbose=args.verbose)
        cmdargs += read_configfile(os.path.join(os.path.expanduser("~"),'.%s.conf' % progname),verbose=args.verbose)

    #print cmdargs, sys.argv[1:]
    args, unparsed_args = parser.parse_known_args(cmdargs + sys.argv[1:])
    #print args, unparsed_args
    
    if args.effect:
        argparse.ArgumentParser(add_help=False)
        effect_module = Effect.load(args.effect)
        effect_parser = effect_module.create_parser()
        effect_args, unparsed_effect_args = effect_parser.parse_known_args(
            unparsed_args)
        if args.verbose and len(unparsed_effect_args):
            print "Ignoring arguments", unparsed_effect_args
        args.__dict__.update(vars(effect_args))
    elif args.verbose and len(unparsed_args):
        print "Ignoring arguments", unparsed_args
        
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
            convert(data,[toHSV, multiply((1,1,args.max)), toRGB, gamma(args.gamma),toByte,clamp(0,255)])
            l.send(data)
            time.sleep(args.time)
            
    except KeyboardInterrupt:
        pass

    if args.offatexit:
        l.off()
