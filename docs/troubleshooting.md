# Troubleshooting Guide

## Table of Contents

1. [Connection Issues](#connection-issues)
2. [Communication Problems](#communication-problems)
3. [Application Errors](#application-errors)
4. [Performance Issues](#performance-issues)
5. [Frequently Asked Questions](#frequently-asked-questions)
6. [Getting Help](#getting-help)

## Connection Issues

### Cannot Find COM Port

**Symptoms:**

- No COM ports listed in the dropdown
- "No available ports found" message

**Solutions:**

1. **Check Physical Connections**
   - Ensure the USB cable is properly connected
   - Try a different USB port
   - Test with a different USB cable

2. **Driver Installation**
   - Install the latest USB-to-Serial drivers for your adapter
   - For FTDI-based adapters, download from [FTDI Chip](https://ftdichip.com/drivers/vcp-drivers/)
   - For CH340/CH341 adapters, download appropriate drivers

3. **Windows Device Manager**
   - Open Device Manager (Win+X, then M)
   - Check under "Ports (COM & LPT)" for your device
   - Look for yellow warning triangles indicating driver issues
   - Right-click and select "Update driver" if needed

### Connection Drops

**Symptoms:**

- Intermittent disconnections
- "Connection lost" errors

**Solutions:**

1. Check cable connections
2. Try a different USB port (preferably USB 2.0)
3. Disable USB power saving:
   - Open Device Manager
   - Expand "Universal Serial Bus controllers"
   - Right-click each "USB Root Hub" → Properties
   - Go to "Power Management" tab
   - Uncheck "Allow the computer to turn off this device to save power"
   - Click OK and restart the computer

## Communication Problems

### No Response from Drive

**Symptoms:**

- "No response from drive" error
- Parameters not updating

**Solutions:**

1. **Verify Settings**
   - Check baud rate matches drive settings (typically 19200)
   - Verify COM port selection
   - Check for address conflicts if using multiple devices

2. **Drive Configuration**
   - Verify drive is powered on
   - Check for fault indicators on the drive
   - Ensure drive is in the correct mode (e.g., Modbus RTU)

3. **Wiring**
   - Verify RS-485/RS-232 wiring
   - Check for proper termination (120Ω resistor at each end for RS-485)
   - Verify polarity (A/B or +/- connections)

## Application Errors

### Application Crashes on Startup

**Symptoms:**

- Application fails to start
- Immediate crash with error message

**Solutions:**

1. **Check Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Clear Configuration**
   - Delete the configuration file (usually in `%APPDATA%\NidecCommander`)
   - Restart the application

3. **Check Logs**
   - Look for error logs in the application directory
   - Check Windows Event Viewer for application crashes

### UI Freezing

**Symptoms:**

- Interface becomes unresponsive
- "Not Responding" in window title

**Solutions:**

1. **Reduce Update Rate**
   - Decrease the polling interval in settings
   - Disable unused monitoring features

2. **Check for Updates**
   - Ensure you're using the latest version
   - Check for graphics driver updates

3. **Run with Debug Mode**

   ```bash
   python -X faulthandler main.py
   ```

## Performance Issues

### High CPU Usage

**Symptoms:**

- Application uses excessive CPU
- System becomes sluggish

**Solutions:**

1. **Optimize Settings**
   - Increase polling interval
   - Reduce number of monitored parameters
   - Disable unused UI elements

2. **Check for Background Processes**
   - Close unnecessary applications
   - Check for malware or other resource-intensive processes

### Memory Leaks

**Symptoms:**

- Application memory usage grows over time
- System becomes slow after prolonged use

**Solutions:**

1. **Restart Application**
   - Close and reopen the application periodically
   - Consider using the built-in memory management features

2. **Report Issue**
   - Note the steps to reproduce
   - Submit a bug report with memory usage logs

## Frequently Asked Questions

### Q: How do I update the application?

A:

1. Backup your configuration
2. Pull the latest changes from the repository
3. Update dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Restore your configuration if needed

### Q: Can I use this with non-Nidec drives?

A: The application is specifically designed for Nidec CDE series drives. While it uses standard protocols like Modbus RTU, compatibility with other drives is not guaranteed.

### Q: How do I enable debug logging?

A: Run the application with the `--debug` flag:

```bash
python main.py --debug
```

## Getting Help

### Support Channels

- **GitHub Issues**: [Create a new issue](https://github.com/Nsfr750/Nidec_CommanderCDE/issues)
- **Email**: [Nsfr750](mailto:nsfr750@yandex.com)

### When Requesting Help

Please provide the following information:

1. Application version
2. Operating system version
3. Drive model and firmware version
4. Steps to reproduce the issue
5. Any error messages or logs
6. Screenshots if applicable
