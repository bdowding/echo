import struct
import time
from PySide2 import QtWidgets, QtCore

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from comms import Comms

class MainWindow:
    def __init__(self):
        self._comms = Comms("COM4")
        self._timer = QtCore.QTimer()
        self._timer.setSingleShot(False)
        self._timer.timeout.connect(self._get_distance)
        self._timer.start(10)
        
        self._window = QtWidgets.QWidget()
        self._window.show()

        self._grid = QtWidgets.QGridLayout()
        self._window.setLayout(self._grid)

        self._distance_text = QtWidgets.QLineEdit()
        self._grid.addWidget(self._distance_text)

        figure = Figure()
        self._canvas = FigureCanvasQTAgg(figure)
        self._axes = figure.add_subplot(111)
                
        self._grid.addWidget(self._canvas, 1, 0)

        self._distance_readings = []

    def _get_distance(self):
        response = self._comms.call_function(0, bytes())
        if not response:
            self._distance_readings.append((time.time(), None))
            self._distance_text.setText(f"-")
            return
        distance = struct.unpack("<L", response)[0]
        self._distance_readings.append((time.time(), distance))
        self._distance_readings = self._distance_readings[-100:]
        self._distance_text.setText(f"{distance}")
        self._redraw_graph()
    
    def _redraw_graph(self):
        self._axes.clear()

        self._axes.plot([x[0] for x in self._distance_readings], 
                           [x[1] for x in self._distance_readings])
        self._axes.set_ybound(0, 300000)
        self._canvas.draw()

        


app = QtWidgets.QApplication()

window = MainWindow()

app.exec_()















