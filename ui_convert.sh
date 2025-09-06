rm src/ZoulTerm_ui.py src/send_Command.py src/ConnectDevice.py src/about_zoulTerm.py src/serial_viewer.py src/terminal_settings_ui.py

pyuic5 -x assets/UI/ZoulTerm.ui -o src/ZoulTerm_ui.py
pyuic5 -x assets/UI/send_Command.ui -o src/send_Command.py
pyuic5 -x assets/UI/ConnectDevice.ui -o src/ConnectDevice.py
pyuic5 -x assets/UI/about_zoulTerm.ui -o src/about_zoulTerm.py
pyuic5 -x assets/UI/serial_viewer.ui -o src/serial_viewer.py
pyuic5 -x assets/UI/terminal_settings.ui -o src/terminal_settings_ui.py