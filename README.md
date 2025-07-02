# Nidec Commander CDE Control

A comprehensive Python GUI application for controlling and monitoring Nidec Commander CDE drives via Modbus RTU.

## ✨ Features

- **Multi-language Support**: Interface available in multiple languages (English, Italian, Spanish, Portuguese, German, French, Dutch, Russian, Chinese, Japanese, Arabic)
- **Drive Control**:
  - Connect to Nidec Commander CDE drives via RS-485/Modbus RTU
  - Control motor speed and direction
  - Start/Stop the drive
  - Real-time monitoring of drive status and diagnostics
  - Fault detection and reset functionality
- **User Interface**:
  - Modern, tabbed interface
  - Status bar with real-time information
  - Responsive design
  - Dark/Light theme support
- **Diagnostics**:
  - Real-time monitoring of drive parameters
  - Fault history and logging
  - System status indicators

## 🚀 Requirements

- Python 3.8 or higher
- PyQt5 >= 5.15.9
- pyserial >= 3.5
- pymodbus >= 3.5.4
- QScintilla >= 2.14.1
- python-dotenv >= 1.0.0

## 🛠 Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Nsfr750/nidec-commander-cde.git
   cd nidec-commander-cde
   ```

2. Create and activate a virtual environment (recommended):

   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Unix or MacOS:
   # source venv/bin/activate
   ```

3. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

## 🚦 Quick Start

1. Connect your Nidec Commander CDE drive to your computer via RS-485 adapter

2. Launch the application:

   ```bash
   python main.py
   ```

3. Select the appropriate COM port and baud rate
4. Click 'Connect' to establish communication with the drive

## 📝 License

This project is licensed under the GPL3 License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Installation

1. Clone this repository or download the source code
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Connect your computer to the Nidec Commander CDE drive using a USB-to-RS485 converter
2. Run the application:
   ```
   python main.py
   ```
3. Select the correct COM port from the dropdown menu
4. Click "Connect" to establish communication with the drive
5. Use the interface to control and monitor the drive

## Connection Settings

- Baud Rate: 9600
- Data Bits: 8
- Parity: Even
- Stop Bits: 1
- Modbus Address: 1 (default, can be changed in drive parameters)

## Important Notes

- This software is provided as-is without any warranty
- Always ensure proper electrical connections and safety measures when working with motor drives
- The default register addresses are based on typical Nidec drive configurations but may need adjustment for your specific model
- Refer to the Nidec CDE 400 Commander manual for detailed information about parameters and register addresses

