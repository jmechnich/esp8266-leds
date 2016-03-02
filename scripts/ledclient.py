#!/usr/bin/env python

import subprocess, sys, time, math, colorsys

def clamp(l):
    return [ max(0,min(255,i)) for i in l ]

class Rainbow(object):
    def __init__(self,nleds,max,stepsize=math.pi/256.,hue=0,grb=False):
        self.max      = int(max)
        self.nleds    = int(nleds)
        self.stepsize = float(stepsize)
        self.hue      = float(hue)
        while self.hue > 1: self.hue -= 1
        while self.hue < 0: self.hue += 1
        self.grb      = grb
    
    def stepHue(self):
        self.hue += self.stepsize
        while self.hue > 1: self.hue -= 1
        while self.hue < 0: self.hue += 1
    
    def iterateLin(self):
        return [ self.hue+i*self.stepsize for i in xrange(self.nleds) ]
    
    def iterateSin(self):
        return [ (math.sin(self.hue+i*self.stepsize)*0.5)+1
                 for i in xrange(self.nleds) ]
    
    def iterateSin2(self):
        return [ math.pow(math.sin(self.hue+i*self.stepsize), 2)
                 for i in xrange(self.nleds) ]
    
    def iterate(self):
        val = self.iterateLin()
        self.stepHue()
        msg = []
        for i in val:
            rgb = [ int((j*self.max)+0.5)
                    for j in colorsys.hsv_to_rgb(i, 1, 1) ]
            if self.grb:
                msg += [ rgb[1], rgb[0], rgb[2] ]
            else:
                msg += [ rgb[1], rgb[0], rgb[2] ]
        return clamp(msg)
    
    def iterate_single(self):
        self.stepHue()
        rgb = [ int((j*self.max)+0.5)
                for j in colorsys.hsv_to_rgb(self.hue,1,1) ]
        if self.grb:
            tmp = rgb[0]
            rgb[0] = rgb[1]
            rgb[1] = tmp
        return clamp(rgb)
    
class LEDClient(object):
    def __init__(self,nled,host,port=1883,pin=1,max=0xf,stepsize=math.pi/1024.,
                 verbose=False,hue=0,proto='mqtt'):
        self.nled      = int(nled)
        self.host      = str(host)
        self.port      = int(port)
        self.pin       = int(pin)
        self.max       = int(max)
        self.stepsize  = float(stepsize)
        self.verbose   = bool(verbose)
        self.hue       = float(hue)
        self.proto     = str(proto)

        grb = False
        if self.proto != 'mqtt':
            import socket
            self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        else:
            self.sock = None
            grb = True

        self.rb        = Rainbow(self.nled,self.max,stepsize=self.stepsize,
                                 hue=self.hue,grb=grb)

    
    def iterate_rb_blend(self):
        r,g,b = self.rb.iterate_single()
        if self.proto == 'mqtt':
            self.send_cmd("ws2812.writergb(%d,string.char(%d,%d,%d):rep(%d))" % \
                          (self.pin,r,g,b,self.nled))
        else:
            self.send_raw(bytearray([r,g,b])*self.nled)
            
    def iterate_rb_full(self):
        self.send_raw(bytearray(self.rb.iterate()))
    
    def iterate_rb_mirror(self):
        pix = self.rb.iterate()
        pix_half = pix[:len(pix)/2]
        pix_rev = []
        tmp = []
        count = 0
        for i in reversed(pix_half):
            tmp.append(i)
            count += 1
            if count == 3:
                tmp.reverse()
                pix_rev += tmp
                tmp = []
                count = 0
        self.send_raw(bytearray(pix_half+pix_rev))
    
    def send_raw_mqtt(self,data,topic="leddata",device="huzzah"):
        if self.verbose:
            print "Sending data to %s:%d, topic %s/in/%s, length %d" % \
                (self.host,self.port,device,topic,len(data))
        cmdline = "mosquitto_pub -h %s -p %d -s -t %s/in/%s" % \
                  (self.host,self.port,device,topic)
        p = subprocess.Popen(cmdline.split(),stdin=subprocess.PIPE)
        p.communicate(data)
        p.wait()
    
    def send_raw(self,data,topic="leddata",device="huzzah"):
        if self.proto == 'mqtt':
            self.send_raw_mqtt(data,topic,device)
        else:
            if topic != "leddata": return
            self.sock.sendto(bytearray('abc') + data,(self.host,self.port))
            
    def send_cmd(self,cmd):
        return self.send_raw(cmd,topic="cmd")
    
    def off(self):
        if self.proto == 'mqtt':
            self.send_cmd("ws2812.writergb(%d,string.char(0):rep(%d))" % \
                          (self.pin,self.nled*3))
        else:
            self.send_raw(bytearray(self.nled*3))
            
if __name__ == "__main__":
    effects = {
        'rainbow':        lambda x: x.iterate_rb_full(),
        'rainbow_mirror': lambda x: x.iterate_rb_mirror(),
        'rainbow_blend':  lambda x: x.iterate_rb_blend(),
    }
    
    import argparse
    def arg_range(first,last,arg_type=int):
        def f(string):
            value = arg_type(string)
            if value < first or value > last:
                raise argparse.ArgumentTypeError(
                    "value out of range: %s < value < %s" %
                    (str(first),str(last)))
            return value
        return f
    
    def arg_positive(arg_type=int):
        def f(string):
            value = arg_type(string)
            if value < 0:
                raise argparse.ArgumentTypeError("value must be positive")
            return value
        return f
    
    parser = argparse.ArgumentParser()
    parser.add_argument("host", default="localhost", type=str, nargs="?",
                        help="host (default: %(default)s)")
    parser.add_argument("port", default=1883, type=int, nargs="?",
                        help="port (default: %(default)s)")
    parser.add_argument("-c", "--color", default=0, type=arg_range(0,1,float),
                        help="set start color (hue), range 0-1" \
                        " (default: %(default)s)")
    parser.add_argument("-d", "--device", default="huzzah", type=str,
                        help="device name (default: %(default)s)")
    parser.add_argument("-e", "--effect", choices=sorted(effects.keys()),
                        default="rainbow_mirror",
                        help="select effect (default: %(default)s)")
    parser.add_argument("-m", "--max", default=50, type=arg_range(0,255),
                        help="maximum brightness, range 0-255" \
                        " (default: %(default)s)")
    parser.add_argument("-n", "--nled", default=120, type=arg_positive(),
                        help="set number of leds (default: %(default)s)")
    parser.add_argument("-o", "--off", action="store_true",
                        help="set leds off and exit")
    parser.add_argument("-p", "--pin", default=1, type=int,
                        help="set led pin number (default: %(default)s)")
    parser.add_argument("-r", "--rtype", default="mqtt", type=str,
                        choices=["mqtt","udp"],
                        help="set remote host type")
    parser.add_argument("-s", "--stepsize", default=math.pi/1024.,
                        type=arg_positive(float),
                        help="rainbow color stepsize (default: math.pi/1024)")
    parser.add_argument("-t", "--time", default=1., type=arg_positive(float),
                        help="time between changes in seconds" \
                        " (default: %(default)s)")
    parser.add_argument("-v", "--verbose", help="verbose output",
                        action="store_true")
    args = parser.parse_args()
    l = LEDClient(host=args.host,port=args.port,nled=args.nled,pin=args.pin,
                  max=args.max,stepsize=args.stepsize,verbose=args.verbose,
                  hue=abs(args.color-int(args.color)),proto=args.rtype)
    try:
        while not args.off:
            effects[args.effect](l)
            time.sleep(args.time)
        else:
            l.off()
    except KeyboardInterrupt:
        pass
    print
