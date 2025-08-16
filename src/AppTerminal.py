from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
import json
import os
from send_Command import Ui_Dialog 

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

class TerminalSettingsDialog(QDialog):

    def __init__(self, parent=None, current_font=None, current_font_size=None,
                 current_bg_color=None, current_text_color=None, current_encoding=None,
                 enable_timestamp=False):
        super(TerminalSettingsDialog, self).__init__(parent)

        self.setWindowTitle("Terminal Display Settings")

        # temporary port info : move file into user config
        self.temp_filename = user_config_path("terminal_set_temp.json")

        # Store the parent and current settings for later use
        self.parent_window = parent
        self.bg_color = current_bg_color or QColor(0, 0, 0)  # Default black
        self.text_color = current_text_color or QColor(0, 255, 0)  # Default green
        self.font = current_font or QFont("Courier")
        self.font_size = current_font_size or 13
        self.encoding = current_encoding or "UTF-8"
        self.enable_timestamp = enable_timestamp

        # Use a reasonable default font size
        self.font.setPointSize(self.font_size)

        # Create the layout
        layout = QGridLayout()

        # Font Settings
        self.font_combo = QFontComboBox(self)
        self.font_combo.setCurrentFont(self.font)
        self.font_combo.setFont(self.font)

        self.font_size_edit = QLineEdit(self)
        # Use QIntValidator to allow only reasonable font sizes
        int_validator = QIntValidator(6, 72, self)
        self.font_size_edit.setValidator(int_validator)
        self.font_size_edit.setFont(self.font)
        self.font_size_edit.setText(str(self.font.pointSize() or self.font_size))

        # Add Font Combo and Font Size Edit widgets to grid layout
        layout.addWidget(QLabel("Font:"), 0, 0)
        layout.addWidget(self.font_combo, 0, 1)
        layout.addWidget(QLabel("Size:"), 1, 0)
        layout.addWidget(self.font_size_edit, 1, 1)

        # Background Color Button with preview
        self.bg_color_button = QPushButton("Background Color", self)
        self.bg_color_button.setFont(self.font)
        self.bg_color_button.clicked.connect(self.select_background_color)
        layout.addWidget(self.bg_color_button, 2, 0)
        self.bg_preview = QLabel()
        self.bg_preview.setFixedSize(40, 20)
        self.bg_preview.setFrameShape(QFrame.Box)
        layout.addWidget(self.bg_preview, 2, 1)

        # Text Color Button with preview
        self.text_color_button = QPushButton("Text Color", self)
        self.text_color_button.setFont(self.font)
        self.text_color_button.clicked.connect(self.select_text_color)
        layout.addWidget(self.text_color_button, 3, 0)
        self.text_preview = QLabel()
        self.text_preview.setFixedSize(40, 20)
        self.text_preview.setFrameShape(QFrame.Box)
        layout.addWidget(self.text_preview, 3, 1)

        # Encoding Combo Box
        self.encoding_combo = QComboBox(self)
        self.encoding_combo.addItems(["UTF-8", "ASCII", "ISO-8859-1", "Windows-1252"])
        self.encoding_combo.setFont(self.font)
        layout.addWidget(QLabel("Encoding:"), 4, 0)
        layout.addWidget(self.encoding_combo, 4, 1)
        # Set current encoding
        idx = self.encoding_combo.findText(self.encoding)
        if idx >= 0:
            self.encoding_combo.setCurrentIndex(idx)

        # Timestamp Checkbox
        self.timestamp_checkbox = QCheckBox("Enable Timestamp", self)
        self.timestamp_checkbox.setChecked(self.enable_timestamp)
        self.timestamp_checkbox.setFont(self.font)
        layout.addWidget(self.timestamp_checkbox, 5, 0, 1, 2)

        # Save Button
        self.save_button = QPushButton("Set", self)
        self.save_button.setFont(self.font)
        self.save_button.clicked.connect(self.set_settings)
        layout.addWidget(self.save_button, 6, 0, 1, 2)

        self.setLayout(layout)

        # Apply previews for colors
        self._update_color_previews()

        # Load temporary info if any
        try:
            TempConf = self.LoadTempTerminalSettings(self.temp_filename)
            if TempConf is not None:
                # apply loaded fields safely
                self.timestamp_checkbox.setChecked(bool(TempConf.get("timestamp_checkbox", False)))
                font_name = TempConf.get("font_name")
                if font_name:
                    self.font_combo.setCurrentFont(QFont(font_name))
                fs = TempConf.get("font_size")
                if fs:
                    self.font_size_edit.setText(str(fs))
                bg_hex = TempConf.get("bg_color")
                if bg_hex:
                    self.bg_color = hex_to_qcolor(bg_hex)
                txt_hex = TempConf.get("text_color")
                if txt_hex:
                    self.text_color = hex_to_qcolor(txt_hex)
                enc = TempConf.get("encoding")
                if enc:
                    idx = self.encoding_combo.findText(enc)
                    if idx >= 0:
                        self.encoding_combo.setCurrentIndex(idx)
                self._update_color_previews()
        except Exception as e:
            # non-fatal: continue with defaults
            print(f"Warning: could not load terminal settings: {e}")

    def _update_color_previews(self):
        """Update the small preview swatches for background/text color."""
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

    def set_settings(self):
        """Emit the selected settings for font, colors, encoding, and timestamp."""
        font = self.font_combo.currentFont()
        text = self.font_size_edit.text()
        try:
            font_size = int(text) if text else self.font.pointSize() or 13
            # Clamp to validator range
            font_size = max(6, min(72, font_size))
        except ValueError:
            font_size = self.font.pointSize() or 13

        encoding = self.encoding_combo.currentText()
        enable_timestamp = self.timestamp_checkbox.isChecked()

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
                print("No parent or apply_terminal_display_settings not present; settings not applied to main window.")
        except Exception as e:
            QMessageBox.warning(self, "Apply Error", f"Could not apply settings to main window: {e}")

        # Close dialog
        self.accept()

    def SaveTempTerminalSettings(self, font=None, font_size=None, bg_color=None, text_color=None, encoding=None, timestamp_checkbox=None):
        # Gather the current settings (use provided or current dialog state)
        data = {
            "font_name": (font.family() if font else self.font_combo.currentFont().family()),
            "font_size": (font_size if font_size is not None else int(self.font_size_edit.text() or 13)),
            "bg_color": qcolor_to_hex(bg_color if bg_color else self.bg_color),
            "text_color": qcolor_to_hex(text_color if text_color else self.text_color),
            "encoding": encoding if encoding else self.encoding_combo.currentText(),
            "timestamp_checkbox": bool(timestamp_checkbox if timestamp_checkbox is not None else self.timestamp_checkbox.isChecked())
        }
        if self.temp_filename:
            try:
                with open(self.temp_filename, 'w', encoding='utf-8') as temp_file:
                    json.dump(data, temp_file, indent=2)
                # debug print
                print(f"Temporary JSON file saved at: {self.temp_filename}")
            except Exception as e:
                # bubble up so callers can warn
                raise

    def LoadTempTerminalSettings(self, temp_filename):
        if temp_filename and os.path.exists(temp_filename):
            try:
                with open(temp_filename, 'r', encoding='utf-8') as temp_file:
                    return json.load(temp_file)
            except Exception as e:
                print(f"Error loading temp file: {e}")
                return None
        # no file found -> return None
        return None

    def apply_terminal_settings(self, font, font_size, bg_color, text_color, encoding, enable_timestamp):
        # Delegate to parent window's method if available
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