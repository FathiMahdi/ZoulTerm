echo "Install requirements"
pip3 install -r requirements.txt
rm -r build
rm -r dist
echo "Convert UI files"
sh ui_convrt.sh
echo "generate resource files" 
sh rc_convert.sh
pyinstaller -w -F --hidden-import=PyQt5.QtSvg --name ZoulTerm main.py
