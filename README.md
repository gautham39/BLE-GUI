#BLE Device Connection and OTA Update
This project provides a GUI-based Python application for Bluetooth Low Energy (BLE) device connection and Over-the-Air (OTA) firmware updates. It uses the Bleak library for Bluetooth communication and CustomTkinter for the graphical user interface.

Features
Scan for available BLE devices and filter by name.
Connect to a BLE device and list its services and characteristics.
Perform OTA firmware updates to a connected device.
Read and write data to/from BLE devices.
Start and stop notifications from BLE devices.
Disconnect from a BLE device.
Prerequisites
To run this application, you need:

Python 3.6 or later.
The following Python libraries: bleak, customtkinter, CTkListbox.



Main GUI Components
Scan Button: Scans for available BLE devices and lists them in a listbox.
Connect Button: Connects to a selected BLE device and displays its services.
Read/Write Buttons: Allows reading from and writing to the connected device.
Notify Button: Starts receiving notifications from the selected characteristic.
Disconnect Button: Disconnects from the BLE device.

SCAN NAD CONNECT:

After scanning to connect to device ,select the device from thr listbox to connect to device .

READ,WRITE AND NOTIFY:

To read,write and notify select the UUID TO do the respective operations



OTA Update Process
To perform an OTA firmware update, follow these steps:

Connect to the BLE device.
Click the "duf" button to select the firmware binary file (.bin).
The OTA update will start automatically, displaying the progress in a progress bar.



OTA Update Process
To perform an OTA firmware update, follow these steps:

Connect to the BLE device.
Click the "duf" button to select the firmware binary file (.bin).
The OTA update will start automatically, displaying the progress in a progress bar.
Troubleshooting
If you encounter any issues, check the following:

Ensure the BLE device is powered on and within range.
Verify that the correct device is selected.
If the OTA update fails, try again or ensure the firmware file is valid.
