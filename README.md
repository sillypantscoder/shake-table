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
     - This is a very important step.
	4. Run `python3 server.py`
	5. Good News: the server has started.
  - If you press Ctrl-C, close the terminal window, or restart your computer or something, the server will stop.
  - **Every time you start up the Raspberry Pi, you need to start the server!**
- Now that you've started the server, open a browser and go to `http://0.0.0.0:8080/`
  - This is a little website that lets you control the motors.
  - This website only works on your computer.
- The "Create File" button lets you create a file where the motor goes back and forth.
  - On this screen, there is a slider to select the frequency you want the motor to run at.
  - Once you create the file, you will be redirected to the "File Info" screen.
- The "Run File" button lets you select a file to run. 7 files come preinstalled.
  - Once you have selected the file, you will be shown the "File Info" screen.
  - This screen contains a description of the file you have selected.
  - There is also a button to run the file.
  - If you push it, the motor will follow the instructions in the file.
  - Once it's done, be sure to go to the "Motor Control" screen to put the motor back in the center.
    - For more information about this, go read the "Motor Control" section below.
  - Warning: If you push the run button a whole bunch of times in a row (without correcting the position), you might have some problems.
  - Warning: Even if you don't do that, you might have problems anyways. Hard to say.
  - If the motor doesn't work, make sure:
    - The motor controller is connected.
    - The server is running.
    - You did Step 3 when setting up the server. (Very important.)
- The "Basic Motor Control" button lets you move the motors around.
  - You can push the four buttons to move the motors.
  - Very simple.
- The "Motor Control" button lets you move the motors around, but in a more advanced way.
  - If there is no dot, click anywhere on the square to guess where the motor position is.
  - If there is a dot, click anywhere on the square to move the motor to that spot.
  - The "Set Center" is equivalent to clicking in the center.
  - The "Reset Position" button removes the dot so you can re-guess.

## How it works

If you're a person who is good at programming, and you are here to fix the gigantic mess that is this entire thing, here's how it works.

(By the way, most of the programs have comments at the top explaining what they do and, to some extent, how they work.)

- `sendcmd.py` will send one command to the motors. I don't know why we can't send multiple commands with one process, but for some reason we have to end and restart the serial connection for each command. It's really annoying and results in somewhere near a 0.1s overhead per command. Which is clearly ridiculous.
- `server.py` is, as you have probably guessed, the server. It basically just serves all the xml files, but there's also some code to move the motor according to the files.
- The `client` folder contains the client files. Yes, the entire website is written in SVG. I told you this was a mess. Each of the files contains a comment at the top which contains a summary of the file. Good luck with that.
- `terminal.py` lets you move the motors from a simple terminal interface. I'm not going to repeat how it works here, you can go look at the file yourself.
- The horribly named `datas` folder contains all of the data files you have generated. Each one is formatted as a description followed by a list of commands. The description ends on the first empty line. The commands are almost the same format as the commands given to `terminal.py`, however passing "0" as the first character indicates that the program should wait for the specified amount of seconds.

Anyways, good luck fixing this!
