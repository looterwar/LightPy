import sys
sys.path.append('/home/pi/LightPy/Animations')
from neopixel import *
from LedAnimation import Animation
from blinker import signal
from Fade import FadeAnimation
from Wipe import WipeAnimation
from RandBuild import RandBuildAnimation
from Split import SplitAnimation
from Bounce import BounceAnimation
import ConfigReader
import BrightnessController

class LedController:

    def __init__(self, useConfig=True, count=0, pin=18, frq=800000, dma=5, brightness=200, invert=False, channel=0):
        
        if (useConfig):
            self.cfg = ConfigReader.GetConfig()
            self.count = self.cfg['strip']['count']
            self.pin = self.cfg['strip']['pin']
            self.frq = self.cfg['strip']['frq']
            self.dma = self.cfg['strip']['dma']
            self.brightness = self.cfg['strip']['brightness']
            self.invert = self.cfg['strip']['invert']
            self.channel = self.cfg['strip']['channel']
            self.activeColor = Color(self.cfg['strip']['active_color']['R'], self.cfg['strip']['active_color']['G'], self.cfg['strip']['active_color']['B'])
        else:
            self.count = count
            self.pin = pin
            self.frq = frq
            self.dma = dma
            self.brightness = brightness
            self.invert = invert
            self.channel = channel
            self.activeColor = Color(60,60,90)
            
        self.type = ws.WS2811_STRIP_GRB
        self.strip = Adafruit_NeoPixel(self.count, self.pin, self.frq, self.dma, self.invert, self.brightness, self.channel, ws.WS2811_STRIP_GRB)
        self.strip.begin()

        self.BrightnessController = BrightnessController.BrightnessController()
        self.SetBrightness()

        self.RegisterAnimations()
        self.AnimationCompleteEvent = signal('anim_complete')

    def RegisterAnimations(self):
        self.StartAnimations = {}
        self.StartAnimations['Fade'] = FadeAnimation(self.brightness, self.activeColor).FadeIn(self.strip)
        self.StartAnimations['FadeColours'] = FadeAnimation(self.brightness).FadeColoursIn(self.strip, [Color(0,0,255), Color(255,0,0)])
        self.StartAnimations['FadeRandIn'] = FadeAnimation(self.brightness, self.activeColor).FadeRandIn(self.strip, 3)
        self.StartAnimations['Wipe'] = WipeAnimation(self.brightness, self.activeColor).WipeIn(self.strip, 0, self.activeColor)
        self.StartAnimations['WipeRand'] = WipeAnimation(self.brightness, self.activeColor).WipeRandIn(self.strip)
        #self.StartAnimations['RandBuild'] = RandBuildAnimation(self.brightness, self.activeColor).BuildIn(self.strip, self.activeColor)
        #self.StartAnimations['Split'] = SplitAnimation().Split(self.strip)
        #self.StartAnimations['SplitRand'] = SplitAnimation().SplitRand(self.strip)
        #self.StartAnimations['Bounce'] = BounceAnimation().Bounce(self.strip)
        #self.StartAnimations['BounceRand'] = BounceAnimation().BounceRand(self.strip)

        self.EndAnimations = {}
        self.EndAnimations['Fade'] = FadeAnimation(self.brightness, self.activeColor).FadeOut(self.strip)

        for v in self.StartAnimations.itervalues():
            v.AnimationComplete.connect(self.AnimationComplete)

        for v in self.EndAnimations.itervalues():
            v.AnimationComplete.connect(self.AnimationComplete)

    def AnimationComplete(self, sender):
        self.SetBrightness()
        self.RegisterAnimations() # Reset animations to allow restart of sub threads (not best performace but meh)
        self.AnimationCompleteEvent.send()

    def SetBrightness(self):
        #self.brightness = self.BrightnessController.CalculateBrightness()
        self.brightness
        self.strip.setBrightness(self.brightness)

    def On(self):
        for j in range(self.strip.numPixels()):
            self.strip.setPixelColor(j, Color(0,0,255))
        self.strip.setBrightness(90)
        self.strip.show()

    def Off(self):
        for j in range(self.strip.numPixels()):
            self.strip.setPixelColor(j, Color(0,0,0))
        self.strip.show()

    def StopAnimation(self):
        self.Animator.Stop()