import time
import board
import busio
import digitalio
import random
import math

import asyncio
from bleak import BleakClient, BleakScanner

from adafruit_ra8875 import ra8875
from adafruit_ra8875.ra8875 import color565

# --- Configuration from XIAO Server Code ---
PLR1_NAME = "OmnicubePlayer1"
PLR1_SERVICE_UUID = "3f1e2b44-f0fa-420a-8630-dfb2e2ebda8e"
PLR1_CHARACTERISTIC_UUID = "2315f48e-a7e5-42d1-b3fa-36fad4994d81"
player1_input = [0, 0, 0, 0, 0, 0] # 0=up, 1=right, 2=down, 3=left, 4=b, 5=a

PLR2_NAME = "OmnicubePlayer2"
PLR2_SERVICE_UUID = "26478d74-e7d2-48f9-8b20-c10f0fdd20d6"
PLR2_CHARACTERISTIC_UUID = "2c8a15df-2c93-4a4b-bb1e-392a74e44864"
player2_input = [0, 0, 0, 0, 0, 0] # 0=up, 1=right, 2=down, 3=left, 4=b, 5=a

client1 = None
client2 = None

BLACK = color565(0, 0, 0)
WHITE = color565(255, 255, 255)

newInput = True

isWaiting = True
isPlaying = False

plr1Pos = 200 #min 0, max 380
plr2Pos = 200

ballX = 400 # distance from top in portrait
ballY = 240 # distance from left wall in portrait

ballSpeed = 20
ballDirection = 270

minBounceAngle = 30 # the minimum angle the ball can bounce of a player

pointPlr1 = 0
pointPlr2 = 0

# Configuration for CS and RST pins:
cs_pin = digitalio.DigitalInOut(board.D13)
rst_pin = digitalio.DigitalInOut(board.D5)

# Config for display baudrate (default max is 6mhz):
BAUDRATE = 6000000

# Setup SPI bus using hardware SPI:
spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# Create and setup the RA8875 display:
display = ra8875.RA8875(spi, cs=cs_pin, rst=rst_pin, baudrate=BAUDRATE, width=800, height=480)
display.init()
display._write_reg(0x22, 0x10)
display._write_reg(0x20, 0x08)
display.txt_size(2)
display.fill(BLACK)

def map(a, min1, max1, min2, max2): # maps a in range min1 - max1 to b in range min2 - max2
	b = (a-min1)*(max2-min2)/(max1-min1)+min2
	return b

def score(player):
	global pointPlr1, pointPlr2, plr1Pos, plr2Pos, ballX, ballY, ballSpeed, ballDirection
	if(player == 1): # handles points
		pointPlr1 += 1
	else:
		pointPlr2 += 1
	# displays points
	display.fill(BLACK)
	display.txt_size(3)
	display.txt_trans(WHITE)
	display.txt_set_cursor(int(display.width/4), int(display.width/5))
	display.txt_write(str(pointPlr1))
	display.txt_write(" - ")
	display.txt_write(str(pointPlr2))
	time.sleep(1.5)
	# Resets positions
	plr1Pos = 200
	plr2Pos = 200
	ballX = 400
	ballY = 240
	if(random.randint(0,1)):
		ballDirection = random.randint(minBounceAngle,180-minBounceAngle)
	else:
		ballDirection = random.randint(180+minBounceAngle,360-minBounceAngle)
	display.fill(BLACK)
	
def pause():
	display.txt_size(3)
	display.txt_trans(WHITE)
	display.txt_set_cursor(int(display.width/4), int(display.width/5))
	display.txt_write("Pause")
	display.txt_size(1)
	display.txt_set_cursor(int(display.width/3+50), int(50))
	display.txt_write("Both players press A")
	display.txt_set_cursor(int(display.width/3+75), int(50))
	display.txt_write("to start")
	display.txt_set_cursor(int(display.width/2+20), int(50))
	display.txt_write("Both players press B")
	display.txt_set_cursor(int(display.width/2+45), int(50))
	display.txt_write("to quit game")
	
	if client1 and client1.is_connected: # connection status plr 1
		display.txt_set_cursor(int(display.width/8), int(display.height/8))
		display.txt_write("plr 1")
	else:
		display.txt_set_cursor(int(display.width/8), int(display.width/8))
		display.txt_trans(BLACK)
		display.txt_write("plr 1")
		display.txt_trans(WHITE)

	if client2 and client2.is_connected: # connection status plr 2
		display.txt_set_cursor(int(display.width/8), int(display.height/8*6))
		display.txt_write("plr 2")
	else:
		display.txt_set_cursor(int(display.width/8), int(display.width/8*5))
		display.txt_trans(BLACK)
		display.txt_write("plr 2")
		display.txt_trans(WHITE)

def update_display():
	global player1_input, player2_input, plr1Pos, plr2Pos, ballX, ballY, ballSpeed, ballDirection
	if(player1_input[1] == 1 and player1_input[3] == 0):
		plr1Pos += 15
	if(player1_input[3] == 1 and player1_input[1] == 0):
		plr1Pos -= 15
	if(player2_input[1] == 1 and player2_input[3] == 0):
		plr2Pos += 15
	if(player2_input[3] == 1 and player2_input[1] == 0):
		plr2Pos -= 15
	
	plr1Pos = min(380, max(0, plr1Pos)) # Constrain position to 0 < x < 380
	plr2Pos = min(380, max(0, plr2Pos))
	
	# Draws player 1 (top player)
	display.fill_rect(20, 0, 20, plr1Pos, BLACK)
	display.fill_rect(20, plr1Pos+100, 20, display.height-plr1Pos-100, BLACK)
	display.fill_rect(20, plr1Pos, 20, 100, WHITE)
	
	# Draws player 2 (bottom player)
	display.fill_rect(display.width - 60, 0, 20, plr2Pos, BLACK)
	display.fill_rect(display.width - 60, plr2Pos + 100, 20, display.height-plr2Pos-100, BLACK)
	display.fill_rect(display.width - 60, plr2Pos, 20, 100, WHITE)
    
	prevBallX = ballX
	prevBallY = ballY
	
	# ball x plr 1 collision detection
	if ballX < 50 and ballY+10 > plr1Pos-10 and ballY+10 < plr1Pos+110:
		ballDirection = map(ballY-plr1Pos, 99, -19, 360-minBounceAngle, 180+minBounceAngle)
	
	# ball x plr 2 collision detection
	if ballX > display.width-90 and ballY+10 > plr2Pos-10 and ballY+10 < plr2Pos+110:
		ballDirection = map(ballY-plr2Pos, 99, -19, minBounceAngle, 180-minBounceAngle)

	# ball x wall collision detection
	if ballY < 10 or ballY > display.height-25: # left wall
		ballDirection = 180-ballDirection
	ballDirection = ballDirection % 360
	ballX -= int(math.sin(math.radians(ballDirection))*ballSpeed) # x = hight in portrait
	ballY += int(math.cos(math.radians(ballDirection))*ballSpeed) # y = width in portrait
	display.fill_rect(prevBallX, prevBallY, 20, 20, BLACK)
	display.fill_rect(ballX, ballY, 20, 20, WHITE)

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
    global newInput, isWaiting, isPlaying

    # 1. Start Player 1
    p1_task = asyncio.create_task(
        handle_player(PLR1_NAME, PLR1_CHARACTERISTIC_UUID, notification_handler_plr1)
    )

    # 2. WAIT before starting Player 2
    print("Waiting for Player 1 to initialize...")
    await asyncio.sleep(2.0)

    # 3. Start Player 2
    p2_task = asyncio.create_task(
        handle_player(PLR2_NAME, PLR2_CHARACTERISTIC_UUID, notification_handler_plr2)
    )

    print("Both Bluetooth managers initialized. Entering display loop...")

    while isWaiting or isPlaying:
        display.fill(BLACK)
        while isWaiting:
            pause()
            if(player1_input[4] and player2_input[4]):
                isWaiting = False
                isPlaying = False
            if player1_input[5] == 1 and player2_input[5] == 1: # Example start condition
                isWaiting = False
                isPlaying = True
            await asyncio.sleep(0.01)

        display.fill(BLACK)

        while isPlaying:
            if(player1_input[4] and player2_input[4]):
                isPlaying = False
            if ballX < 49 - ballSpeed and ballDirection < 180:
                score(2)
            if ballX > display.width-89 + ballSpeed and ballDirection > 180:
        	    score(1)
            update_display()
            if not (client1 and client1.is_connected) or not (client2 and client2.is_connected): # If a controller disconnects, pause the game
                isWaiting = True
                isPlaying = False
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
