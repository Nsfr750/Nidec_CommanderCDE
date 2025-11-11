# User Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [User Interface Overview](#user-interface-overview)
3. [Connecting to a Drive](#connecting-to-a-drive)
4. [Monitoring Drive Status](#monitoring-drive-status)
5. [Controlling the Drive](#controlling-the-drive)
6. [Parameter Configuration](#parameter-configuration)
7. [Data Logging](#data-logging)
8. [Saving and Loading Configurations](#saving-and-loading-configurations)
9. [Troubleshooting](#troubleshooting)

## Getting Started

### System Requirements

- Windows 10/11 (64-bit)
- Python 3.8 or higher
- USB-to-Serial adapter (if using USB connection)
- Nidec CDE series drive

### Installation

1. Download and install Python from [python.org](https://www.python.org/downloads/)
2. Install required packages:

   ```
   pip install -r requirements.txt
   ```

3. Launch the application:

   ```
   python main.py
   ```

## User Interface Overview

The main window is divided into several sections:

1. **Menu Bar** - Access to file operations, view options, and help
2. **Connection Panel** - Configure and manage drive connections
3. **Main Tabs** - Different functional areas of the application
   - Dashboard - Real-time monitoring
   - Parameters - Drive parameter configuration
   - Diagnostics - System status and fault information
   - Data Logging - Data recording and export

## Connecting to a Drive

1. Select the correct COM port from the dropdown
2. Choose the appropriate baud rate (typically 19200 for Nidec drives)
3. Select the drive model (e.g., CDE400)
4. Click "Connect"

## Monitoring Drive Status

The dashboard provides real-time information about the drive's status:
- Output frequency (Hz)
- Output current (A)
- DC bus voltage (V)
- Drive status (Ready, Running, Fault, etc.)
- Active faults (if any)

## Controlling the Drive

### Basic Controls

- **Start/Stop** - Toggle drive operation
- **Speed Control** - Set the desired output frequency
- **Direction** - Set motor rotation direction (Forward/Reverse)
- **Jog** - Momentary operation at preset speed

### Parameter Configuration

1. Navigate to the "Parameters" tab
2. Select a parameter group from the left panel
3. Enter new values in the parameter fields
4. Click "Write" to save changes to the drive
5. Use "Read" to refresh parameter values from the drive

## Data Logging

1. Go to the "Data Logging" tab
2. Click "Browse" to select a log file location
3. Set the logging interval (in milliseconds)
4. Click "Start Logging" to begin recording data
5. Use "Export Data" to save collected data to a new file

## Saving and Loading Configurations

### Save Configuration

1. Click "File" > "Save Configuration"
2. Choose a location and filename
3. Click "Save"

### Load Configuration

1. Click "File" > "Load Configuration"
2. Select a previously saved configuration file
3. Click "Open"

## Troubleshooting

### Common Issues

1. **Connection Issues**
   - Verify the correct COM port is selected
   - Check cable connections
   - Ensure no other application is using the COM port

2. **Parameter Write Failures**
   - Verify the drive is in the correct mode for parameter changes
   - Check for write protection settings
   - Ensure the parameter is writable in the current drive state

3. **Application Crashes**
   - Check the application log file for errors
   - Verify all dependencies are installed correctly
   - Try restarting the application

### Getting Help

For additional support:
- Check the [Troubleshooting Guide](troubleshooting.md)
- Open an issue on [GitHub](https://github.com/Nsfr750/Nidec_CommanderCDE/issues)
