from ConnectDevice import Ui_DialogConnect
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import serial
import serial.tools.list_ports
from PyQt5.QtCore import pyqtSignal
import json
import os



class DialogConnectDevice(QDialog, Ui_DialogConnect):

    serial_connection_signal = pyqtSignal(object)
    
    def __init__(self,temp_filename=None):
        super(DialogConnectDevice, self).__init__()
        self.setupUi(self)

        self.serial_connection = None

        # temporary port info : 
        self.temp_filename = temp_filename

        # Connect the refresh button to the function to update the serial ports
        self.pushButton.clicked.connect(self.refresh_ports)
        self.commandLinkButton_connect.clicked.connect(self.connect_to_port)
        self.commandLinkButton_cancel.clicked.connect(self.cancel_connection)
        self.commandLinkButton_load.clicked.connect(self.load_serial_config)
        self.commandLinkButton_save.clicked.connect(self.save_serial_config)

        # prepare ports
        self.refresh_ports()


        if self.temp_filename:
             # load tempory info if any
            TempConf = self.load_temp_json(self.temp_filename)
            if TempConf is not None:
                self.comboBox_port.setCurrentText(TempConf.get('port', ''))
                self.comboBox_speed.setCurrentText(TempConf.get('speed', ''))
                self.comboBox_data.setCurrentText(TempConf.get('data_bits', '8'))  # Default to 8 bits if not found
                self.comboBox_stop_bits.setCurrentText(TempConf.get('stop_bits', '1'))  # Default to 1 stop bit if not found
                self.comboBox_flow_control.setCurrentText(TempConf.get('flow_control', 'none'))
                self.lineEdit.setText(TempConf.get('transmit_delay', '0'))  # Default to 0 if not found


        if not self.scrollArea_port_info.layout():
            self.scrollArea_port_info.setLayout(QVBoxLayout())


    def save_serial_config(self):
        # Show the save file dialog
        file_name, _ = QFileDialog.getSaveFileName(self, "Save JSON File", "", "JSON Files (*.json);;All Files (*)")

        # Check if the user selected a file
        if file_name:
            # If the file doesn't already have the .json extension, append it
            if not file_name.endswith('.json'):
                file_name += '.json'

            # Gather the current settings
            config_data = {
                'port': self.comboBox_port.currentText(),
                'speed': self.comboBox_speed.currentText(),
                'data_bits': self.comboBox_data.currentText(),
                'stop_bits': self.comboBox_stop_bits.currentText(),
                'flow_control': self.comboBox_flow_control.currentText(),
                'transmit_delay': self.lineEdit.text()  # Get the transmit delay from the QLineEdit
            }

            try:
                # Save the config data to the selected file in JSON format
                with open(file_name, 'w') as file:
                    json.dump(config_data, file, indent=4)

                QMessageBox.information(self, "Saved", f"Port configuration saved to {file_name}")
            
            except Exception as e:
                QMessageBox.warning(self, "Save Error", f"Could not save the port configuration: {e}")



    def load_serial_config(self):
        # Show the open file dialog
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Serial Config", "", "JSON Files (*.json);;All Files (*)")

        # If the user selected a file
        if file_name:
            try:
                # Open the selected file and read its content
                with open(file_name, 'r') as file:
                    config_data = json.load(file)

                # Fill in the UI fields with the loaded configuration data
                self.comboBox_port.setCurrentText(config_data.get('port', ''))
                self.comboBox_speed.setCurrentText(config_data.get('speed', ''))
                self.comboBox_data.setCurrentText(config_data.get('data_bits', '8'))  # Default to 8 bits if not found
                self.comboBox_stop_bits.setCurrentText(config_data.get('stop_bits', '1'))  # Default to 1 stop bit if not found
                self.comboBox_flow_control.setCurrentText(config_data.get('flow_control', 'none'))
                self.lineEdit.setText(config_data.get('transmit_delay', '0'))  # Default to 0 if not found

                QMessageBox.information(self, "Loaded", f"Port configuration loaded from {file_name}")
            
            except Exception as e:
                QMessageBox.warning(self, "Load Error", f"Could not load the port configuration: {e}")



    def refresh_ports(self):
        """Function to refresh available serial ports"""
        self.comboBox_port.clear()  # Clear the current list
        available_ports = self.get_available_ports()  # Get list of available ports
        self.comboBox_port.addItems(available_ports)  # Add ports to the comboBox

    def get_available_ports(self):
        """Returns a list of available serial ports"""
        ports = []
        if sys.platform == 'win32':
            # For Windows, use pyserial to list available ports
            ports = [port.device for port in serial.tools.list_ports.comports()]
        elif sys.platform == 'linux':
            # For Linux, use pyserial to list available ports
            ports = [port.device for port in serial.tools.list_ports.comports()]
            usb_ports = [f"/dev/{dev}" for dev in os.listdir("/dev") if dev.startswith("ttyUSB") or dev.startswith("ttyACM")]
            ports.extend(usb_ports)
        return ports

    # cancel connection
    def cancel_connection(self):
        self.reject()


    def connect_to_port(self):
        """Function to connect to the selected serial port"""
        port = self.comboBox_port.currentText()  # Get the selected port
        baud_rate = self.comboBox_speed.currentText()  # Get the selected baud rate
        data_bits = self.comboBox_data.currentText()
        stop_bits = self.comboBox_stop_bits.currentText()
        flow_control = self.comboBox_flow_control.currentText()

        try:
            
            # Close the existing connection if any
            if self.serial_connection and self.serial_connection.is_open:
                self.serial_connection.close()  

            # Open the serial port
            self.serial_connection = serial.Serial(
                port,
                baudrate=int(baud_rate),
                timeout=1,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            )

            # Ensure the connection is successfully opened
            if not self.serial_connection.is_open:
                self.serial_connection.open()

            self.serial_connection.flush()

            self.serial_connection_signal.emit(self.serial_connection)

            self.update_port_info(port)


            # Gather the current settings
            config_data = {
                'port': self.comboBox_port.currentText(),
                'speed': self.comboBox_speed.currentText(),
                'data_bits': self.comboBox_data.currentText(),
                'stop_bits': self.comboBox_stop_bits.currentText(),
                'flow_control': self.comboBox_flow_control.currentText(),
                'transmit_delay': self.lineEdit.text()  # Get the transmit delay from the QLineEdit
            }

            # save current connection info
            self.save_temp_json(config_data)

            QMessageBox.information(self, "Connected", f"Connected to {port} at {baud_rate} baud.")


        except serial.SerialException as e:

            QMessageBox.warning(self, "Connection Error", f"Could not connect to {port}: {e}")
            self.serial_connection = None  # Ensure that serial_connection is reset on failure

    def save_temp_json(self, config_data):
        # Use the temp_filename from the main window
        if self.temp_filename:
            with open(self.temp_filename, 'w') as temp_file:
                json.dump(config_data, temp_file)
            print(f"Temporary JSON file saved at: {self.temp_filename}")
        

    def load_temp_json(self, temp_filename):
        if temp_filename and os.path.exists(temp_filename):
            with open(temp_filename, 'r') as temp_file:
                return json.load(temp_file)
        print("Temporary file does not exist.")
        return None


    def update_port_info(self,port):

        # Clear any previous widgets in the scroll area
        layout = self.scrollArea_port_info.layout()

        for i in reversed(range(layout.count())):
            widget = layout().itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()


        # Create a layout to add to the scroll area
        layout = QVBoxLayout()


        for p in serial.tools.list_ports.comports():
            if p.device == port:
                port_info = f"Port: {p.device}\nDescription: {p.description}\nHardware ID: {p.hwid}\n"
                label = QLabel(port_info)
                layout.addWidget(label)
                break

        # Set the layout to the scroll area widget
        widget = QWidget()
        widget.setLayout(layout)
        self.scrollArea_port_info.setWidget(widget)
