# shake-table
Code for the Raspberry Pi Shake Table project.

## How to use it

If you're a random person who wants to know how to use this thing, here are some instructions for you.

- Whenever you want to make the motor do stuff, you need to start the server.
  - How to start the server:
    1. Open up a Terminal window
	2. Navigate to the folder where you installed all this stuff
	   (if you don't know how to, go read some online introduction to bash or something)
	3. Run `sudo chmod ugo+rwx /dev/ttyS0`
	   - This will allow the server to access the motor controller.
	   - It may ask for administrator permissions.
	4. Run `python3 server.py`
	5. Good News: the server has started.
  - If you press Ctrl-C, close the terminal window, or restart your computer or something, the server will stop.
- Now that you've started the server, open a browser and go to `http://0.0.0.0:8080/`
  - This is a little website that lets you control the motors.
  - This website only works on your computer.
- The "Create File" button lets you create a file where the motor goes in a circle
  - You don't have to worry about this button.
  - This screen is completely broken.
  - Do not press the "Create File" button.
  - This button has been removed to discourage pressing.
- The "Run File" button lets you select a file to run. 3 files come preinstalled.
  - Once you have selected the file, there is a button to run the file.
  - If you push it, the motor will follow the instructions in the file.
  - Once it's done, be sure to go to the "Motor Control" screen to put the motor back in the center.
    - For more information about this, go read the "Motor Control" section below.
  - Warning: If you push the run button a whole bunch of times in a row (without correcting the position), you might have some problems.
  - Warning: Even if you don't do that, you might have problems anyways.
  - If the motor doesn't work, make sure:
    - The motor controller is connected.
    - The server is running.
    - You did Step 3 when setting up the server.
- The "Motor Control" button lets you move the motors around.
  - You can push the four buttons to move the motors.

## How it works

If you're a person who is good at programming, and you are here to fix the gigantic mess that is this entire thing, here's how it works.

(By the way, most of the programs have comments at the top explaining what they do and, to some extent, how they work.)

- `sendcmd.py` will send one command to the motors. I don't know why we can't send multiple commands with one process, but for some reason we have to end and restart the serial connection for each command. It's really annoying and results in somewhere near a 0.2s overhead per command.
- `server.py` is, as you have probably guessed, the server. It basically just serves all the xml files, but there's also some code to move the motor according to the files.
- The `client` folder contains the client files. Yes, the entire website is written in SVG. I told you this was a mess. Each of the files contains a comment at the top which contains a summary of the file.
- `terminal.py` lets you move the motors from a simple terminal interface. I'm not going to repeat how it works here, you can go look at the file yourself.
- The horribly named `datas` folder contains all of the data files you have generated. Each one is a 2D list of numbers encoded with JSON. (In other words, it's a double[3][].) In each sub-list, the first item is the time and the other two numbers are the X and Y positions at that time.

Anyways, good luck fixing this!
