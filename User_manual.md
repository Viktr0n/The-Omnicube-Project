Full User Manual
This manual will guide you through the basic operations and features of the Omni-Cube game console.

You will need: 
* A Micro USB cable with 2.5 A
* A barrel plug power cord with 12 V and 6 A
* A USB-C cable

Startup
Make sure that the batteries for the handheld controllers are charged. If not, charge them with the USB-C cable.
Plug in the Raspberry Pi and the external power supply to a power outlet with the Micro-USB cable.
Wait for the Raspberry Pi to finish startup. The motor and the display should turn on automatically after the startup, which takes around a minute.

Maneuvering the main menu
Wake the controllers from deep sleep by pressing up on the d-pad.
The controllers should automatically connect to the Raspberry Pi.
Move the selection up in the main menu by pressing up on the d-pad, and down by pressing down.
Press the A button when selecting one of the buttons in the main menu. There are currently only two working buttons, the “Power Off” button turns of the display, and the “Pong” button which starts the game Pong.

Pong
When starting the game, you will enter a pause menu where the code will be waiting for the controllers to connect. The code displays which controllers are connected. If the black controller is connected, “plr 1” will be written in the top left corner of the pause menu, and if the white controller is connected “plr 2” will be written in the top right corner.
When both controllers are connected, both players need to press the A button at the same time to start the game.
In the game, you move your character to the left by pressing left on the d-pad and right by pressing right. The black controller controls the character on top, and the white controller controls the player on the bottom.
If a controller disconnects from the Raspberry Pi, the game will open the pause menu and can be started again the same way as in step 2.
To stop the pong game and to return to the main menu, both controllers need to be connected and then press the B button. This can be done both during the pause menu and during the game.

Controllers
You can force a controller to enter deep sleep by pressing and holding the A and B button for 2.5 seconds. This is a way to restart the controller if it doesn’t connect to the Raspberry Pi.
The controller enters deep sleep if no buttons are pressed for 2 minutes.
The controllers awake from deep sleep when the up button on the d-pad is pressed.

Adding more games
Here is a step by step tutorial on how to add a new game to the Omni-Cube.
Plug in a monitor, a keyboard and a mouse to the Raspberry Pi or access it remotely with for example Windows App Remote Desktop.
Create a new .py file in the same folder as the previous programmes. In this project Geany was used for this, but other text editors work as well.

Copy the configuration for CS and RST pins, the config for display baudrate, the setup for SPI bus using hardware SPI and the setup for the RA8875 display from the Pong code to the new game code so that you can update the display. Note that part of the setup for the RA8875 rotates the text for the display to fit portrait mode, but the x and y coordinates are not rotated. This means that a higher x coordinate translates to further from the top of the display and a higher y coordinate translates to further from the left edge.
Copy the notification_handler_plr1, notification_handler_plr2 and the handle_player functions as well as the Configuration from XIAO Client Code and the part of the run function that create tasks to connect to the controllers from the Pong code into the new game code. This is so that the new code can connect to and receive inputs from the controllers.
Program the rest of the game. Look at the main menu, the splashscreen and the Pong code for tips about how the syntax works for drawing on the display and how to check player inputs.
Update the while True loop in the run function of the main menu code so that it can start the new game. Use the if statement for the Pong code on row 168 as a template for how to add your own. select == 0 means that the Pong button is selected and select == 3 is the Power Off button, so there are currently two unused buttons.
Update on row 74 the text  on the button from “Game 2” to the name of your game.
Save the codes.
The new game should now be able to be started from the main menu.

If you want to add more than two new games to the Omni-Cube there are two things that need to be updated. Firstly, a new text needs to be added in the update_display function on row 78. Secondly, the modulus on the select variable on row 66 needs to be increased to the amount of buttons you require.
