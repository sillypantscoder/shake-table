"""
Starts an HTTP server letting you move the motors in various ways.

To see the client source pages, look at the "client" folder.

The actual servery stuff is handled in the "get" and "post" functions.
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import typing
import subprocess
import os
import threading
import time
import datetime
from urllib.parse import unquote

hostName = "0.0.0.0"
serverPort = 8080

def read_file(filename: str) -> bytes:
	f = open(filename, "rb")
	t = f.read()
	f.close()
	return t

def write_file(filename: str, content: bytes):
	f = open(filename, "wb")
	f.write(content)
	f.close()

original_time = datetime.datetime.now().timestamp()
def getTime():
	"""Get time in seconds since the program has started."""
	return datetime.datetime.now().timestamp() - original_time

class HttpResponse(typing.TypedDict):
	status: int
	headers: dict[str, str]
	content: "str | bytes"

class Point(typing.TypedDict):
	x: float
	y: float

TRACK_SIZE: float = 400

motor_pos: typing.Union[Point, None] = None

motor_speeds: Point = { "x": 0, "y": 0 }
last_motor_times: Point = { "x": getTime(), "y": getTime() }

def sendCommand(motor: int, speed: int):
	"""Send one command to the motors. Also, update the simulated motor position."""
	subprocess.run(["python3", "sendcmd.py", f"{motor}{speed}"])
	# Update the motor position
	if motor_pos == None: return
	# - Figure out what motor to update
	motorname: typing.Literal["x", "y"] = "y"
	if motor == 2: motorname = "x"
	# - Find time interval
	timeInterval = getTime() - last_motor_times[motorname]
	# - Update the position
	motor_pos[motorname] += timeInterval * motor_speeds[motorname] * -1# (-1 if motorname == "x" else 1)
	# - Update the new motor speed
	motor_speeds[motorname] = speed
	last_motor_times[motorname] = getTime()
	# print(motor_pos)

def run_file(data: list[tuple[float, float]]):
	"""Runs a file by moving the motors according to the data."""
	print(f"[0/{len(data)}]")
	for i in range(len(data)):
		if data[i][0] == 0:
			time.sleep(data[i][1])
		else:
			sendCommand(int(data[i][0]), int(data[i][1]))
		print(f"[{i + 1}/{len(data)}]")
	sendCommand(1, 0)
	sendCommand(2, 0)

def start_running_file(data: str):
	"""Starts a thread that runs a specified file. Allows the server to continue handling other requests after this one has finished."""
	maindata = data[data.index("\n\n") + 2:]
	t: list[tuple[float, float]] = [(int(x[0]), float(x[1:]) ) for x in maindata.split("\n")]
	threading.Thread(target=run_file, args=(t,)).start()

def generate_file(filename: str, frequency: float):
	"""Generate a file with back-and-forth motion. Accessed from the 'create.xml' file."""
	fileData = f"Move back and forth horizontally at {frequency} Hz.\n"
	motorTime = 0.5 / frequency
	motorSpeed = round(46 / (motorTime + 0.26))
	motorTime = round(motorTime, 2)
	for _ in range(round(4)):
		fileData += f"""
2{motorSpeed}
0{motorTime}
2{-motorSpeed}
0{motorTime}"""
	while os.path.exists("datas/" + filename + ".txt"):
		filename += "2"
	f = open("datas/" + filename + ".txt", "w")
	f.write(fileData)
	f.close()

def get(path: str) -> HttpResponse:
	"""Return the results of a GET request."""
	if path == "/": # Home page
		return {
			"status": 200,
			"headers": {
				"Content-Type": "image/svg+xml"
			},
			"content": read_file("client/home.xml")
		}
	elif path == "/motors": # More complex motor control page.
		return {
			"status": 200,
			"headers": {
				"Content-Type": "image/svg+xml"
			},
			"content": read_file("client/motors.xml").replace(b"{{MOTORLOC}}",
				("null" if motor_pos == None else f"[{motor_pos['x']}, {motor_pos['y']}]").encode("UTF-8")
			) # This part sends the motor location to the page.
		}
	elif path == "/motors_basic": # Less complex motor control page.
		return {
			"status": 200,
			"headers": {
				"Content-Type": "image/svg+xml"
			},
			"content": read_file("client/motors_basic.xml")
		}
	elif path == "/run": # List of files.
		return {
			"status": 200,
			"headers": {
				"Content-Type": "image/svg+xml"
			},
			"content": read_file("client/run.xml")
		}
	elif path == "/create": # Create a file page.
		return {
			"status": 200,
			"headers": {
				"Content-Type": "image/svg+xml"
			},
			"content": read_file("client/create.xml")
		}
	elif path.startswith("/set/run/"): # Start running a file.
		setname = unquote(path[9:-1])
		contents = read_file("datas/" + setname + ".txt").decode("UTF-8")
		start_running_file(contents)
		return {
			"status": 200,
			"headers": {
				"Content-Type": "image/svg+xml"
			},
			"content": read_file("client/watch.xml").decode("UTF-8").replace("{{FILENAME}}", setname).replace("{{FILEINFO}}", contents)
		}
	elif path.startswith("/set/"): # View a file's info.
		setname = unquote(path[5:-1])
		contents = read_file("datas/" + setname + ".txt")
		return {
			"status": 200,
			"headers": {
				"Content-Type": "image/svg+xml"
			},
			"content": read_file("client/view.xml").decode("UTF-8").replace("{{FILENAME}}", setname).replace("{{FILEINFO}}", contents.decode("UTF-8"))
		}
	elif path == "/data/ls": # Get the list of files.
		return {
			"status": 200,
			"headers": {
				"Content-Type": "text/plain"
			},
			"content": "\n".join([x[:-4] for x in os.listdir("datas")])
		}
	else: # 404 page
		return {
			"status": 404,
			"headers": {
				"Content-Type": "text/html"
			},
			"content": f""
		}

def post(path: str, body: bytes) -> HttpResponse:
	"""Return the results of a POST request."""
	global motor_pos
	if path == "/move_motor": # Send one command to the motor.
		# The request's body should contain the command to send,
		# in the same format as `terminal.py`.
		data = body.decode("UTF-8")
		motor = int(data[0])
		speed = int(data[1:])
		sendCommand(motor, speed)
		return {
			"status": 200,
			"headers": {},
			"content": f""
		}
	elif path == "/guess/remove": # Remove the motor's position.
		motor_pos = None
		return {
			"status": 200,
			"headers": {},
			"content": f""
		}
	elif path == "/guess/pos": # Guess the motor's position.
		data = body.decode("UTF-8").split("\n")
		x = float(data[0])
		y = float(data[1])
		motor_pos = { "x": x, "y": y }
		return {
			"status": 200,
			"headers": {},
			"content": f""
		}
	elif path == "/create": # Create a file with a specific frequency.
		info = body.decode("UTF-8").split("\n")
		filename = info[0]
		frequency = float(info[1])
		generate_file(filename, frequency)
		# The actual file creation takes place in the `generate_file` function.
		return {
			"status": 200,
			"headers": {},
			"content": f""
		}
	else: # 404 POST
		return {
			"status": 404,
			"headers": {
				"Content-Type": "text/html"
			},
			"content": f""
		}

class MyServer(BaseHTTPRequestHandler):
	"""A crazy thing that handles HTTP requests that I generally don't mess with"""
	def do_GET(self):
		global running
		res = get(self.path)
		self.send_response(res["status"])
		for h in res["headers"]:
			self.send_header(h, res["headers"][h])
		self.end_headers()
		c = res["content"]
		if isinstance(c, str): c = c.encode("utf-8")
		self.wfile.write(c)
	def do_POST(self):
		res = post(self.path, self.rfile.read(int(self.headers["Content-Length"])))
		self.send_response(res["status"])
		for h in res["headers"]:
			self.send_header(h, res["headers"][h])
		self.end_headers()
		c = res["content"]
		if isinstance(c, str): c = c.encode("utf-8")
		self.wfile.write(c)
	def log_message(self, format: str, *args: typing.Any) -> None:
		return; # Get rid of the server log messages
		if 400 <= int(args[1]) < 500:
			# Errored request!
			print(u"\u001b[31m", end="")
		print(args[0].split(" ")[0], "request to", args[0].split(" ")[1], "(status code:", args[1] + ")")
		print(u"\u001b[0m", end="")
		# don't output requests

if __name__ == "__main__":
	# Run the server!
	running = True
	webServer = HTTPServer((hostName, serverPort), MyServer)
	webServer.timeout = 1
	print("Server started http://%s:%s" % (hostName, serverPort))
	while running:
		try:
			webServer.handle_request()
		except KeyboardInterrupt:
			running = False
	webServer.server_close()
	print("Server stopped")
