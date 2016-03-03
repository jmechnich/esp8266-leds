import math,subprocess

class LEDClient(object):
    def __init__(self,args):
        self.nled      = int(args.nled)
        self.host      = str(args.host)
        self.port      = int(args.port)
        self.pin       = int(args.pin)
        self.verbose   = bool(args.verbose)
        self.proto     = str(args.rtype)

        if self.proto != 'mqtt':
            import socket
            self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        else:
            self.sock = None
    
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
