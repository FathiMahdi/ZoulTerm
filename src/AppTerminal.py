
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
import json
import os
from send_Command import Ui_Dialog

 


class TerminalSettingsDialog(QDialog):

    def __init__(self,parent=None, current_font=None, current_font_size=None, current_bg_color=None, current_text_color=None, current_encoding=None, enable_timestamp=False):
        super(TerminalSettingsDialog, self).__init__(parent)
        
        self.setWindowTitle("Terminal Display Settings")

        # temporary port info : 
        self.temp_filename = "terminal_set_temp.json" 

        # Store the parent and current settings for later use
        self.parent_window = parent
        self.bg_color = current_bg_color or QColor(0, 0, 0)  # Default black
        self.text_color = current_text_color or QColor(0, 255, 0)  # Default green
        self.font = current_font or QFont("Courier New")
        self.font_size = current_font_size or 13
        self.encoding = current_encoding or "UTF-8"
        self.enable_timestamp = enable_timestamp

        self.font.setPointSize(13)

        # Create the layout
        # layout = QVBoxLayout()
        layout = QGridLayout()

        # Font Settings
        self.font_combo = QFontComboBox(self)
        self.font_combo.setCurrentFont(self.font)
        self.font_combo.setFont(self.font)
        self.font_size_edit = QLineEdit(self)
        self.font_size_edit.setFont(self.font)
        self.font_size_edit.setText(str(self.font_size))


        # Add Font Combo and Font Size Edit widgets to grid layout
        layout.addWidget(QLabel("Font:"), 0, 0)  # Row 0, Column 0
        layout.addWidget(self.font_combo, 0, 1)  # Row 0, Column 1
        layout.addWidget(QLabel("Size:"), 1, 0)  # Row 1, Column 0
        layout.addWidget(self.font_size_edit, 1, 1)  # Row 1, Column 1

        # Background Color Button
        self.bg_color_button = QPushButton("Background Color", self)
        self.bg_color_button.setFont(self.font)
        self.bg_color_button.clicked.connect(self.select_background_color)
        layout.addWidget(self.bg_color_button, 2, 0, 1, 2)  # Span across 2 columns

        # Text Color Button
        self.text_color_button = QPushButton("Text Color", self)
        self.text_color_button.setFont(self.font)
        self.text_color_button.clicked.connect(self.select_text_color)
        layout.addWidget(self.text_color_button, 3, 0, 1, 2)  # Span across 2 columns

        # Encoding Combo Box
        self.encoding_combo = QComboBox(self)
        self.encoding_combo.addItems(["UTF-8", "ASCII", "ISO-8859-1", "Windows-1252"])
        self.encoding_combo.setFont(self.font)
        layout.addWidget(QLabel("Encoding:"), 4, 0)
        layout.addWidget(self.encoding_combo, 4, 1)


        # Timestamp Checkbox
        self.timestamp_checkbox = QCheckBox("Enable Timestamp", self)
        self.timestamp_checkbox.setChecked(self.enable_timestamp)
        self.timestamp_checkbox.setFont(self.font)
        layout.addWidget(self.timestamp_checkbox, 5, 0, 1, 2)  # Span across 2 columns


        # Save Button
        self.save_button = QPushButton("Set", self)
        self.save_button.setFont(self.font)
        self.save_button.clicked.connect(self.set_settings)
        layout.addWidget(self.save_button, 6, 0, 1, 2)  # Span across 2 columns

        # Set the layout for the dialog
        self.setLayout(layout)

        if self.temp_filename:
             # load tempory info if any
            TempConf = self.LoadTempTerminalSettings(self.temp_filename)
            if TempConf is not None:
                self.timestamp_checkbox.setChecked(TempConf.get("timestamp_checkbox", False))


    def select_background_color(self):
        color = QColorDialog.getColor(self.bg_color, self)
        if color.isValid():
            self.bg_color = color

    def select_text_color(self):
        """Open color dialog to choose text color"""
        color = QColorDialog.getColor(self.text_color, self)
        if color.isValid():
            self.text_color = color

    def set_settings(self):
        """Emit the selected settings for font, colors, encoding, and wrap"""
        font = self.font_combo.currentFont()
        font_size = int(self.font_size_edit.text())  # Convert to integer
        encoding = self.encoding_combo.currentText()
        enable_timestamp = self.timestamp_checkbox.isChecked()

        self.SaveTempTerminalSettings()

        # Send the selected settings to the main window 
        self.apply_terminal_settings(font, font_size, self.bg_color, self.text_color, encoding, enable_timestamp)

        # Close dialog
        self.accept()

    def SaveTempTerminalSettings(self):
        # Gather the current settings
        config_data = {
            'timestamp_checkbox': self.timestamp_checkbox.isChecked(),
        }        
        if self.temp_filename:
            with open(self.temp_filename, 'w') as temp_file:
                json.dump(config_data, temp_file)
            print(f"Temporary JSON file saved at: {self.temp_filename}")

    
    def LoadTempTerminalSettings(self,temp_filename):
        if temp_filename and os.path.exists(temp_filename):
            with open(temp_filename, 'r') as temp_file:
                return json.load(temp_file)
        print("Temporary file does not exist.")
        return None

    def apply_terminal_settings(self,font, font_size, bg_color, text_color, encoding, enable_timestamp):
    
        self.parent_window.apply_terminal_display_settings(font, font_size, bg_color, text_color, encoding, enable_timestamp)





class DialogCommand(QDialog,Ui_Dialog):  
    def __init__(self,serial_port):
        super(DialogCommand, self).__init__()
        self.setupUi(self)

        self.port = serial_port
        self.listWidget_command_list.itemSelectionChanged.connect(self.fill_command_from_selection)
        
        self.pushButton_send_at_command.clicked.connect(self.send_at_command)

        self.toolButton_add_command.clicked.connect(self.add_new_command)

    def fill_command_from_selection(self):

        selected_items = self.listWidget_command_list.selectedItems()

        if selected_items:
            selected_item_text = selected_items[0].text()
            self.lineEdit_selected_command.setText(selected_item_text)



    def add_new_command(self):

        new_command = self.lineEdit_new_command.text()

        if(new_command):
            self.listWidget_command_list.addItem(new_command)
            self.lineEdit_new_command.clear()
        else:
            QMessageBox.warning(self, "Input Error", "Command cannot be empty.")

    def send_at_command(self):

        data = self.lineEdit_selected_command.text()

        if self.port == None:
            QMessageBox.warning(self, "Send Command Error", f"Port is not connected")

        else:
            if data:
                try:
                    if self.port.isOpen():
                        self.port.write(data.encode('utf-8') + b"\r\n")
                except Exception as e:
                    QMessageBox.warning(self, "Send Command Error", f"Cannot send AT command: {e}")