<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BLE Device Connection and OTA Update</title>
</head>
<body>
    <h1>BLE Device Connection and OTA Update</h1>
    <p>This project provides a GUI-based Python application for Bluetooth Low Energy (BLE) device connection and Over-the-Air (OTA) firmware updates. It uses the Bleak library for Bluetooth communication and CustomTkinter for the graphical user interface.</p>
    <h2>Features</h2>
    <ul>
        <li>Scan for available BLE devices and filter by name.</li>
        <li>Connect to a BLE device and list its services and characteristics.</li>
        <li>Perform OTA firmware updates to a connected device.</li>
        <li>Read and write data to/from BLE devices.</li>
        <li>Start and stop notifications from BLE devices.</li>
        <li>Disconnect from a BLE device.</li>
    </ul>
    <h2>Prerequisites</h2>
    <p>To run this application, you need:</p>
    <ul>
        <li>Python 3.6 or later.</li>
        <li>The following Python libraries: bleak, customtkinter, CTkListbox.</li>
    </ul>
    <h2>Main GUI Components</h2>
    <ul>
        <li><strong>Scan Button:</strong> Scans for available BLE devices and lists them in a listbox.</li>
        <li><strong>Connect Button:</strong> Connects to a selected BLE device and displays its services.</li>
        <li><strong>Read/Write Buttons:</strong> Allows reading from and writing to the connected device.</li>
        <li><strong>Notify Button:</strong> Starts receiving notifications from the selected characteristic.</li>
        <li><strong>Disconnect Button:</strong> Disconnects from the BLE device.</li>
    </ul>
    <h2>Usage Instructions</h2>
    <h3>Scan and Connect</h3>
    <p>After scanning, to connect to a device, select the device from the listbox to connect to it.</p>
    <h3>Read, Write, and Notify</h3>
    <p>To read, write, and notify, select the UUID to perform the respective operations.</p>
    <h2>OTA Update Process</h2>
    <p>To perform an OTA firmware update, follow these steps:</p>
    <ol>
        <li>Connect to the BLE device.</li>
        <li>Click the "duf" button to select the firmware binary file (.bin).</li>
        <li>The OTA update will start automatically, displaying the progress in a progress bar.</li>
    </ol>
    <h2>Troubleshooting</h2>
    <p>If you encounter any issues, check the following:</p>
    <ul>
        <li>Ensure the BLE device is powered on and within range.</li>
        <li>Verify that the correct device is selected.</li>
        <li>If the OTA update fails, try again or ensure the firmware file is valid.</li>
    </ul>
</body>
</html>
