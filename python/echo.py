import struct
import time
from PySide2 import QtWidgets, QtCore

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from comms import SerialComms

class MainWindow:
    def __init__(self):
        self._comms = SerialComms("COM4")
        self._read_timer = QtCore.QTimer()
        self._read_timer.setSingleShot(False)
        self._read_timer.timeout.connect(self._get_distance)
        self._read_timer.start(1)
        
        self._draw_timer = QtCore.QTimer()
        self._draw_timer.setSingleShot(False)
        self._draw_timer.timeout.connect(self._redraw_graph)
        self._draw_timer.start(50)
        
        self._window = QtWidgets.QWidget()
        self._window.show()

        self._grid = QtWidgets.QGridLayout()
        self._window.setLayout(self._grid)

        self._distance_text = QtWidgets.QLineEdit()
        self._grid.addWidget(self._distance_text)

        figure = Figure()
        self._canvas = FigureCanvasQTAgg(figure)
        self._axes = figure.add_subplot(121)
        self._axes_pos = figure.add_subplot(122)
                
        self._grid.addWidget(self._canvas, 1, 0)

        self._distance_readings = []

    def _get_distance(self):
        response = self._comms.call_function(0, bytes())
        if not response:
            self._distance_readings.append((time.time(), (None, None)))
            self._distance_text.setText(f"-")
            return
        distances = struct.unpack("<LL", response)
        self._distance_readings.append((time.time(), distances))
        old_timestamp = time.time() - 10
        while self._distance_readings and self._distance_readings[0][0] < old_timestamp:
            self._distance_readings.pop(0)
        self._distance_text.setText(f"{distances}")
    
    def _redraw_graph(self):
        self._axes.clear()
        self._axes_pos.clear()

        if not self._distance_readings:
            return

        self._axes.plot([x[0] for x in self._distance_readings], 
                           [x[1][0] for x in self._distance_readings])
        self._axes.plot([x[0] for x in self._distance_readings], 
                           [x[1][1] for x in self._distance_readings])
        self._axes.set_ybound(0, 300000)

        t_start = self._distance_readings[-30:][0][0]
        t_end = self._distance_readings[-1][0]
        def time_to_color(t):
            time_range = t_end - t_start
            time_delta = t - t_start
            if time_range == 0:
                return (1, 0, 0)
            else:
                return (time_delta / time_range, 0, 0)
        self._axes_pos.scatter([x[1][0] for x in self._distance_readings[-30:]],
                            [x[1][1] for x in self._distance_readings[-30:]],
                            c=[time_to_color(x[0]) for x in self._distance_readings[-30:]])
        self._axes_pos.set_xbound(0, 150000)
        self._axes_pos.set_ybound(0, 150000)

        self._canvas.draw()

        


app = QtWidgets.QApplication()

window = MainWindow()

app.exec_()















