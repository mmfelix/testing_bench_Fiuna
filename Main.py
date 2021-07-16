#!/usr/bin/python3
import datetime
from datetime import timedelta, timezone
import csv

import time, serial
from kivy import app
from kivy.lang.builder import Builder
import ADS1256
import RPi.GPIO as GPIO
import subprocess
import time
from ventparams import VentilatorParams
from kivy.properties import ObjectProperty, StringProperty
from kivy.config import Config
from kivy.core.window import Window
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.spinner import Spinner
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.vkeyboard import VKeyboard
from kivy_garden.graph import Graph, LinePlot
from kivy.uix.screenmanager import ScreenManager, Screen

Config.set('kivy', 'keyboard_mode', 'systemanddock')
Config.set('graphics', 'fullscreen', '1')
Config.set('graphics', 'show_cursor', '0')
Config.set('graphics', 'height', '720')
Config.set('graphics', 'width', '1080')
Config.write()

EnableGraph = False
EnableRecord = False
EnableShow = False

record_time = ''
CSV_file_name = 'default'
count = 0
offset_pressure = 0.0
offset_flow = 0.0

try:
    ADC = ADS1256.ADS1256()
    ADC.ADS1256_init()
               
except:
    GPIO.cleanup()
    print ("\r\nProgram end     ")

# for i in range(100):
#     offset_pressure += 105.0/4.0*(ADC.ADS1256_GetChannalValue(1)*5.0/0x7fffff-0.5) - 5.0
#     offset_flow += (-1)*(ADC.ADS1256_GetChannalValue(2)*5.0/0x7fffff-2.5)*125.0
# 
# offset_pressure = offset_pressure/100.0
# offset_flow = offset_flow/100.0
    
def createCSV(name="default"):
    with open(name+'.csv', 'w', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(["Time", "Presion", "Flujo", "Oxigeno"])
        file.close()

def recordCSV(name="default", pressure=0.0, flow=0.0, oxygen=0.0):
    time = datetime.datetime.now(timezone.utc)
    utc_time = time.replace(tzinfo=timezone.utc)
    utc_timestamp = utc_time.timestamp()
    row = [utc_timestamp, pressure, flow, oxygen]
    with open(name+'.csv', 'a', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(row)
        file.close()

class WindowManager(ScreenManager):
    pass

class AdvertenciaPopUp(Popup):
    pass

class RecordWindow(Screen):
    file_name = ObjectProperty(None)
    min = ObjectProperty(None)
    sec = ObjectProperty(None)

    def accept(self):
        global EnableRecord, CSV_file_name, record_time
        try:
            print(self.min.text, self.sec.text)
            record_time = datetime.datetime.now() + timedelta(minutes=int(self.min.text), seconds=int(self.sec.text))
            
            if self.file_name.text != '':
                CSV_file_name = self.file_name.text

            self.file_name.text = ''
            self.min.text = ''
            self.sec.text = ''
            EnableRecord = True
            App.get_running_app().root.current = "main"
            self.manager.transition.direction = "up"

        except:
            AdvertenciaPopUp().open()


    def cancel(self):
        global EnableRecord
        EnableRecord = False

class ClockText(Label):
    def __init__(self, *args, **kwargs):
        super(ClockText, self).__init__(*args, **kwargs)
        Clock.schedule_interval(self.update, 1)

    def update(self, *args):
        self.text = time.strftime('%I:%M:%S %p')
    

class ConfigTab(TabbedPanel):
    pass
   

class MainWindow(Screen):
    graph_P = ObjectProperty(Graph())
    graph_F = ObjectProperty(Graph())
    graph_V = ObjectProperty(Graph())
    
    pip_string = StringProperty("--")
    peep_string = StringProperty("--")
    ti_string = StringProperty("--")
    fio2_string= StringProperty("--")
    ie_string = StringProperty("--")
    bpm_string = StringProperty("--")
    pif_string = StringProperty("--")
    vti_string = StringProperty("--")


    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.plot_p = LinePlot(line_width=1.1, color=[1, 0, 0, 1])
        self.plot_f = LinePlot(line_width=1.1, color=[0.5, 1, 0.5, 1])
        self.plot_v = LinePlot(line_width=1.1, color=[0, 0.55, 0.8, 1])
        self.parameters = VentilatorParams()
        Clock.schedule_interval(self.update, 1/100.0)

    def update(self, *args):
        global count, record_time, EnableRecord
        # if offset < 80 and count == 9.5:
        #     offset += 5
        
        # self.graph_F.ymax = offset+3
        # self.graph_F.ymin = -offset+2

        
        if EnableRecord or EnableShow or EnableGraph:
            try:
                self.parameters.pressure = 105.0/4.0*(ADC.ADS1256_GetChannalValue(1)*5.0/0x7fffff-0.5) - 5.0
                self.parameters.flow = (-1)*(ADC.ADS1256_GetChannalValue(2)*5.0/0x7fffff-2.5)*125.0
                self.parameters.oxygen = (39)*(ADC.ADS1256_GetChannalValue(0)*5.0/0x7fffff-3.0) + 100.0
                                    
            except:
                pass
        
        if EnableRecord:
            self.ids['grabar'].background_color = (0.0, 0.7, 0.0, 1.0)
            self.ids['grabar'].text = str(record_time - datetime.datetime.now())[2:7]
            if (record_time - datetime.datetime.now()) < datetime.timedelta(0):
                EnableRecord = False

            recordCSV(CSV_file_name, self.parameters.pressure, self.parameters.flow, self.parameters.oxygen)
        
        else:
            self.ids['grabar'].text = "Grabación"
            self.ids['grabar'].background_color = (0.15, 0.15, 0.15, 1.0)

        if EnableShow:
            self.parameters.calculateALL()
            try:
                self.pip_string = str(round(self.parameters.pip['current'], 1))
                self.peep_string = str(round(self.parameters.peep['current'], 1))
                self.ti_string = str(round(self.parameters.ti['current'], 2))
                self.fio2_string = str(round(self.parameters.oxygen, 1))
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
            self.fio2_string = "--"
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

    def recordButton(self):
        global EnableRecord
        if self.ids['grabar'].background_color == [0.0, 0.7, 0.0, 1.0]:
            self.ids['grabar'].background_color = (0.15, 0.15, 0.15, 1.0)
            EnableRecord = False
            print("hola")
            return
        elif self.ids['grabar'].background_color == [0.15, 0.15, 0.15, 1]:
            App.get_running_app().root.current = "record"
            self.manager.transition.direction = "down"
            return

    def infoButton(self):
        if self.ids['info'].background_color == [0.0, 0.7, 0.0, 1.0]:
            self.ids['info'].background_color = (0.15, 0.15, 0.15, 1.0)
            return
        elif self.ids['info'].background_color == [0.15, 0.15, 0.15, 1]:
            self.ids['info'].background_color = (0.0, 0.7, 0.0, 1.0)
            return

    def exitButton(self):
        exit()

class MainApp(App):
    def build(self):
        pass

if __name__ == '__main__':
    MainApp().run()
