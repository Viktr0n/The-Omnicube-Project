import time
import board
import busio
import digitalio
import random
import subprocess

import asyncio
from bleak import BleakClient, BleakScanner

from adafruit_ra8875 import ra8875
from adafruit_ra8875.ra8875 import color565

import os
import sys

# Change the working directory to the script's location
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# --- Configuration from XIAO Server Code ---
PLR1_NAME = "OmnicubePlayer1"
PLR1_SERVICE_UUID = "3f1e2b44-f0fa-420a-8630-dfb2e2ebda8e"
PLR1_CHARACTERISTIC_UUID = "2315f48e-a7e5-42d1-b3fa-36fad4994d81"
player1_input = [0, 0, 0, 0, 0, 0] # 0=up, 1=right, 2=down, 3=left, 4=b/cancel, 5=a/confirm

PLR2_NAME = "OmnicubePlayer2"
PLR2_SERVICE_UUID = "26478d74-e7d2-48f9-8b20-c10f0fdd20d6"
PLR2_CHARACTERISTIC_UUID = "2c8a15df-2c93-4a4b-bb1e-392a74e44864"
player2_input = [0, 0, 0, 0, 0, 0] # 0=up, 1=right, 2=down, 3=left, 4=b/cancel, 5=a/confirm

client1 = None
client2 = None

BLACK = color565(0, 0, 0)
WHITE = color565(255, 255, 255)
BLUE = color565(32, 64, 255)
CYAN = color565(77, 255, 223)

select = 0
newInput = True

# Configuration for CS and RST pins:
cs_pin = digitalio.DigitalInOut(board.D13)
rst_pin = digitalio.DigitalInOut(board.D5)

# Config for display baudrate (default max is 6mhz):
BAUDRATE = 6000000

# Setup SPI bus using hardware SPI:
spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# Create and setup the RA8875 display:
display = ra8875.RA8875(spi, cs=cs_pin, rst=rst_pin, baudrate=BAUDRATE)
display.init()
display._write_reg(0x22, 0x10)
display._write_reg(0x20, 0x08)
display.txt_size(3)

def update_display():
    global select, newInput, player1_input, player2_input
    if(newInput):
        if(player1_input[0] == 1 or player2_input[0] == 1):
            select -= 1
        elif(player1_input[2] == 1 or player2_input[2] == 1):
            select += 1
        select %= 4
        try:    
            display.fill(BLUE)
            display.fill_rect(int(display.width/6*(select+1.5)+10), 0, 55, int(display.height), CYAN)
            display.txt_trans(WHITE)
            display.txt_set_cursor(int(display.width/6*1.5), int(display.height/5))
            display.txt_write("Pong")
            display.txt_set_cursor(int(display.width/6*2.5), int(display.height/5))
            display.txt_write("Game 2")
            display.txt_set_cursor(int(display.width/6*3.5), int(display.height/5))
            display.txt_write("Game 3")
            display.txt_set_cursor(int(display.width/6*4.5), int(display.height/5))
            display.txt_write("Power Off")
            newInput = False
        except Exception as e:
            print(f"Display update failed: {e}")


def notification_handler_plr1(sender, data):
    global player1_input, newInput
    #Handles data received from the characteristic notification.
    #The data is received as a bytearray, which is then decoded and parsed.
    try:
        data_int = int.from_bytes(data, "little") #decodes data to int
        player1_input = [0, 0, 0, 0, 0, 0] # 0=up, 1=right, 2=down, 3=left, 4=b, 5=a
        for i in range(5, -1, -1): #converts int to list
            if data_int >= 10**i:
                player1_input[i] = 1
                data_int -= 10**i
        newInput = True
        print(f"Received data from player 1: {player1_input}")
    except Exception as e:
        print(f"Error processing notification data: {e}")

def notification_handler_plr2(sender, data):
    global player2_input, newInput
    try:
        data_int = int.from_bytes(data, "little") #decodes data to int
        player2_input = [0, 0, 0, 0, 0, 0] # 0=up, 1=right, 2=down, 3=left, 4=b, 5=a
        for i in range(5, -1, -1): #converts int to list
            if data_int >= 10**i:
                player2_input[i] = 1
                data_int -= 10**i
        newInput = True
        print(f"Received data from player 2: {player2_input}")
    except Exception as e:
        print(f"Error processing notification data: {e}")


async def handle_player(name, char_uuid, handler):
    """Manages the connection for a specific XIAO device."""
    global client1, client2
    print(f"Starting manager for {name}...")
    while True:
        try:
            device = await BleakScanner.find_device_by_name(name, timeout=10.0)
            if not device:
                print(f"{name} not found, retrying...")
                await asyncio.sleep(5)
                continue

            async with BleakClient(device) as client:
                if(name == PLR1_NAME):
                    client1 = client
                elif(name == PLR2_NAME):
                    client2 = client
                print(f"Connected to {name} ({device.address})")
                await client.start_notify(char_uuid, handler)
                
                # Keep this task alive as long as the client is connected
                while client.is_connected:
                    await asyncio.sleep(1.0) 
                
                print(f"Connection lost to {name}. Reconnecting...")
        except Exception as e:
            print(f"Error in {name} manager: {e}")
            # Randomize sleep between 2 and 5 seconds to avoid collisions
            await asyncio.sleep(random.uniform(2.0, 5.0))

async def run():
    global newInput
    
    # 1. Start Player 1
    p1_task = asyncio.create_task(
        handle_player(PLR1_NAME, PLR1_CHARACTERISTIC_UUID, notification_handler_plr1)
    )
    
    # 2. WAIT before starting Player 2
    # This gives Player 1 time to finish scanning/connecting
    print("Waiting for Player 1 to initialize...")
    await asyncio.sleep(2.0) 

    # 3. Start Player 2
    p2_task = asyncio.create_task(
        handle_player(PLR2_NAME, PLR2_CHARACTERISTIC_UUID, notification_handler_plr2)
    )

    print("Both Bluetooth managers initialized. Entering display loop...")

    # Main UI Loop
    while True:
        if newInput:
            if(select == 0 and (player1_input[5] or player2_input[5])): # If you press on the pong option
                display.fill(BLACK)
                display.fill_rect(int(display.width/4+50), int(display.height/4), int(display.width/7), int(display.height/4*2), WHITE)
                display.fill_rect(int(display.width/4+60), int(display.height/4+10), int(display.width/7-20), int(display.height/4*2-20), BLACK)
                display.txt_trans(WHITE)
                display.txt_set_cursor(int(display.width/4+70), int(display.height/3+10))
                display.txt_write("PONG")
                try:
                    await client1.disconnect() # disconnects controllers so they can reconnect in the game
                except:
                    print("Player 1 couldn't disconnect")
                try:
                    await client2.disconnect()
                except:
                    print("Player 2 couldn't disconnect")
                subprocess.run(["python", "pong.py"]) # starts pong
                display.txt_size(3)
            update_display()
            newInput = False
            if(select == 3 and (player1_input[5] or player2_input[5])): # If you press on "Power Off"
                display.fill(BLACK)
                break
        await asyncio.sleep(0.01)

# --- Execution ---
if __name__ == "__main__":
    try:
        # This is required to run asynchronous functions
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\nClient stopped by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
