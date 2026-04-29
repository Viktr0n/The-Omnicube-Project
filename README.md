# Omni-Cube

## Project Overview

The Omni-Cube is a gaming console with an omnidirectional Andotrope display. It is a final thesis project for upper secondary school that addresses the challenge of restricted viewing angles in traditional multiplayer gaming by providing a 360-degree display experience.

This repository contains the codes used in this project. For the 3D models, please go to this repo:
https://github.com/Kingfisk/Omni-Cube_3DModels 

## Hardware Components

- **Main Console**: Raspberry Pi 3 Model B running CircuitPython
- **Display**: RA8875 omnidirectional display with 360-degree image capability
- **Controllers**: Two handheld wireless controllers built with ESP32/ESP32-S3 using Bluetooth Low Energy (BLE)
- **Motor Control**: H-bridge controlled DC motor for display rotation
- **Chassis**: Custom 3D-printed PLA housing designed in Fusion 360

## Software Structure

- **OC_splashscreen.py** - Splash screen with project title and creator credits
- **OC_main_menu.py** - Main menu system with game selection and power control
- **OC_pong.py** - Pong game implementation with BLE controller support
- **OC_motorCode.py** - Motor control via PWM and GPIO
- **OC_controller_plr1.ino & OC_controller_plr2.ino** - Wireless controller firmware with BLE communication

## Features

- **Dual Wireless Controllers** - D-pad and A/B button inputs for two players
- **BLE Connectivity** - Seamless Bluetooth Low Energy communication between controllers and console
- **Power Management** - Automatic deep sleep modes after 2 minutes of inactivity
- **Expandable Game Architecture** - Easy-to-extend system for adding new games beyond Pong
- **Omnidirectional Display** - 360-degree viewing experience for multiplayer gaming

## Getting Started

### Startup Instructions
1. Ensure controller batteries are charged
2. Plug in the Raspberry Pi with Micro-USB cable (2.5A)
3. Connect external power supply (12V, 6A barrel plug)
4. Wait approximately 1 minute for startup - motor and display will initialize automatically

### Controller Pairing
- Wake controllers by pressing up on the D-pad
- Controllers automatically connect to the Raspberry Pi

### Main Menu Navigation
- Press up/down on D-pad to navigate menu options
- Press A button to select an option
- Current working options: Pong game and Power Off

### Pong Game Controls
- **Black Controller** (Player 1): Controls top paddle
- **White Controller** (Player 2): Controls bottom paddle
- Press left/right on D-pad to move your paddle
- Press A button (both players simultaneously) to start the game
- Press B button (both players) to return to main menu
- Game pauses automatically if a controller disconnects

### Controller Management
- Press and hold A + B buttons for 2.5 seconds to force deep sleep/restart
- Controllers enter deep sleep after 2 minutes of inactivity
- Press D-pad up to wake controllers from deep sleep

## Adding More Games

The Omni-Cube supports extensible game development. See the User_manual file for detailed step-by-step instructions on how to add new games to the system.

## Authors

- Oscar Bodenäs
- Victor Ekberg

## Technologies

- CircuitPython
- C++ (Arduino)
- Bluetooth Low Energy (BLE)
- RA8875 Display Controller
- Raspberry Pi GPIO Control
