from multiprocessing import Pool

from math import cos
import time
# import ADS1256
# import RPi.GPIO as GPIO

from kivy.config import Config
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy_garden.graph import Graph, LinePlot

Config.set('graphics', 'fullscreen', '0')
Config.set('graphics', 'height', '840')
Config.set('graphics', 'width', '1080')
Config.write()

graph_pressure = Graph(xlabel='Time', ylabel='Presion', x_ticks_minor=10,
                       x_ticks_major=70, y_ticks_major=100,
                       y_grid_label=True, x_grid_label=True, padding=5,
                       x_grid=True, y_grid=True, xmin=-0, xmax=700, ymin=0, ymax=200)

graph_flow = Graph(xlabel='Time', ylabel='Flujo', x_ticks_minor=10,
                   x_ticks_major=70, y_ticks_major=0.2,
                   y_grid_label=True, x_grid_label=True, padding=5,
                   x_grid=True, y_grid=True, xmin=-0, xmax=700, ymin=-1, ymax=1)

graph_volume = Graph(xlabel='Time', ylabel='Volume', x_ticks_minor=10,
                     x_ticks_major=70, y_ticks_major=0.2,
                     y_grid_label=True, x_grid_label=True, padding=5,
                     x_grid=True, y_grid=True, xmin=-0, xmax=700, ymin=-1, ymax=1)


plot_pressure = LinePlot(line_width=1.5, color=[1, 0, 0, 1])
plot_flow = LinePlot(line_width=2, color=[0.5, 1, 0.5, 1])
plot_volume = LinePlot(line_width=2, color=[0.5, 1, 0.5, 1])

count = 0

class Graphics(GridLayout):
    def __init__(self):
        super(Graphics, self).__init__(cols=2)
        self.add_widget(graph_pressure)
        self.add_widget(Button(text='Hola Mundo', size_hint_x=0.1, size_hint_y=0.1, width=10, height=200))
        self.add_widget(graph_flow)
        self.add_widget(Button(text='Hola Mundooo', size_hint_x=.3, padding=(500, 100)))
        self.add_widget(graph_volume)
        self.add_widget(Button(text='Hola Mundoooo', size_hint_x=.3, padding=(550, 100)))

    def update(self, *args):
        t = int(round(time.time() * 10))
        global count
        value = 25
        if value is not None:
            plot_flow.points = [(x, cos(t + (x / 10.))) for x in range(0, 701)]
            graph_flow.add_plot(plot_flow)

            if count >= 700:
                count = 0
                plot_pressure.points = [(count, value)]
                graph_pressure.add_plot(plot_pressure)
            else:
                plot_pressure.points.append((count, value))
                graph_pressure.add_plot(plot_pressure)
                count += 1


class TestApp(App):
    def build(self):
        test = Graphics()
        Clock.schedule_interval(test.update, 0.01)
        return test

if __name__ == '__main__':
    TestApp().run()