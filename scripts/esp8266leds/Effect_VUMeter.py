# A VU meter effect 
# Adapted from http://www.howtoguides.co.uk/Raspberry_Pi_VU_meter.html

import pyaudio, audioop, math
from itertools import chain
import esp8266leds.Conversion as cu

# set up a bunch of constants 
PeakL = 0
PeakR = 0

# setup code
pa = pyaudio.PyAudio()

info = pa.get_default_input_device_info()
RATE = int(info['defaultSampleRate'])

class AudioSource(object):

    def __init__(self):

        self.LevelL   = 0
        self.LevelR   = 0
        self.stream   = pa.open(format = pyaudio.paInt16,
                        channels = 2,
                        rate = RATE,
                        input = True,
                        stream_callback=self.audioReceived)


    def audioReceived(self,in_data, frame_count, time_info, status):

        def getLevel(in_data, leftChannel=True):
            normalize   = 32767.0
            leftFactor  = 1 if leftChannel else 0
            rightFactor = 1 if not leftChannel else 0
            data        = audioop.tomono(in_data, 2, leftFactor, rightFactor)
            amplitudel  = ((audioop.max(data, 2))/normalize)
            level       = (int(41+(20*(math.log10(amplitudel+(1e-40))))))
            return level

        self.LevelL = max(getLevel(in_data, leftChannel=True),0)
        self.LevelR = max(getLevel(in_data, leftChannel=False),0)

        return in_data, pyaudio.paContinue


class VUMeter(object):

    def __init__(self,args):

        self.args     = args
        self.nled     = int(args.nled)
        hue_start     = args.huestart
        hue_end       = args.hueend
        hue_values    = [ hue_start + ( (hue_end-hue_start) / float(self.nled) ) * x  for x in range(self.nled)]
        self.texture  = list(chain.from_iterable((hue, 1.0, 1.0) for hue in hue_values))
        self.begin    = 0
        self.end      = 41
        self.source   = AudioSource()
        cu.convert(self.texture,[cu.toRGB])


    def iterate(self):

        LevelRPercent = (self.source.LevelR-self.begin) / float(self.end-self.begin)
        LevelRIdx     = int((LevelRPercent * self.nled)+0.5) * 3
        return self.texture[:LevelRIdx] + ([0] * (self.nled * 3 - LevelRIdx)) 


def create_parser():

    from argparse import ArgumentParser, SUPPRESS
    from esp8266leds.Common import arg_range, arg_positive
    parser = ArgumentParser(add_help=False, usage=SUPPRESS,
                            description="Effect options:")
    parser.add_argument("--huestart", default=0.24, type=arg_positive(float),
                        help="Starting color for VU meter (the color on the bottom)" \
                        " (default: %(default)s)")
    parser.add_argument("--hueend", default=0.0, type=arg_positive(float),
                        help="End color for VU meter (the color on the top)" \
                        " (default: %(default)s)")
    return parser


def instance(args):

    return VUMeter(args)

