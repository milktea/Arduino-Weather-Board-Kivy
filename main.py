from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.clock import Clock
from collections import deque
import matplotlib
matplotlib.use('module://kivy.garden.matplotlib.backend_kivy')
from matplotlib.figure import Figure
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvas,\
                                                NavigationToolbar2Kivy
from matplotlib import style
import matplotlib.pyplot as plt
import sys
import time
import threading
import thread
import serial

from random import random


#matplot layout
style.use('fivethirtyeight')

# Basic class Screen Layout
class WeatherData(Screen):
    #random bg color
    hue = NumericProperty(0)

    def __init__(self, **kwargs):
        super(WeatherData, self).__init__(**kwargs)

        self.data_gen = self.weather_data()
        self.val = 0

        self.plot = Matplot()
        self.plot_canvas = self.plot.canvas

    def read_data(self):
        print "Reading data from arduino"
        # Get data from serial port
        return arduino.readline().strip("\n\t\r\x12\x13 ")

    def dic_data(self, data):
        values = data.split(' ')    
        keys = ['temp1', 
                'temp2', 
                'humidity', 
                'dewpoint', 
                'pressure', 
                'light', 
                'wind_speed', 
                'wind_direction', 
                'rainfall', 
                'date', 
                'time']
        new_data = dict(zip(keys, values))
        return new_data

    def weather_data(self):
        while True:
            try:
                data = self.read_data()
                if len(data):
                    yield self.dic_data(data)
            except KeyboardInterrupt:
                sys.exit()

    def update_label(self, delta):
        val = self.data_gen.next()

        #show data 
        self.ids.temp1.text = str(val['temp1'])
        self.ids.humidity.text = str(val['humidity'])
        self.ids.dewpoint.text = str(val['dewpoint'])
        self.ids.pressure.text = str(val['pressure'])
        self.ids.light.text = str(val['light'])
        self.ids.wind_speed.text = str(val['wind_speed'])
        self.ids.wind_direction.text = str(val['wind_direction'])
        self.ids.rainfall.text = str(val['rainfall'])
        self.ids.date.text = str(val['date'])
        self.ids.time.text = str(val['time'])

        #graph light
        self.plot.callback(val['light'])

#matlpotlib graph
class Matplot(object):
    def __init__(self):
        self.a1 = deque([0] * 10)
        self.fig = plt.figure()
        #  subplot(nrows, ncols, plot_number)
        self.ax = self.fig.add_subplot(1, 1, 1)

        self.line, = plt.plot(self.a1)
        plt.ion()
        plt.ylim([0,10])
        plt.show()

        self.canvas = self.fig.canvas

    def callback(self, val):
        array_index = 5
        self.graph(val);
        self.canvas.draw()

    def graph(self, data):
        self.a1.appendleft(data)
        datatoplot = self.a1.pop()
        self.line.set_ydata(self.a1)
        plt.draw() 


# Main App class
class ArduinoApp(App):
    def build(self):

        layout = BoxLayout(orientation='vertical')
    
        root = ScreenManager()

        weather_data = WeatherData(name='Navigation')
        root.add_widget(weather_data)

        refresh_time = 0.1
        Clock.schedule_interval(weather_data.update_label, refresh_time)

        #add widget to the data
        layout.add_widget(root)
        #add widget to plot graph
        layout.add_widget(weather_data.plot_canvas)

        return layout

# Main program
if __name__ == '__main__':
    # Connect to serial port
    try:
        print "Connecting to arduino"
        arduino = serial.Serial('/dev/tty.HC-06-DevB', 9600)
        print "Connected"
    except:
        print "Failed to connect"
        exit()

    #Launch the app
    ArduinoApp().run()

    #Close serial commu
    arduino.close()

