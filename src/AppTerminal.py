from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
import json
import os
from send_Command import Ui_Dialog 
from terminal_settings_ui import Ui_DialogTerminalSettings


def user_config_path(filename: str) -> str:
    """
    Return a per-user config path for zoulterm.
    Example: ~/.config/zoulterm/terminal_set_temp.json
    """
    base = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
    cfg_dir = os.path.join(base, "zoulterm")
    os.makedirs(cfg_dir, exist_ok=True)
    return os.path.join(cfg_dir, filename)

def qcolor_to_hex(col: QColor) -> str:
    return col.name() if isinstance(col, QColor) else "#000000"

def hex_to_qcolor(hexstr: str) -> QColor:
    try:
        return QColor(hexstr)
    except Exception:
        return QColor(0, 0, 0)

class TerminalSettingsDialog(QDialog, Ui_DialogTerminalSettings):
    def __init__(self, parent=None, current_font=None, current_font_size=None,
                 current_bg_color=None, current_text_color=None, current_encoding=None,
                 enable_timestamp=False):
        # super().__init__(parent)
        super(TerminalSettingsDialog, self).__init__()
        self.setupUi(self)

        self.parent_window = parent
        self.temp_filename = os.path.expanduser("~/.zoulterm_terminal_settings.json")

        # defaults
        self.bg_color = current_bg_color or QColor(0, 0, 0)
        self.text_color = current_text_color or QColor(50, 255, 0)
        self.font = current_font or QFont("Courier")
        self.font_size = current_font_size or 13
        self.encoding = current_encoding or "UTF-8"
        self.enable_timestamp = enable_timestamp

        # initialize widgets
        self.fontComboBox_terminal.setCurrentFont(self.font)
        self.spinBox_fontSize.setValue(self.font_size)

        idx = self.comboBox_encoding.findText(self.encoding)
        if idx >= 0:
            self.comboBox_encoding.setCurrentIndex(idx)

        self.checkBox_enable_timestamp.setChecked(self.enable_timestamp)

        # update previews
        self._update_color_previews()

        # signals
        self.bg_color_button.clicked.connect(self.select_background_color)
        self.text_color_button.clicked.connect(self.select_text_color)
        self.pushButton_apply.clicked.connect(self.set_settings)

        # load temp saved settings if available
        try:
            data = self.LoadTempTerminalSettings()
            if data:
                self.fontComboBox_terminal.setCurrentFont(QFont(data.get("font_name", "Courier")))
                self.spinBox_fontSize.setValue(data.get("font_size", 13))
                self.bg_color = hex_to_qcolor(data.get("bg_color", "#000000"))
                self.text_color = hex_to_qcolor(data.get("text_color", "#00FF00"))
                idx = self.comboBox_encoding.findText(data.get("encoding", "UTF-8"))
                if idx >= 0:
                    self.comboBox_encoding.setCurrentIndex(idx)
                self.checkBox_enable_timestamp.setChecked(data.get("timestamp_checkbox", False))
                self._update_color_previews()
        except Exception as e:
            print(f"Warning: could not load temp terminal settings: {e}")

    def _update_color_previews(self):
   
        self.bg_preview.setStyleSheet(f"background:{qcolor_to_hex(self.bg_color)};")
        self.text_preview.setStyleSheet(f"background:{qcolor_to_hex(self.text_color)};")

    def select_background_color(self):
        color = QColorDialog.getColor(self.bg_color, self, "Select background color")
        if color.isValid():
            self.bg_color = color
            self._update_color_previews()

    def select_text_color(self):
        color = QColorDialog.getColor(self.text_color, self, "Select text color")
        if color.isValid():
            self.text_color = color
            self._update_color_previews()

    def SaveTempTerminalSettings(self, font=None, font_size=None, bg_color=None, text_color=None, encoding=None, timestamp_checkbox=False):
        data = {
            "font_name": font.family(),
            "font_size": font_size,
            "bg_color": qcolor_to_hex(bg_color),
            "text_color": qcolor_to_hex(text_color),
            "encoding": encoding,
            "timestamp_checkbox": timestamp_checkbox
        }
        with open(self.temp_filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def set_settings(self):
        font = self.fontComboBox_terminal.currentFont()
        text = str(self.spinBox_fontSize.value())
        try:
            font_size = int(text) if text else self.font.pointSize() or 13
            # Clamp to validator range
            font_size = max(6, min(72, font_size))
        except ValueError:
            font_size = self.font.pointSize() or 13

        encoding = self.comboBox_encoding.currentText()
        enable_timestamp = self.checkBox_enable_timestamp.isChecked()

        # Save temporary settings
        try:
            self.SaveTempTerminalSettings(font, font_size, self.bg_color, self.text_color, encoding, enable_timestamp)
        except Exception as e:
            QMessageBox.warning(self, "Save Error", f"Could not save temp settings: {e}")

        # Send the selected settings to the main window only if parent exists and implements expected call
        try:
            if self.parent_window and hasattr(self.parent_window, "apply_terminal_display_settings"):
                self.apply_terminal_settings(font, font_size, self.bg_color, self.text_color, encoding, enable_timestamp)
            else:
                print("No parent or ttings not present; settings not applied to main window.")
        except Exception as e:
            QMessageBox.warning(self, "Apply Error", f"Could not apply settings to main window: {e}")


        # Close dialog
        self.accept()


    def LoadTempTerminalSettings(self):
        if os.path.exists(self.temp_filename):
            with open(self.temp_filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def apply_terminal_settings(self, font, font_size, bg_color, text_color, encoding, enable_timestamp):
       
        if self.parent_window and hasattr(self.parent_window, "apply_terminal_display_settings"):
            try:
                self.parent_window.apply_terminal_display_settings(font, font_size, bg_color, text_color, encoding, enable_timestamp)
            except Exception as e:
                print(f"Error while applying terminal settings to parent: {e}")
        else:
            print("Parent window not present or does not support apply_terminal_display_settings.")


class DialogCommand(QDialog, Ui_Dialog):
    def __init__(self, serial_port):
        super(DialogCommand, self).__init__()
        self.setupUi(self)

        self.port = serial_port
        # connect signals safely — only if widgets are present
        try:
            self.listWidget_command_list.itemSelectionChanged.connect(self.fill_command_from_selection)
            self.pushButton_send_at_command.clicked.connect(self.send_at_command)
            self.toolButton_add_command.clicked.connect(self.add_new_command)
            self.pushButton_save_command_list.clicked.connect(self.SaveCommandHAndler)
            self.pushButton_load_command_list.clicked.connect(self.LoadCommandHAndler)
        except Exception:
            # UI might be missing widgets if Ui_Dialog changed
            pass

    def fill_command_from_selection(self):
        selected_items = self.listWidget_command_list.selectedItems()
        if selected_items:
            selected_item_text = selected_items[0].text()
            self.lineEdit_selected_command.setText(selected_item_text)

    def add_new_command(self):
        new_command = self.lineEdit_new_command.text().strip()
        if new_command:
            self.listWidget_command_list.addItem(new_command)
            self.lineEdit_new_command.clear()
        else:
            QMessageBox.warning(self, "Input Error", "Command cannot be empty.")


    def LoadCommandHAndler(self):

        file_name, _ = QFileDialog.getOpenFileName(
            self, 
            "Load Commands", 
            "", 
            "Text Files (*.txt);;All Files (*)"
        )

        if file_name:
            try:
                with open(file_name, "r") as file:
                    lines = file.readlines()

                self.listWidget_command_list.clear()

                for line in lines:
                    command = line.strip()
                    if command:  
                        self.listWidget_command_list.addItem(command)

                QMessageBox.information(
                    self, 
                    "Load Commands", 
                    f"Commands loaded from: {file_name}"
                )

            except Exception as e:
                QMessageBox.warning(self, "Load Commands", f"Error loading file: {e}")
                print(f"Error loading file: {e}")

    def SaveCommandHAndler(self):

        command_list = []

        for i in range(self.listWidget_command_list.count()):
            item = self.listWidget_command_list.item(i)

            command_list.append(item.text())

        if len(command_list)<1:

            QMessageBox.warning(self, "save commands", f"No command to save")

        else:

            content = ""

            # Open a file save dialog
            self.FileName, _ = QFileDialog.getSaveFileName(self, "Save Commands", "", "Text Files (*.txt);;All Files (*)")

            # If the user selected a file
            if self.FileName:
                try:
                    for i in range(len(command_list)):

                        content+= str(command_list[i])+'\n'

                    # Open the file for writing
                    with open(self.FileName, 'w') as file:
                        file.write(content)

                    QMessageBox.information(self, "save commands", f"commands saved to: {self.FileName}")

                except Exception as e:
                    QMessageBox.warning(self, "save commands", f"Error saving file: {e}")
                    print(f"Error saving file: {e}") 


    def send_at_command(self):
        data = self.lineEdit_selected_command.text()
        if self.port is None:
            QMessageBox.warning(self, "Send Command Error", "Port is not connected")
            return

        if not data:
            QMessageBox.warning(self, "Send Command Error", "No command selected to send")
            return

        try:
            if hasattr(self.port, "isOpen") and callable(self.port.isOpen):
                open_state = self.port.isOpen()
            else:
                # fallback: assume pyserial-like object with 'open' attribute
                open_state = getattr(self.port, "open", False)

            if not open_state:
                QMessageBox.warning(self, "Send Command Error", "Selected serial port is not open.")
                return

            # Ensure CRLF termination (common for AT commands)
            payload = data.encode('utf-8')
            if not payload.endswith(b"\r") and not payload.endswith(b"\n"):
                payload = payload + b"\r\n"

            # Write to port
            self.port.write(payload)

            self.lineEdit_selected_command.clear()
            
        except Exception as e:
            QMessageBox.warning(self, "Send Command Error", f"Cannot send AT command: {e}")