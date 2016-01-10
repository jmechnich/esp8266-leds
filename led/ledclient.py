#!/usr/bin/env python

import subprocess, sys, time, math, colorsys

class Rainbow(object):
    def __init__(self,nleds,max,stepsize=math.pi/256.):
        self.max      = max
        self.nleds    = nleds
        self.hsv      = [0,1,1]
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
    def __init__(self,nled,host,port=1883,pin=1,max=0xf,stepsize=math.pi/1024.):
        self.nled      = nled
        self.mqtt_host = host
        self.mqtt_port = port
        self.pin       = pin
        self.max       = max
        self.stepsize  = stepsize
        self.rb        = Rainbow(self.nled,self.max,self.stepsize)

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
    l = LEDClient(host="localhost",nled=120,pin=1,max=50)
    l.off()
    while True:
        l.iterate_rb_mirror()
        time.sleep(1)
