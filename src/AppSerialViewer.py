from serial_viewer import Ui_Form_serial_viewer
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal
import pyqtgraph as pg
import numpy as np


MAX_POINTS = 2000

class DropPlotWidget(pg.PlotWidget):
    variableDropped = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        var_name = event.mimeData().text()
        self.variableDropped.emit(var_name)
        event.acceptProposedAction()


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Serial Parser Settings")
        layout = QFormLayout()

        self.delim = QLineEdit(",")
        self.assign = QLineEdit("=")
        self.eol = QComboBox()
        self.eol.addItems(["\\n", "\\r\\n", "Custom"])
        self.custom_eol = QLineEdit("")

        layout.addRow("Delimiter:", self.delim)
        layout.addRow("Assign symbol:", self.assign)
        layout.addRow("End of line:", self.eol)
        layout.addRow("Custom EOL:", self.custom_eol)

        self.btn_save = QPushButton("Save")
        self.btn_save.clicked.connect(self.accept)
        layout.addWidget(self.btn_save)

        self.setLayout(layout)

    def get_settings(self):
        eol = "\n"
        if self.eol.currentText() == "Custom":
            eol = self.custom_eol.text()
        elif self.eol.currentText() == "\\r\\n":
            eol = "\r\n"
        return {
            "delimiter": self.delim.text(),
            "assign": self.assign.text(),
            "eol": eol
        }


class DialogShowGraph(QDialog, Ui_Form_serial_viewer):

    serial_connection_signal = pyqtSignal(object)
    
    def __init__(self):
        super(DialogShowGraph, self).__init__()
        self.setupUi(self)

        self.listWidget_variable_list.itemDoubleClicked.connect(self.toggleCurve)
        
        self.parser_settings = {"delimiter": ",", "assign": "=", "eol": "\n"}
        self.last_line = ""
        self.curves = {}   
        self.data = {}     
        self.legend_items = {}  

        # Create graph
        self.CreateGraph()
        self.UpdateGraph()

        # Connect buttons
        self.pushButton_serial_viewer_settings.clicked.connect(self.openSettings)
        self.pushButton_refresh_variable_list.clicked.connect(self.refreshVariables)

        # Enable drag from variable list
        self.listWidget_variable_list.setDragEnabled(True)

        # Connect drop event from graph
        self.plot_widget.variableDropped.connect(self.addCurve)

    def handle_serial_line(self, line: str):
        self.last_line = line
        self.SerialDataHandler(line)

    def openSettings(self):
        dlg = SettingsDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            self.parser_settings = dlg.get_settings()


    def toggleCurve(self, item):
        var_name = item.text()
        if var_name in self.curves:
            self.removeCurve(var_name)
        else:
            self.addCurve(var_name)



    def GetVariables(self, line):
        parts = line.strip().split(self.parser_settings["delimiter"])
        variables = {}
        for p in parts:
            if self.parser_settings["assign"] in p:
                key, val = p.split(self.parser_settings["assign"], 1)
                try:
                    variables[key.strip()] = float(val.strip())
                except ValueError:
                    pass
        return variables

    def refreshVariables(self):

        if self.last_line:

            try:
                variables = self.GetVariables(self.last_line)
                self.listWidget_variable_list.clear()
                self.listWidget_variable_list.addItems(variables.keys())

            except Exception as e:
                QMessageBox.warning(self, "Serial Viewer", f"ERROR: {e}")

            if len(variables) == 0:
                QMessageBox.warning(self, "Serial Viewer", "Data is not detectd !!")
        else:
            QMessageBox.warning(self, "Serial Viewer", "Data is not detectd !!")


    def SerialDataHandler(self, line):
        # variables = self.GetVariables(line)
        self.updateCurves()

   
    def CreateGraph(self):
        self.plot_widget = DropPlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.showGrid(x=True, y=True)
        self.legend = self.plot_widget.addLegend()

        layout = QVBoxLayout(self.scrollAreaWidgetContents)
        layout.addWidget(self.plot_widget)


    def addCurve(self, var_name):
        if var_name not in self.curves:
            pen = pg.mkPen(color=pg.intColor(len(self.curves)), width=2)
            curve = self.plot_widget.plot([], [], pen=pen, name=var_name)
            self.curves[var_name] = curve

            # initialize buffer correctly
            self.data[var_name] = np.zeros(MAX_POINTS, dtype=float)

            sample, label = self.legend.items[-1]  # last added item
            self.legend_items[var_name] = label

    def showLegendContextMenu(self, pos, var_name, label):
        menu = QMenu()
        remove_action = menu.addAction("Remove " + var_name)
        action = menu.exec_(label.mapToGlobal(pos))
        if action == remove_action:
            self.removeCurve(var_name)

    def removeCurve(self, var_name):
        if var_name in self.curves:
            self.plot_widget.removeItem(self.curves[var_name])
            del self.curves[var_name]
            del self.data[var_name]

            # remove legend entry
            if var_name in self.legend_items:
                label = self.legend_items[var_name]
                label.deleteLater()
                del self.legend_items[var_name]

    def updateCurves(self):

        if not self.last_line:
            return

        try:

            variables = self.GetVariables(self.last_line)

            for var_name, val in variables.items():
                if var_name in self.curves:
                    buf = self.data[var_name]
                    buf[:-1] = buf[1:]   # shift left
                    buf[-1] = val        # insert new value
                    self.curves[var_name].setData(np.arange(MAX_POINTS), buf)

        except Exception as e:
                print(f"ERROR: {e}")

    def PlotUpdate(self):
        if hasattr(self, "last_line") and self.last_line:
            self.SerialDataHandler(self.last_line)

    def UpdateGraph(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.PlotUpdate)
        self.timer.start(30)  