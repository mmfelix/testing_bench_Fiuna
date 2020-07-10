from math import cos
import datetime
import csv
import time

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
Config.set('graphics', 'height', '840')
Config.set('graphics', 'width', '1450')
Config.write()

EnableGraph = False
EnableRecord = False
CSV_file_name = ''
count = 0


def createCSV(name="hehe"):
    with open(name+'.csv', 'w', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(["Dia", "Hora", "Minuto", "Segundo", "Microsegundo"])
        file.close()
    pass

def recordCSV(name="hehe"):
    time = datetime.datetime.now()
    row = [time.date(), time.hour, time.minute, time.second, time.microsecond]
    with open(name+'.csv', 'a', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(row)
        file.close()

class ClockText(Label):
    def __init__(self, *args, **kwargs):
        super(ClockText, self).__init__(*args, **kwargs)
        Clock.schedule_interval(self.update, 1)

    def update(self, *args):
        self.text = time.strftime('%I'+':'+'%M'+' %p')


class RecordPopUp(Popup):
    file_name = ObjectProperty(None)
    name = StringProperty('')

    def accept(self):
        global EnableRecord, CSV_file_name
        self.name = self.file_name.text
        CSV_file_name = self.name
        self.name = ''
        createCSV(CSV_file_name)
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

    def __init__(self, *args, **kwargs):
        super(MainScreen, self).__init__(*args, **kwargs)
        self.plot_p = LinePlot(line_width=1.5, color=[1, 0, 0, 1])
        self.plot_f = LinePlot(line_width=2, color=[0.5, 1, 0.5, 1])
        self.plot_v = LinePlot(line_width=2, color=[0, 0.55, 0.8, 1])
        Clock.schedule_interval(self.update, 0.01)

    def update(self, *args):
        global count, EnableGraph, EnableRecord
        if EnableRecord:
            print("ok")
            recordCSV(CSV_file_name)
        if EnableGraph:
            if count >= 700:
                count = 0

            self.plot_p.points = [(x, cos((x / 10))) for x in range(0, count)]
            self.graph_P.add_plot(self.plot_p)

            self.plot_f.points = [(x, cos((x / 40.))) for x in range(0, count)]
            self.graph_F.add_plot(self.plot_f)

            self.plot_v.points = [(x, cos((x / 40.))) for x in range(0, count)]
            self.graph_V.add_plot(self.plot_v)

            count += 1

    def graphButton(self):
        global EnableGraph, count
        if self.ids['graficar'].background_color == [0.0, 0.7, 0.0, 1.0]:
            self.ids['graficar'].background_color = (0.15, 0.15, 0.15, 1.0)
            EnableGraph = False
            count = 0
            self.plot_p.points = []
            self.plot_f.points = []
            self.plot_v.points = []
            self.graph_P.add_plot(self.plot_p)
            self.graph_F.add_plot(self.plot_f)
            self.graph_V.add_plot(self.plot_v)
            return

        elif self.ids['graficar'].background_color == [0.15, 0.15, 0.15, 1]:
            self.ids['graficar'].background_color = (0.0, 0.7, 0.0, 1.0)
            EnableGraph = True
            return

    def showButton(self):
        if self.ids['mostrar'].background_color == [0.0, 0.7, 0.0, 1.0]:
            self.ids['mostrar'].background_color = (0.15, 0.15, 0.15, 1.0)
            return
        elif self.ids['mostrar'].background_color == [0.15, 0.15, 0.15, 1]:
            self.ids['mostrar'].background_color = (0.0, 0.7, 0.0, 1.0)
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
            EnableRecord = False
            self.ids['grabar'].background_color = (0.15, 0.15, 0.15, 1.0)
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
        exit()


class MainApp(App):
    def build(self):
        test = MainScreen()
        return test

if __name__ == '__main__':
    MainApp().run()