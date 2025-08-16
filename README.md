# 🔌 ZoulTerm

### Version: 0.0.2  
**ZoulTerm** is an open-source, Qt-based serial monitor built for developers working with microcontrollers, embedded systems, and development boards. Inspired by tools like **Tera Term** and **RealTerm**, ZoulTerm provides a lightweight, modern, and Linux-friendly alternative.

---

## 🚀 Motivation

Serial terminals are essential for firmware debugging and device communication. Unfortunately, many popular tools are Windows-centric or lack modern interfaces. **ZoulTerm** fills this gap by offering a Qt-powered serial monitor with a clean GUI and strong Linux support, with cross-platform plans underway.

---

## ✨ Features

- Real-time serial data monitoring
- Auto-detection of available serial ports
- Hex / ASCII / raw display modes
- Logging to text files
- Send custom commands or text files (e.g., AT commands)

---

## 🛠 Installation

### 🐧Linux

#### 🧱 Build

```bash
git clone https://github.com/FathiMahdi/ZoulTerm.git
cd ZoulTerm
chmod +x setup.sh
bash setup.sh
```
#### 📦 Package

go to release page and download the latest .deb version

```bash
dbkg -i zoulterm_[version]
```

for example for beta version
```bash

dbkg -i zoulterm_0.0.2
```

> 📋 Note: This will automatically create a python virtual environment folder

> 📦 Dependencies: Ensure you have `qtbase5-dev`, `qtserialport5-dev`, and `pyserial` are installed.

### Windows / macOS

> 🧪 Support for Windows and macOS is planned for future versions.

---

## 🧪 Usage

After building, launch ZoulTerm with:

```bash
./dist/ZoulTerm
```

### ⚙️ Basic Operations

- Select the available serial port
- Set baud rate and serial parameters
- View real-time incoming data
- Send manual or file-based commands

---


## 📑 TODO

- Adding themes
- Emoji support
- Ascci color support

---
## 🤝 Contributing

We welcome contributions! Whether it's bug fixes, new features, or suggestions:

- Fork the repo and create a feature branch
- Open a pull request
- Report issues or request features via GitHub Issues

> Consider following a [contribution guideline](CONTRIBUTING.md) if one is added.

---

## 🧾 License

ZoulTerm is licensed under the **[GNU LGPL v3](LICENSE.txt)**.  
This allows you to use, modify, and redistribute the software under the terms of the license.

> Note: This project uses the Qt framework under the LGPL v3 license.