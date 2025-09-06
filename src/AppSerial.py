
from PyQt5.QtCore import QThread, pyqtSignal


class SerialReaderThread(QThread):
 
    new_data_signal = pyqtSignal(str)

    def __init__(self, serial_connection):
        super().__init__()
        self.serial_connection = serial_connection

    def run(self):

        # Reads data from the serial port and emits the new data
        while self.serial_connection.isOpen():
            
            try:
                # Read data line by line
                data = self.serial_connection.readline()  
                
                try:
                    decoded_data = data.decode('ascii', errors='replace')
                except Exception as e:
                    print(f"Error decoding data: {e}")
                    continue  # Skip this line if decoding fails

                if decoded_data:

                    self.new_data_signal.emit(decoded_data) 

            except Exception as e:
                print(f"Error reading data: {e}")
                break