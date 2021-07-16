import datetime
import csv
import time, serial
import ADS1256
import RPi.GPIO as GPIO

limite = 0.5

class VentilatorParams():
    def __init__(self):
        self.pressure = 0.0
        self.flow = 0.0
        self.oxygen = 0.0
        self.flow_last = 0.0
        self.volume = 0.0
        self.pip = {'current': None, 'auxiliar': None}
        self.peep = {'current': None, 'auxiliar': None}
        self.ti = {'current': None, 'last': None, 'new': None}
        self.te = {'current': None, 'last': None, 'new': None}
        self.ie = {'current': None, 'new_calculation': True}
        self.bpm = {'current': None, 'new_calculation': True}
        self.pif = {'current': None, 'auxiliar': None}
        self.vti = {'current': None, 'auxiliar': None}
        self.time = 0.0
    
    def calculatePIP(self):
        if self.flow > limite:
            if self.pip['auxiliar'] is None:
                self.pip['auxiliar'] = self.pressure
                
            elif self.pressure > self.pip['auxiliar']:
                self.pip['auxiliar'] = self.pressure
        
        elif self.flow <= limite and self.pip['auxiliar'] is not None:
            self.pip['current'] = self.pip['auxiliar']
            self.pip['auxiliar'] = None
        
    def calculatePEEP(self):        
        if self.flow <= limite:
            if self.peep['auxiliar'] is None:
                self.peep['auxiliar'] = self.pressure
                
            elif self.pressure < self.peep['auxiliar']:
                self.peep['auxiliar'] = self.pressure
        
        elif self.flow > limite and self.peep['auxiliar'] is not None:
            self.peep['current'] = self.peep['auxiliar']
            self.peep['auxiliar'] = None
            
    def calculateTI(self):
        if self.flow > limite and self.ti['last'] is None:
            self.ti['last'] = int(round(time.time()*1000))
            self.ti['new'] = None
            
        elif self.flow <= limite and self.ti['new'] is None and self.ti['last'] is not None:
            self.ti['new'] = int(round(time.time()*1000))
            self.ti['current'] = (self.ti['new'] - self.ti['last'])/1000
            self.ti['last'] = None
    
    def calculateTE(self):
        if self.flow <= limite and self.te['last'] is None:
            self.te['last'] = int(round(time.time()*1000))
            self.te['new'] = None
            
        elif self.flow > limite and self.te['new'] is None and self.te['last'] is not None:
            self.te['new'] = int(round(time.time()*1000))
            self.te['current'] = (self.te['new'] - self.te['last'])/1000
            self.te['last'] = None
    
    
    def calculateIE(self):
        if self.flow > limite and self.ie['new_calculation'] and self.te['current'] is not None and self.ti['current'] is not None:
            self.ie['current'] = float(self.te['current']/self.ti['current'])
            self.ie['new_calculation'] = False
        
        elif self.flow <= limite and not self.ie['new_calculation']:
            self.ie['new_calculation'] = True
    
    def calculateBPM(self):
        if self.flow > limite and self.bpm['new_calculation'] and self.te['current'] is not None and self.ti['current'] is not None:
            self.bpm['current'] = 60.0/(self.te['current']+self.ti['current'])
            self.bpm['new_calculation'] = False
        
        elif self.flow <= 0.5 and not self.bpm['new_calculation']:
            self.bpm['new_calculation'] = True
            
    def calculatePIF(self):
        if self.flow > limite:
            if self.pif['auxiliar'] is None:
                self.pif['auxiliar'] = self.flow
                
            elif self.flow > self.pif['auxiliar']:
                self.pif['auxiliar'] = self.flow
        
        elif self.flow <= limite and self.pif['auxiliar'] is not None:
            self.pif['current'] = self.pif['auxiliar']
            self.pif['auxiliar'] = None
    

    def calculateVTI(self):
        if self.flow > limite:
            self.volume = self.volume + self.flow*0.025/(60.0)*1000
            self.flow_last = self.flow
            if self.vti['auxiliar'] is None:
                self.volume = 0.0
                self.flow_last = 0.0
                self.volume = self.volume + self.flow*0.025/(60.0)*1000
                self.flow_last = self.flow
                self.vti['auxiliar'] = self.volume
                
            elif self.volume > self.vti['auxiliar']:
                self.vti['auxiliar'] = self.volume
            return
        
        elif self.flow <= limite and self.vti['auxiliar'] is not None:          
            self.vti['current'] = self.vti['auxiliar']
            self.vti['auxiliar'] = None
            
        self.volume = self.volume + self.flow*0.025/(60.0)*1000
        self.flow_last = self.flow  

    
    def calculateALL(self):
        self.calculatePIP()
        self.calculatePEEP()
        self.calculateTI()
        self.calculateTE()
        self.calculateIE()
        self.calculateBPM()
        self.calculatePIF()
        self.calculateVTI()
