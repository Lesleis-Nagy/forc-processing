from importlib import resources

import sys
import numpy as np
import random

from PyQt6 import QtCore
from PyQt6 import QtGui

from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QSizePolicy, QVBoxLayout, QPushButton

from PyQt6 import uic

from magicgui import widgets


import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class MyFigureCanvas(FigureCanvas):
    """ Subclass canvas to catch the resize event """
    def __init__(self, figure):
        self.lastEvent = False # store the last resize event's size here
        FigureCanvas.__init__(self, figure)

    # def resizeEvent(self, event):
    #     if not self.lastEvent:
    #         # at the start of the app, allow resizing to happen.
    #         super(MyFigureCanvas, self).resizeEvent(event)
    #     # store the event size for later use
    #     self.lastEvent = (event.size().width(),event.size().height())
    #     print("try to resize, I don't let you.")
    #
    # def do_resize_now(self):
    #     # recall last resize event's size
    #     newsize = QtCore.QSize(self.lastEvent[0],self.lastEvent[1] )
    #     # create new event from the stored size
    #     event = QtGui.QResizeEvent(newsize, QtCore.QSize(1, 1))
    #     print("Now I let you resize.")
    #     # and propagate the event to let the canvas resize.
    #     super(MyFigureCanvas, self).resizeEvent(event)


class ApplicationWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.main_widget = QWidget(self)
        l = QVBoxLayout(self.main_widget)
        self.fig = Figure()
        # use subclassed FigureCanvas
        self.canvas = MyFigureCanvas(self.fig)
        self.button = QPushButton("Manually Resize")
        l.addWidget(self.button)
        l.addWidget(self.canvas)
        self.setCentralWidget(self.main_widget)
        self.button.clicked.connect(self.action)
        self.plot()

    def action(self):
        # when button is clicked, resize the canvas.
        self.canvas.do_resize_now()

    def plot(self):
        # just some random plots
        self.axes = []
        for i in range(4):
            ax = self.fig.add_subplot(2,2,i+1)
            a = np.random.rand(100,100)
            ax.imshow(a)
            self.axes.append(ax)
        self.fig.tight_layout()

def main():

    qApp = QApplication(sys.argv)
    aw = ApplicationWindow()
    aw.show()
    sys.exit(qApp.exec())
