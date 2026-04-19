from PIL import Image
from adafruit_ra8875 import ra8875
from adafruit_ra8875.ra8875 import color565

import time
import board
import busio
import digitalio
import subprocess
import os
import sys

BLUE = color565(32, 64, 255)
WHITE = color565(255, 255, 255)

# Change the working directory to the script's location
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Configuration for CS and RST pins:
cs_pin = digitalio.DigitalInOut(board.D13)
rst_pin = digitalio.DigitalInOut(board.D5)

# Config for display baudrate (default max is 6MHz):
BAUDRATE = 6000000

# Setup SPI bus using hardware SPI:
spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# Create and setup the RA8875 display:
display = ra8875.RA8875(spi, cs=cs_pin, rst=rst_pin, baudrate=BAUDRATE)
display.init()
display._write_reg(0x22, 0x10)
display._write_reg(0x20, 0x08)
display.txt_size(3)

def draw_image(filename, x_start=0, y_start=0, pixel_size=1):
    try:
        img = Image.open(filename).convert("RGB")
        pixels = img.load()
        width, height = img.size
        
        # If pixels are the same color in a row, draw one long rectangle
        for y in range(height):
            x = 0
            while x < width:
                color = color565(*pixels[x, y])
                run_length = 1
                
                # Check how many pixels in this row are the same color
                while x + run_length < width and pixels[x + run_length, y] == pixels[x, y]:
                    run_length += 1
                
                # Draw the entire section of same-colored pixels as one rectangle
                display.fill_rect(
                    x_start + (x * pixel_size),
                    y_start + (y * pixel_size),
                    run_length * pixel_size,
                    pixel_size,
                    color
                )
                
                x += run_length # Increase x by amount of pixels drawn
                
    except Exception as e:
        print(f"Error: {e}")
            
display.fill(BLUE)

draw_image("/home/viktr0n/Pictures/splashscreen.bmp", 240, 130, 4)

display.txt_trans(WHITE)
display.txt_set_cursor(120, 90)
display.txt_write("OMNI-CUBE")

display.txt_size(2)
display.txt_set_cursor(520, 90)
display.txt_write("Oscar Bodenäs")
display.txt_set_cursor(560, 90)
display.txt_write("Victor Ekberg")

subprocess.run(["python", "mainMenue.py"]) # starts main menue
