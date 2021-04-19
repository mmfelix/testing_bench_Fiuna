#!/usr/bin/python3
import datetime
import csv
import time, serial
import ADS1256
import RPi.GPIO as GPIO
import subprocess
import time
from ventparams import VentilatorParams

import smbus
from fcntl import ioctl
from struct import unpack

from kivy.properties import ObjectProperty, StringProperty
from kivy.config import Config
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy_garden.graph import LinePlot

Config.set('graphics', 'fullscreen', '1')
Config.set('graphics', 'show_cursor', '0')
Config.set('graphics', 'height', '320')
Config.set('graphics', 'width', '480')
Config.write()

EnableGraph = False
EnableRecord = False
EnableShow = False

CSV_file_name = 'default'
count = 0
offset = 0

# df = pd.read_csv("Gui_data.csv")

ADDRESS = 0x40
sfm3300 = smbus.SMBus(1)
# ser = serial.Serial("/dev/ttyUSB0", baudrate=115200, timeout=2)

try:
    ADC = ADS1256.ADS1256()
    ADC.ADS1256_init()
    
#     sfm3300.write_byte_data(ADDRESS, 16, 0)
#     i2c = open("/dev/i2c-1", "rb", buffering=0)
#     ioctl(i2c, 0x0703, ADDRESS)
#     i2c.read(3)
#                 
except:
    #GPIO.cleanup()
    print ("\r\nProgram end     ")

# pressure = 0.0
# 
# for i in range(100):
#     pressure = ADC.ADS1256_GetChannalValue(0)*5/0x7fffff
#     pressure = (pressure-(0.10*3.3))*10/(0.8*3.3) + 5
#     pressure *= 70.307
#     offset = offset + pressure
# offset = offset/100.0
    
def createCSV(name="default"):
    with open(name+'.csv', 'w', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(["Dia", "Hora", "Minuto", "Segundo", "Microsegundo",
                         "Presion", "Flujo"])
        file.close()

def recordCSV(name="default", pressure=0.0, flow=0.0):
    time = datetime.datetime.now()
    row = [time.date(), time.hour, time.minute, time.second, time.microsecond,
           pressure, flow]
    with open(name+'.csv', 'a', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(row)
        file.close()


class ClockText(Label):
    def __init__(self, *args, **kwargs):
        super(ClockText, self).__init__(*args, **kwargs)
        Clock.schedule_interval(self.update, 1)

    def update(self, *args):
        self.text = time.strftime('%I'+':'+'%M'+':'+'%S'+ '%p')


class RecordPopUp(Popup):
    file_name = ObjectProperty(None)
    name = StringProperty('')

    def accept(self):
        global EnableRecord, CSV_file_name
        self.name = self.file_name.text
        CSV_file_name = self.name
        self.name = ''
        command = "./ads1256_test /home/pi/TestBench/RaspberryPI/ADS1256/python3/ peeerrooo 0 5"
        subprocess.Popen(["./ads1256_test", "/home/pi/TestBench/RaspberryPI/ADS1256/python3/",
                          "cccccc", "0", "5"])
        time.sleep(10)
        EnableRecord = True
        self.dismiss()

    def cancel(self):
        global EnableRecord
        EnableRecord = False
        self.dismiss()


class ConfigTab(TabbedPanel):
    pass


class ConfigPopUp(Popup):
    def accept(self):
        self.dismiss()

    def cancel(self):
        self.dismiss()
    pass
    
class MainScreen(BoxLayout):
    graph_P = ObjectProperty(None)
    graph_F = ObjectProperty(None)
    graph_V = ObjectProperty(None)

    pip_string = StringProperty("--")
    peep_string = StringProperty("--")
    ti_string = StringProperty("--")
    te_string= StringProperty("--")
    ie_string = StringProperty("--")
    bpm_string = StringProperty("--")
    pif_string = StringProperty("--")
    vti_string = StringProperty("--")


    def __init__(self, *args, **kwargs):
        super(MainScreen, self).__init__(*args, **kwargs)
        self.plot_p = LinePlot(line_width=1.1, color=[1, 0, 0, 1])
        self.plot_f = LinePlot(line_width=1.1, color=[0.5, 1, 0.5, 1])
        self.plot_v = LinePlot(line_width=1.1, color=[0, 0.55, 0.8, 1])
        self.parameters = VentilatorParams()
        Clock.schedule_interval(self.update, 1/100.0)

    def update(self, *args):
        global count, offset
        
        if EnableRecord or EnableShow or EnableGraph:
            try:
                self.parameters.pressure = ADC.ADS1256_GetChannalValue(0)*5/0x7fffff
                self.parameters.flow = ADC.ADS1256_GetChannalValue(1)*5/0x7fffff
                               
#                 d0, d1, c = unpack('BBB', i2c.read(3))
#                 d = (d0 << 8) | d1
#                 self.parameters.flow = (float(d) - 32768.0)/120
                pass
                    
            except:
                pass
        
#         if EnableRecord:
#             recordCSV(CSV_file_name, self.parameters.pressure, self.parameters.flow)

        if EnableShow:
            self.parameters.calculateALL()
            try:
                self.pip_string = str(round(self.parameters.pip['current'], 1))
                self.peep_string = str(round(self.parameters.peep['current'], 1))
                self.ti_string = str(round(self.parameters.ti['current'], 2))
                self.te_string = str(round(self.parameters.te['current'], 2))
                self.ie_string = str(round(self.parameters.ie['current'], 1))
                self.bpm_string = str(round(self.parameters.bpm['current'], 1))
                self.pif_string = str(round(self.parameters.pif['current'], 1))
                self.vti_string = str(int(self.parameters.vti['current']))
            except:
                pass
        else:
            self.pip_string = "--"
            self.peep_string = "--"
            self.ti_string= "--"
            self.te_string = "--"
            self.ie_string = "--"
            self.bpm_string = "--"
            self.pif_string = "--"
            self.vti_string = "--"

        if EnableGraph:
            if count >= 10:
                self.plot_p.points.clear()
                self.plot_f.points.clear()
                self.plot_v.points.clear()
                count = 0

            self.plot_p.points.append((count, self.parameters.pressure))
            self.graph_P.add_plot(self.plot_p)

            self.plot_f.points.append((count, self.parameters.flow))
            self.graph_F.add_plot(self.plot_f)

            self.plot_v.points.append((count, self.parameters.volume))
            self.graph_V.add_plot(self.plot_v)
                
            count += 0.025


    def graphButton(self):
        global EnableGraph, count
        if self.ids['graficar'].background_color == [0.0, 0.7, 0.0, 1.0]:
            self.ids['graficar'].background_color = (0.15, 0.15, 0.15, 1.0)
            EnableGraph = False
            count = 0
            self.plot_p.points.clear()
            self.plot_f.points.clear()
            self.plot_v.points.clear()
            self.graph_P.add_plot(self.plot_p)
            self.graph_F.add_plot(self.plot_f)
            self.graph_V.add_plot(self.plot_v)
            return

        elif self.ids['graficar'].background_color == [0.15, 0.15, 0.15, 1]:
            self.ids['graficar'].background_color = (0.0, 0.7, 0.0, 1.0)
            EnableGraph = True
            return

    def showButton(self):
        global EnableShow
        if self.ids['mostrar'].background_color == [0.0, 0.7, 0.0, 1.0]:
            self.ids['mostrar'].background_color = (0.15, 0.15, 0.15, 1.0)
            EnableShow = False
            return
        elif self.ids['mostrar'].background_color == [0.15, 0.15, 0.15, 1]:
            self.ids['mostrar'].background_color = (0.0, 0.7, 0.0, 1.0)
            EnableShow = True
            return

    def configButton(self):
        if self.ids['setear'].background_color == [0.0, 0.7, 0.0, 1.0]:
            self.ids['setear'].background_color = (0.15, 0.15, 0.15, 1.0)
            return
        elif self.ids['setear'].background_color == [0.15, 0.15, 0.15, 1]:
            ConfigPopUp().open()
            self.ids['setear'].background_color = (0.0, 0.7, 0.0, 1.0)
            return

    def recordButton(self):
        global EnableRecord
        if self.ids['grabar'].background_color == [0.0, 0.7, 0.0, 1.0]:
            self.ids['grabar'].background_color = (0.15, 0.15, 0.15, 1.0)
            EnableRecord = False
            return
        elif self.ids['grabar'].background_color == [0.15, 0.15, 0.15, 1]:
            RecordPopUp().open()
            self.ids['grabar'].background_color = (0.0, 0.7, 0.0, 1.0)
            return

    def infoButton(self):
        if self.ids['info'].background_color == [0.0, 0.7, 0.0, 1.0]:
            self.ids['info'].background_color = (0.15, 0.15, 0.15, 1.0)
            return
        elif self.ids['info'].background_color == [0.15, 0.15, 0.15, 1]:
            self.ids['info'].background_color = (0.0, 0.7, 0.0, 1.0)
            return

    def exitButton(self):
#         command = "/usr/bin/sudo /sbin/shutdown -h now"
#         import subprocess
#         process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
#         output = process.communicate()[0]
        exit()
        print(output)
        
class MainApp(App):
    def build(self):
        test = MainScreen()
        return test

if __name__ == '__main__':
    MainApp().run()
