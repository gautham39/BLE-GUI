import asyncio
import binascii
import threading
from bleak import BleakScanner, BleakClient
from customtkinter import *
from CTkListbox import *
import re
from tkinter import *
import datetime
import time

i = 0
filter_data = None
connected = False
address = ''
char_read = []
char_write = []
char_notify = []

OTA_DATA_UUID = '23408888-1F40-4CD8-9B89-CA8D45F8A5B0'
OTA_CONTROL_UUID = '7AD671AA-21C0-46A4-B722-270E3AE3D830'

"""
char_write_uuid = "33333333-2222-2222-1111-111100000101"
notify_uuid1___ = "33333333-2222-2222-1111-111100000000"
char_read_uuid_ = "33333333-2222-2222-1111-111100000001
"""""

SVR_CHR_OTA_CONTROL_NOP = bytearray.fromhex("00")
SVR_CHR_OTA_CONTROL_REQUEST = bytearray.fromhex("01")
SVR_CHR_OTA_CONTROL_REQUEST_ACK = bytearray.fromhex("02")
SVR_CHR_OTA_CONTROL_REQUEST_NAK = bytearray.fromhex("03")
SVR_CHR_OTA_CONTROL_DONE = bytearray.fromhex("04")
SVR_CHR_OTA_CONTROL_DONE_ACK = bytearray.fromhex("05")
SVR_CHR_OTA_CONTROL_DONE_NAK = bytearray.fromhex("06")
SVR_CHR_OTA_MTU_REQUEST =bytearray.fromhex("07")
async def send_ota(file_path):
    global complete
    t0 = datetime.datetime.now()
    queue = asyncio.Queue()
    firmware = []
    ota_window = CTkToplevel(root)
    ota_window.title("ota update")
    ota_window.geometry("400x200")
    w3 = CTkLabel(master=ota_window, text='0%')
    w3.pack()
    ota_progress=CTkProgressBar(ota_window,orientation="horizontal")
    ota_progress.pack(pady=10)
    w2 = CTkLabel(master=ota_window, text='0%')
    w2.pack()
    ota_progress.set(0)

    async def ota_notification_handler(sender: int, data: bytearray):
        if data == SVR_CHR_OTA_CONTROL_REQUEST_ACK:
            print("ESP32: OTA request acknowledged.")
            await queue.put("ack")
        elif data == SVR_CHR_OTA_CONTROL_REQUEST_NAK:
            print("ESP32: OTA request NOT acknowledged.")
            await queue.put("nak")
            await client1.stop_notify(OTA_CONTROL_UUID)
        elif data == SVR_CHR_OTA_CONTROL_DONE_ACK:
            print("ESP32: OTA done acknowledged.")
            await queue.put("ack")
            await client1.stop_notify(OTA_CONTROL_UUID)
        elif data == SVR_CHR_OTA_CONTROL_DONE_NAK:
            print("ESP32: OTA done NOT acknowledged.")
            await queue.put("nak")
            await client1.stop_notify(OTA_CONTROL_UUID)
        else:
            print(f"Notification received: sender: {sender}, data: {data}")

    # subscribe to OTA control
    await client1.start_notify(
        OTA_CONTROL_UUID, ota_notification_handler)

    # compute the packet size
    packet_size =client1.mtu_size
    print(f"{client1.mtu_size}")
    if packet_size < 512:
        await client1.write_gatt_char(
            OTA_CONTROL_UUID,
            SVR_CHR_OTA_MTU_REQUEST
        )
        await client1.disconnect()

        print("MTU negotiation successful.")
        await client1.connect()
        asyncio.sleep(1)
        print(client1.connect())
        await client1.start_notify(
            OTA_CONTROL_UUID, ota_notification_handler)

    else:
        print("MTU characteristic not found. MTU negotiation failed.")

# write the packet size to OTA Data
    packet_size2 = (client1.mtu_size - 3)

    print(f"Sending packet size: {packet_size2}.")
    await client1.write_gatt_char(
        OTA_DATA_UUID,
        packet_size2.to_bytes(2, 'little'),
        response=True
    )

    # split the firmware into packets
    with open(file_path, "rb") as file:
        while chunk := file.read(packet_size2):
            firmware.append(chunk)

    # write the request OP code to OTA Control
    print("Sending OTA request.")
    print(f" BEFORE OTA_CONTROL REQUEST{queue}")

    await client1.write_gatt_char(
        OTA_CONTROL_UUID,
        SVR_CHR_OTA_CONTROL_REQUEST
    )

    # wait for the response
    await asyncio.sleep(1)
    print(f" AFTER OTA_CONTROL REQUEST{queue}")
    if await queue.get() == "ack":

        # sequentially write all packets to OTA data
        for i, pkg in enumerate(firmware):
            try:
                print(f"Sending packet {i + 1}/{len(firmware)}.")
                #Listbox2.insert("1", f" Sending packet {i + 1}/{len(firmware)}. ")

                data_size_bytes = len(firmware)
                print(f"before progress calc  .")

                progress = (i / len(firmware)) * 1  # Calculate progress percentage

                start_time = time.time()
                print(f"after  progress calc  .")
                print(f"before  write ota .")

                await client1.write_gatt_char(OTA_DATA_UUID, pkg, response=True)
                print(f"after write ota .")

                end_time = time.time()
                time_taken = end_time - start_time
                transfer_speed_bytes_per_second = (data_size_bytes / time_taken)/1024
                speed = round(transfer_speed_bytes_per_second, 3)
                ota_progress.set(progress)   # Update progress bar
                print(f"after progress bar update  .")

                #root.update_idletasks()
                per1 = ota_progress.get()*100
                per2 = round(per1, 2)
                w2.configure(text=f" transfer speed = {speed} KB/second")
                print(f"after speed update   .")

                w3.configure(text=f" transferred = {per2} %")
                print(f"after percentage update  .")

                if i == len(firmware):
                    ota_window.destroy()
                    Listbox2.insert("0", f" transfer complete ,now the device will be disconnected and updated ")
                    print(client1.is_connected)
                    if not client1.is_connected:
                        Listbox1.delete("0", "END")
            except Exception as e:
                Listbox2.insert("0", f"OTA update interrupted at packet {i + 1}")
                Listbox2.insert("1", f"TRY AGAIN")

                print(f"OTA update interrupted at packet {i + 1}: {e}")
                break  # Break from the loop on interruption or error



        # write done OP code to OTA Control
        await  asyncio.sleep(1)
        print("Sending OTA done.")
        await client1.write_gatt_char(
            OTA_CONTROL_UUID,
            SVR_CHR_OTA_CONTROL_DONE
        )

        # wait for the response
        await asyncio.sleep(1)
        if await queue.get() == "ack":
            dt = datetime.datetime.now() - t0
            print(f"OTA successful! Total time: {dt}")
        else:
            print("OTA failed.")

    else:
        print("ESP32 did not acknowledge the OTA request.")


def duf():
    if not connected:
        Listbox2.insert("0", f"first connect to server")
        print("first connect to server")
    else:
        print("duf started ")
        file_path = filedialog.askopenfilename()

        if file_path:
            print("Selected file:", file_path)
            base_name, extension = os.path.splitext(file_path)
            if extension.lower() == ".bin":
                send_future = asyncio.run_coroutine_threadsafe(send_ota(file_path), loop)
            else:
                print("select a .bin file for ota")
                return
###########################################################################################################################
async def stop_notification():
    try:

        await client1.stop_notify(notify_uuid)
        Listbox2.insert("0", f" notification stopped \n \n ")


    except Exception as e:
        print("Error during stop operation:", e)


def stop_notify():
    print("stopped_notification")
    notify_future = asyncio.run_coroutine_threadsafe(stop_notification(), loop)
################################################################################################


"""start notification from server """


async def notification_callback(sender, data):
    # Process received notification data
    print(f"Received notification data:sender ={sender}, data={data}")
    Listbox2.insert("0", f" notify data is  {data} \n \n ")
    await asyncio.sleep(1)


async def start_notification(notify_uuid):
    try:

        value1 = await client1.start_notify(notify_uuid, notification_callback)
        print(f" Value: {value1}")


    except Exception as e:
        print("Error during read operation:", e)



def notify():
    if not connected:
        Listbox2.insert("0", f"first connect to server")
        print("first connect to server")
        return
    else:
        global notify_future
        uuid = selected_data.strip()

# check if it is a notify uuid

        for i in range(len(char_notify)):
            if uuid == char_notify[i]:
                global notify_uuid
                notify_uuid = uuid

                notify_future = asyncio.run_coroutine_threadsafe(start_notification(notify_uuid), loop)
            else:
                print("select uuid to start notify   \n ")
                Listbox2.insert("0", f"select notify uuid ")

##############################################################################################################


"""write  and  display  data """


async def write_display(write_uuid,write_data):

# get user input and convert to hex

    if write_data is not None:
        print("You entered:", write_data)
        my_hex_rep = binascii.hexlify(write_data.encode())

    # decode to ascii
        print(my_hex_rep)
        await client1.write_gatt_char(write_uuid, my_hex_rep, response=False)
        Listbox2.insert("END", f" written data is : {write_data} \n \n ")
    else:
        print("You canceled.")

def write():
    if not connected:
        Listbox1.insert("END", f"first connect to server")
        print("first connect to server")
        return
    else:
        # check if it is a wrte uuid
        for i in range(len(char_write)):
            print(f"{char_write[i]},i={i}")
            uuid = selected_data.strip()
            print(f"{uuid}")
            if uuid == char_write[i]:
                write_uuid = uuid
                print(f"{write_uuid}")
                user_input= CTkInputDialog(text="Type in a number:", title="Test")
                write_data=user_input.get_input()

                write_future = asyncio.run_coroutine_threadsafe(write_display(write_uuid,write_data), loop)
            else:
                print("select uuid to write to \n ")
                Listbox2.insert("0", f"select write uuid ")


#####################################################################################################################


"""read and  display data """


def read():
    if not connected:
        Listbox1.insert("END", f"first connect to server")
        print("first connect to server")
        return
    else:
        for i in range(len(char_read)):
            print(f"s={selected_data}")
            print(f"cr={char_read[i]}")
            uuid = selected_data.strip()
            if uuid == char_read[i]:
                read_uuid = uuid
                asyncio.run_coroutine_threadsafe(read_and_display(read_uuid), loop)

        else:
            print(f"select read uuid")
            Listbox2.insert("0", f"select read uuid ")


async def read_and_display(read_uuid):
    try:
        value = await client1.read_gatt_char(read_uuid)
        print(f" Value: {value}")

        Listbox2.insert("1", f" Value: {value} \n \n ")

    except Exception as e:
        print("Error during read operation ", e)
        Listbox1.insert("END", f"Error during read operation {e}")


def go(event):

    global selected_data
    cs = Listbox1.curselection()
    selected_data = Listbox1.get(cs)
    # Updating label text to selected option
    w.configure(text=f"selected data is ={selected_data}")

    # Setting Background Colour

##################################################################################


"""disconnect from ble server """


async def async_disconnect():
    Listbox1.delete("0", "END")
    Listbox2.delete("0", "END")
    await client1.disconnect()
    print(client1.is_connected)
    selected_data = None
    Listbox1.insert("END", f"disconnected from  {client1} \n \n ")


def disconnect():
    if connected:
        asyncio.run_coroutine_threadsafe(async_disconnect(), loop)
    else:
        print(client1.is_connected)
        print("not connected to anything")


######################################################################################################################
"""connect to ble server  and show services """


async def connect(address):
    try:
            global client1
            client1 = BleakClient(address)
            await client1.connect()
            print(client1.connect)
            global connected
            connected = client1.is_connected

# Perform operations after successful connection

            Listbox1.delete(0, END)
            Listbox1.insert("END", f"connected to {client1} \n ")
            device_address = client1.address
            Listbox1.insert("END", f"    AVAILABLE SERVICES ARE   : ")

            for service in client1.services:
                Listbox1.insert("END", f"- Description of service: {service.description}")
                Listbox1.insert("END", f" UUID: {service.uuid} ")
                Listbox1.insert("END", f" Handle: {service.handle}  \n  ")

            for char in service.characteristics:
                    k=0
                    Listbox1.insert("END", f" \n  - Description of char : {char.description}")
                    Listbox1.insert("END", f" Properties: {','.join(char.properties)}")
                    if char.properties == ['read']:
                        char_read.append(char.uuid)
                        print("char_read_uuid=", char_read[k])
                    elif char.properties == ['write']:
                        char_write.append(char.uuid)

                        print("char write uuid =", char_write[k])
                    else:
                        char_notify.append(char.uuid)
                        print("char notify_uuid =", char_notify[k])
                    k = k+1
                    Listbox1.insert("END", f"{char.uuid} \n")

    except Exception as e:
        print("Error:", e)


async def async_connect(address):
    await connect(address)


def connect_to_device():

    selected = Listbox1.get(Listbox1.curselection())
    if selected:
        words = selected.split(',')
        selected_device = words[1].strip()
        global address
        address = str(selected_device)
        asyncio.run_coroutine_threadsafe(async_connect(address), loop)


#####################################################################################################################
"""SCAN AND PRINT AVAILABLE DEVICES  """


async def async_scan(filter_data):
    Listbox1.delete(0, END)
    Listbox1.insert("1", f"scan started \n")

    Listbox1.insert("2", f"available devices are \n")
    devices = await BleakScanner.discover()
    count = 1

    for d in devices:
            count = count+1
            print(f"{filter_data}")
            print(f"{count}")
            print(f"{d.name}")
            if filter_data:
                try:
                    match = re.search(filter_data, d.name, flags=re.I)
                except Exception as e:
                    print("Error occurred during regex search:", e)
                    continue

                if match:
                    print(f"Match found for device {d.name} at index {match.start()}")
                    Listbox1.insert("END", f"{d.name},{d.address}\n ")

                # Perform further actions if a match is found
                else:
                    print("No match found for this device.")
            else :
                Listbox1.insert("END", f"{d.name},{d.address}\n ")


def start_scan():

    asyncio.run_coroutine_threadsafe(async_scan(filter_data), loop)

#######################################################################################################################


"""DEFINING EVENT LOOP function"""


def start_event_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

####################################################################################


"""filter devices to show """


def filter_device():
    filter1 = CTkInputDialog(text="enter filter data:", title="filter")
    global filter_data

    filter_data = filter1.get_input()

    print(f"filter={filter_data}")
    return filter_data
######################################################################################################################


"""MAIN   function WHICH HAS TKINTER GUI CODE  """


def main():
    global root
    root = CTk()
    root.configure(bg="black")
    root.title("BLE Device Connection")
    root.geometry("640x480")

    frame_buttons = CTkFrame(root)# frame which contains buttons
    frame_buttons.pack(side=LEFT, padx=20, pady=20)

    filter_button = CTkButton(frame_buttons, text="filter", command=filter_device)
    filter_button.pack(padx=10, pady=10)

    scan_button = CTkButton(frame_buttons, text="Scan", command=start_scan)
    scan_button.pack(padx=10, pady=10)

    connect_button = CTkButton(frame_buttons, text="Connect", command=connect_to_device)
    connect_button.pack(padx=10, pady=10)

    global Listbox1
    global Listbox2
    global w

    w = CTkLabel(master=root, text='Default')
    w.pack()

    Listbox1 = CTkListbox(root, width=500, height=600)# listbox to show chr uuid
    Listbox1.pack(side=LEFT,  expand=True, padx=2, pady=2)

    Listbox2 = CTkListbox(root, width=500, height=600)# listbox to show sent and receive data
    Listbox2.pack(side=RIGHT, padx=2, pady=2)

    Listbox1.bind('<<ListboxSelect>>', go)
    Listbox1.pack()

    read_button = CTkButton(frame_buttons, text="read", command=read)
    read_button.pack(padx=10, pady=10)

    write_button = CTkButton(frame_buttons, text="write", command=write)
    write_button.pack(padx=10, pady=10)

    global btn_text
    notify_button = CTkButton(frame_buttons, text="start notify", command =notify)
    notify_button.pack(padx=10, pady=10)

    stopnotify_button = CTkButton(frame_buttons, text= "stop_notify", command =stop_notify)
    stopnotify_button.pack(padx=10, pady=10)

    duf_button = CTkButton(frame_buttons, text="duf", command=duf)
    duf_button.pack(padx=10, pady=10)

    disconnect_button = CTkButton(frame_buttons, text="disconnect", command=disconnect)
    disconnect_button.pack(padx=10, pady=10)

    global loop
    loop = asyncio.new_event_loop()
    asyncio_thread = threading.Thread(target=start_event_loop, args=(loop,), daemon=True)
    asyncio_thread.start()

    root.mainloop()


if __name__ == "__main__":
    main()
