
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QBuffer, QByteArray
from PyQt5.QtCore import QDateTime
from PyQt5 import uic
import json
from PyQt5 import QtCore, QtGui, QtWidgets
import os
import re
from ZoulTerm_ui import Ui_MainWindow
from evaq_config_main_rc import *

from  terminal_settings_ui import *
from AppAbout      import *
from AppTerminal   import *
from AppConnection import *
from AppSerial     import *
from AppSerialViewer import *



class MyWindow(QMainWindow, Ui_MainWindow): 

    def __init__(self):

        super().__init__()

        self.setupUi(self)

        # Status indicator as a colored circle
        self.connection_status_label = QLabel("Disconnected")
        self.connection_status_label.setStyleSheet("""
            QLabel {
                color: red;
                font-weight: bold;
                font-size: 16px;
            }
        """)

        # Add to status bar
        status_bar = QStatusBar(self)
        status_bar.addWidget(self.connection_status_label)
        self.setStatusBar(status_bar)

        # disable auto scroll
        self.plainTextEdit_terminal.moveCursor(QTextCursor.Start)
        self.plainTextEdit_terminal.ensureCursorVisible()

        # apply terminal settings when start
        self.set_default_terminal_settings()

        # Set the status bar for the window
        self.setStatusBar(status_bar)

        self.temp_filename       = "config_temp.json" 
        self.serial_connection   = None 
        self.decoded_serial_data = ""
        self.isLight             = True
        self.enable_timestamp    = False
        self.pause_serial        = False  
        self.isTreeAdjested      = False
        self.isLogTriggered      = False
        self.MSGFormat           = 'Text'
        self.MonitorFormat       = 'Text'
        self.LogFileName         = ''
        self.EnableAutoScroll    = False
        self.TerminalSearchTriggered = False
        self.actionAbout.triggered.connect(About_clicked)
        self.actionConnect.triggered.connect(self.Connect_clicked)
        self.actionShowGraph.triggered.connect(self.Graph_clicked)
        self.actionClear_terminal.triggered.connect(self.clear_terminal)
        self.pushButton_terminal_clear.clicked.connect(self.clear_terminal)
        self.actionlog_terminal.triggered.connect(self.log_terminal)
        self.actionSendCommand.triggered.connect(self.Command_clicked)
        self.pushButton_terminal_log.clicked.connect(self.log_terminal)
        self.pushButton_disconnect.clicked.connect(self.disconnect_serial)
        self.pushButton_connect.clicked.connect(self.Connect_clicked)
        self.actionDisconnect.triggered.connect(self.disconnect_serial)
        self.pushButton_search.clicked.connect(self.TriggerTerminalSearch)
        self.pushButton_timestamp.clicked.connect(self.TriggerTimeStamp)
        self.pushButton_SendMSG.clicked.connect(self.send_msg)
        self.pushButton_scroll.clicked.connect(self.ScrollHandler)
        self.pushButton_pause.clicked.connect(self.PauseSerial)
        self.pushButton_terminal_send_command.clicked.connect(self.Command_clicked)
        self.pushButton_terminal_settings.clicked.connect(self.open_terminal_settings)
        self.actionTerminal_settings.triggered.connect(self.open_terminal_settings)
        self.toolButton_search_up.clicked.connect(self.navigate_up)
        self.toolButton_search_down.clicked.connect(self.navigate_down)
        self.actionSetupConnection.triggered.connect(self.SetupConnection_clicked)
        # self.pushButton_apply.clicked.connect(self.set_terminal_settings)


        self.reconnect_timer = QTimer(self)
        self.reconnect_timer.timeout.connect(self.update_config_check)
        self.reconnect_timer.timeout.connect(self.check_serial_connection)
        self.reconnect_timer.timeout.connect(self.search_terminal)
        self.reconnect_timer.start(500) 


   
    def TriggerTerminalSearch(self):

        if not self.TerminalSearchTriggered:
            self.TerminalSearchTriggered = True

    def PauseSerial(self):

        if self.pushButton_pause.isChecked():
            self.pause_serial = True
        else:
            self.pause_serial = False

    def ScrollHandler(self):

        if not self.EnableAutoScroll:
            self.EnableAutoScroll = True
        else:
            self.EnableAutoScroll = False

   
    
            

    def TriggerTimeStamp(self):

        if self.pushButton_timestamp.isChecked():
            self.enable_timestamp=True

        else:
            self.enable_timestamp=False



    # pefore program close
    def closeEvent(self, event):
        
        if os.path.exists(self.temp_filename):
            self.delete_temp_json(self.temp_filename)
     
        event.accept()


    def navigate_down(self):

        if self.current_index < len(self.keyword_positions) - 1:
            self.current_index += 1
            self.highlight_current_occurrence()
        else:
            self.current_index = 0
            self.highlight_current_occurrence()

    ##############################################################################################

    def navigate_up(self):

        if self.current_index > 0 :
            self.current_index -= 1
            self.highlight_current_occurrence()
        else:
            self.current_index = len(self.keyword_positions) - 1
            self.highlight_current_occurrence()


    ##############################################################################################

    def highlight_current_occurrence(self):

        if self.current_index != -1:

            # Get the current occurrence's position
            keyword_position = self.keyword_positions[self.current_index]

            # Get the plain text from the QPlainTextEdit widget
            plain_text = self.plainTextEdit_terminal.toPlainText()

            # Move the cursor to the current keyword occurrence and select it
            cursor = self.plainTextEdit_terminal.textCursor()
            cursor.setPosition(keyword_position, QTextCursor.MoveAnchor)
            cursor.setPosition(keyword_position + len(self.lineEdit_search.text()), QTextCursor.KeepAnchor)

            # Set the cursor in the QPlainTextEdit to highlight the current occurrence
            self.plainTextEdit_terminal.setTextCursor(cursor)

        self.label_find_number.setText(f"{self.current_index+1} of {len(self.keyword_positions)}")


    ##############################################################################################

    def search_terminal(self):

        keyword = self.lineEdit_search.text()

        if not keyword:
            self.label_find_number.setText("")
            return


        if keyword == getattr(self, "last_search_keyword", "") and not self.TerminalSearchTriggered:
            return 

        # Update the last searched keyword
        self.last_search_keyword = keyword

        # Reset the positions list and current index
        self.keyword_positions = []
        self.current_index = -1

        # Clear any existing selection
        cursor = self.plainTextEdit_terminal.textCursor()
        cursor.clearSelection()
        self.plainTextEdit_terminal.setTextCursor(cursor)

        # Get the plain text
        plain_text = self.plainTextEdit_terminal.toPlainText()

        # Find all keyword occurrences
        index = plain_text.find(keyword)
        while index != -1:
            self.keyword_positions.append(index)
            index = plain_text.find(keyword, index + 1)

        # Select the first occurrence if found
        if self.keyword_positions:
            self.current_index = 0
            self.highlight_current_occurrence()

        if self.TerminalSearchTriggered:
            self.TerminalSearchTriggered = False
        


    ##############################################################################################

    def open_terminal_settings(self):
        dlg = TerminalSettingsDialog(
            parent=self,
            current_font=self.plainTextEdit_terminal.font(),
            current_font_size=self.plainTextEdit_terminal.font().pointSize(),
            current_bg_color=self.plainTextEdit_terminal.palette().color(QPalette.Base),
            current_text_color=self.plainTextEdit_terminal.palette().color(QPalette.Text),
            current_encoding=self.encoding,  
            enable_timestamp=self.enable_timestamp
        )
        dlg.exec_()

    ##############################################################################################

    def apply_terminal_display_settings(self, font, font_size, bg_color, text_color, encoding,enable_timestamp):
   
        self.plainTextEdit_terminal.setFont(QFont(font.family(), font_size))
        
        self.enable_timestamp = enable_timestamp  

        self.encoding = encoding

        self.plainTextEdit_terminal.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {bg_color.name()};
                color: {text_color.name()};
                font-weight: bold;
                padding: 4px;
                border-radius: 4px;
            }}
        """)
    ##############################################################################################


    def get_timestamp(self):
        current_time = QDateTime.currentDateTime()  # Get the current date and time
        month_number = current_time.date().month()
        month_name = current_time.date().shortMonthName(month_number)
        days = current_time.date().day()
        hours = current_time.time().hour()
        minutes = current_time.time().minute()
        seconds = current_time.time().second()
        mseconds = current_time.time().msec()

        # Format the timestamp as `d/h/m/sec`
        timestamp = f"{hours}:{minutes}:{seconds}:{mseconds}"
        return timestamp
    

    ##############################################################################################

    def delete_temp_json(self, temp_filename):
        """Deletes the temporary JSON file if it exists."""
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
            print(f"Temporary JSON file {temp_filename} has been deleted.")
        else:
            print(f"Temporary JSON file {temp_filename} does not exist, cannot delete.")
         

    def ansi_apply_format(self, codes):

        for code in codes:
            if code == 0:  # reset
                self.current_format = QTextCharFormat()
                fg = self.plainTextEdit_terminal.palette().color(QPalette.Text)
                bg = self.plainTextEdit_terminal.palette().color(QPalette.Base)
                self.current_format.setForeground(QBrush(fg))
                self.current_format.setBackground(QBrush(bg))

            elif 30 <= code <= 37:  # foreground
                colors = [Qt.black, Qt.red, Qt.green, Qt.yellow,
                        Qt.blue, Qt.magenta, Qt.cyan, Qt.white]
                self.current_format.setForeground(QBrush(colors[code - 30]))

            elif 40 <= code <= 47:  # background
                colors = [Qt.black, Qt.red, Qt.green, Qt.yellow,
                        Qt.blue, Qt.magenta, Qt.cyan, Qt.white]
                self.current_format.setBackground(QBrush(colors[code - 40]))

            elif code == 1:  # bold
                self.current_format.setFontWeight(QFont.Bold)

            elif code == 22:  # normal weight
                self.current_format.setFontWeight(QFont.Normal)


    def ansi_insert_text(self, text):
  
        cursor = self.plainTextEdit_terminal.textCursor()
        cursor.movePosition(QTextCursor.End)  # always append at the end

        pattern = re.compile(r'\x1b\[([0-9;]*)m')
        pos = 0
        had_code = False

        for match in pattern.finditer(text):
            # Insert plain text before ANSI code
            before = text[pos:match.start()]
            if before:
                cursor.insertText(before, self.current_format)

            # Parse and apply ANSI codes
            codes = [int(c) if c else 0 for c in match.group(1).split(';')]
            self.ansi_apply_format(codes)
            had_code = True
            pos = match.end()

        # Insert any remaining text
        if pos < len(text):
            cursor.insertText(text[pos:], self.current_format if had_code else QTextCharFormat())


    ##############################################################################################

    def clear_terminal(self):
        self.plainTextEdit_terminal.clear()

    ##############################################################################################
    
    def log_terminal(self):

        if self.pushButton_terminal_log.isChecked():

            self.isLogTriggered = True

        else:
            self.isLogTriggered = False

        if self.isLogTriggered:

            if self.serial_connection:

                if self.serial_connection.isOpen():
                    # Open a file save dialog
                    self.LogFileName, _ = QFileDialog.getSaveFileName(self, "Save Log", "", "Text Files (*.txt);;All Files (*)")

                    # If the user selected a file
                    if self.LogFileName:

                        try:

                            # Get the content from the text edit widget
                            content = self.plainTextEdit_terminal.toPlainText()

                            # Open the file for writing
                            with open(self.LogFileName, 'w') as file:
                                file.write(content)


                            QMessageBox.information(self, "Terminal log", f"Log saved to: {self.LogFileName}")

                        except Exception as e:
                            self.pushButton_terminal_log.setChecked(False)
                            self.isLogTriggered = False
                            print(f"Error saving file: {e}") 
                else:
                    self.pushButton_terminal_log.setChecked(False)
                    self.isLogTriggered = False
                    QMessageBox.warning(self, "Serial Log Error", f"Port is disconnected")                  
            else:
                self.pushButton_terminal_log.setChecked(False)
                self.isLogTriggered = False
                QMessageBox.warning(self, "Serial Log Error", f"Port is disconnected") 

        else:
            self.LogFileName = ''
    
    ##############################################################################################

    def send_msg(self):

        data = self.lineEdit_sendMSG.text()

        if self.serial_connection == None:
            QMessageBox.warning(self, "Error", f"Port is not connected")

        else:
            if data:
                try:
                    if self.serial_connection.isOpen():

                        format_type = self.comboBox_msgFormat.currentText()
                        
                        if format_type == 'Text':
                            self.serial_connection.write(data.encode('utf-8'))

                        elif format_type == 'Hex':
                            hex_data = data.replace(' ', '')
                            byte_data = bytes.fromhex(hex_data)
                            self.serial_connection.write(byte_data)


                    self.lineEdit_sendMSG.clear()

                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Error while sending msg {e}")


    def update_connection_status(self, is_connected):

        if is_connected:
            self.connection_status_label.setText("● Connected")
            self.connection_status_label.setStyleSheet("color: green; font-weight: bold; font-size: 16px;")
        else:
            self.connection_status_label.setText("● Disconnected")
            self.connection_status_label.setStyleSheet("color: red; font-weight: bold; font-size: 16px;")   

    ##############################################################################################


    def disconnect_serial(self):
    
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            self.serial_connection = None
            self.update_connection_status(False)  
            QMessageBox.information(self, "Disconnected", "Disconnected from the serial port.")
        else:
            QMessageBox.warning(self, "Disconnected", "No device connected")


    ##############################################################################################

    def check_serial_connection(self): 
        """Check if the serial connection is still open, and reconnect if it's lost"""
        if self.serial_connection is None or not self.serial_connection.isOpen():
            self.update_connection_status(False)
            # self.reconnect_serial()
        else:
            self.update_connection_status(True)

    ##############################################################################################

    def reconnect_serial(self):

        try:
            self.serial_connection.open()

        except Exception as e:
            print("Cannot reconnect to port {}",e)

    def set_default_terminal_settings(self):

        temp_filename = os.path.expanduser("~/.zoulterm_terminal_settings.json")

        try:
            if os.path.exists(temp_filename):
                with open(temp_filename, 'r', encoding='utf-8') as f:
                    data =  json.load(f)
        
                if data:
                    font = (QFont(data.get("font_name", "Courier")))
                    font_size = data.get("font_size", 13)
                    bg_color = hex_to_qcolor(data.get("bg_color", "#000000"))
                    text_color = hex_to_qcolor(data.get("text_color", "#00FF00"))
                    encoding = data.get("encoding", "UTF-8")
                    timestamp = data.get("timestamp_checkbox", False)

                    self.apply_terminal_display_settings(font,font_size,bg_color,text_color,encoding,timestamp)
            else :
                self.apply_terminal_display_settings(QFont("Courier"),13,hex_to_qcolor("#000000"),hex_to_qcolor("#00FF00"),"UTF-8",False)

        except Exception as e:
            print(f"Error: {e}")
            self.apply_terminal_display_settings(QFont("Courier"),13,hex_to_qcolor("#000000"),hex_to_qcolor("#00FF00"),"UTF-8",False) 

    ##############################################################################################

    def on_serial_connected(self, serial_connection):
        
        self.serial_connection = serial_connection
        self.update_connection_status(True)

    
        self.serial_reader_thread = SerialReaderThread(self.serial_connection)
        self.serial_reader_thread.new_data_signal.connect(self.on_new_serial_data)  
        self.serial_reader_thread.start()

    ##############################################################################################

    def on_new_serial_data(self, data):
            
        try:
            self.decoded_serial_data = data

            if self.comboBox_TerminalViewMode.currentText() == 'Hex':
                
                if isinstance(data, bytes):
                    data = ' '.join(f'{b:02X}' for b in data)
                else:
                    data = ' '.join(f'{ord(c):02X}' for c in data)

            if self.pause_serial==False:

                if self.enable_timestamp:

                    timestamp = self.get_timestamp()
                    data_with_timestamp = f"-> {timestamp} : {data}"
                    self.ansi_insert_text(data_with_timestamp)
                    # self.plainTextEdit_terminal.appendPlainText(data_with_timestamp)
         
                    if self.EnableAutoScroll :
                        self.plainTextEdit_terminal.moveCursor(QTextCursor.End)
                        self.plainTextEdit_terminal.ensureCursorVisible()

                else:
                    self.ansi_insert_text(data)
                    # self.plainTextEdit_terminal.appendPlainText(data)

               
                    if self.EnableAutoScroll :
                        self.plainTextEdit_terminal.moveCursor(QTextCursor.End)
                        self.plainTextEdit_terminal.ensureCursorVisible()
       

                if self.isLogTriggered and self.LogFileName:

                    with open(self.LogFileName, 'a+') as file:
                                if self.enable_timestamp:
                                    file.write(data_with_timestamp)
                                else:
                                    file.write(data)
                
                

                
        except Exception as e:
            print(f"Error processing serial data: {e}")


    ##############################################################################################

    def update_config_check(self):

        # Load icons (or use emojis)
        connected_icon = QIcon(':/resources/Assets/icons/connected.png')
        disconnected_icon = QIcon(':/resources/Assets/icons/disconnected.png')
        connected_emoji = "✅"
        disconnected_emoji = "❌"

        # Define a helper function to check the value status
        def check_value(value):
            if value == "Not Defined" or value == "" or value == "False":
                return disconnected_emoji  # ❌ if not defined
            return connected_emoji  # ✅ if defined
    

    ##############################################################################################


    # serial port connect window
    def Connect_clicked(self):
        connect = DialogConnectDevice(temp_filename=self.temp_filename)
        connect.serial_connection_signal.connect(self.on_serial_connected)
        connect.connect_to_port() 
         
        # Ensure the connection is successfully opened

    def Graph_clicked(self):

        if self.serial_connection and self.serial_connection.is_open:

            self.graph = DialogShowGraph()
            self.graph.show()

            if hasattr(self, "serial_reader_thread"):
                self.serial_reader_thread.new_data_signal.connect(self.graph.handle_serial_line)

        else:
            QMessageBox.warning(self, "Serial Viewer", "No device connected")

        # graph.serial_connection_signal.connect(self.on_serial_connected)
        # graph.exec_()
            

    ##############################################################################################
        
    def SetupConnection_clicked(self):
        connect = DialogConnectDevice(temp_filename=self.temp_filename)
        connect.serial_connection_signal.connect(self.on_serial_connected) 
        connect.exec_()

    ##############################################################################################


    # serial command send window
    def Command_clicked(self):
        command = DialogCommand(serial_port=self.serial_connection)
        command.exec_()


def About_clicked(self):
    dialog = DialogAbout()
    dialog.exec_()