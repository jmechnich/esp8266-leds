#!/usr/bin/env python

import subprocess, sys, time, math, colorsys

class Rainbow(object):
    def __init__(self,nleds,max,stepsize=math.pi/256.,hue=0):
        self.max      = max
        self.nleds    = nleds
        self.hsv      = [hue,1,1]
        self.stepsize = stepsize
    
    def iterateLin(self):
        return [ self.hsv[0]+i*self.stepsize for i in xrange(self.nleds) ]
    def iterateSin(self):
        return [ abs(math.sin(self.hsv[0]+i*self.stepsize))
                 for i in xrange(self.nleds) ]
    def iterateSin2(self):
        return [ math.pow(math.sin(self.hsv[0]+i*self.stepsize), 2)
                 for i in xrange(self.nleds) ]
    def iterate(self):
        val = self.iterateLin()
        self.hsv[0] += self.stepsize
        while self.hsv[0]+self.nleds*self.stepsize > 1: self.hsv[0] -= 1
        while self.hsv[0] < 0: self.hsv[0] += 1
        msg = []
        for i in val:
            msg += [ int(j*self.max)
                     for j in colorsys.hsv_to_rgb(i, *(self.hsv[1:3]))]
        return msg

class LEDClient(object):
    def __init__(self,nled,host,port=1883,pin=1,max=0xf,stepsize=math.pi/1024.,
                 verbose=False,hue=0):
        self.nled      = nled
        self.mqtt_host = host
        self.mqtt_port = port
        self.pin       = pin
        self.max       = max
        self.stepsize  = stepsize
        self.verbose   = verbose
        self.hue       = hue
        self.rb        = Rainbow(self.nled,self.max,stepsize=self.stepsize,
                                 hue=self.hue)

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
        
    def send_raw(self,data,topic="leddata",device="huzzah"):
        if self.verbose:
            print "Sending data to %s:%d, topic %s/in/%s, length %d" % \
                (self.mqtt_host,self.mqtt_port,device,topic,len(data))
        cmdline = "mosquitto_pub -h %s -p %d -s -t %s/in/%s" % \
                  (self.mqtt_host,self.mqtt_port,device,topic)
        p = subprocess.Popen(cmdline.split(),stdin=subprocess.PIPE)
        p.communicate(data)
        p.wait()
        
    def send_cmd(self,cmd):
        return self.send_raw(cmd,topic="cmd")

    def off(self):
        self.send_cmd("ws2812.writergb(%d,string.char(0):rep(%d))" % \
                      (self.pin,self.nled*3))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("host", default="localhost", type=str, nargs="?",
                        help="mptt host (default: %(default)s)")
    parser.add_argument("port", default=1883, type=int, nargs="?",
                        help="mptt port (default: %(default)s)")
    parser.add_argument("-c", "--color", default=0, type=float,
                        help="set start color (hue), range 0-1 (default: %(default)s)")
    parser.add_argument("-d", "--device", default="huzzah", type=str,
                        help="device name (default: %(default)s)")
    parser.add_argument("-m", "--max", default=50, type=int,
                        help="maximum brightness (default: %(default)s)")
    parser.add_argument("-n", "--nled", default=120, type=int,
                        help="set number of leds (default: %(default)s)")
    parser.add_argument("-o", "--off", action="store_true",
                        help="set leds off and exit")
    parser.add_argument("-p", "--pin", default=1, type=int,
                        help="set led pin number (default: %(default)s)")
    parser.add_argument("-s", "--stepsize", default=math.pi/1024., type=float,
                        help="rainbow color stepsize (default: math.pi/1024)")
    parser.add_argument("-t", "--time", default=1., type=float,
                        help="time between changes (default: %(default)s)")
    parser.add_argument("-v", "--verbose", help="verbose output",
                        action="store_true")
    args = parser.parse_args()
    l = LEDClient(host=args.host,port=args.port,nled=args.nled,pin=args.pin,
                  max=args.max,stepsize=args.stepsize,verbose=args.verbose,
                  hue=abs(args.color-int(args.color)))
    try:
        while not args.off:
            l.iterate_rb_mirror()
            time.sleep(args.time)
        else:
            l.off()
    except KeyboardInterrupt:
        pass
    print

