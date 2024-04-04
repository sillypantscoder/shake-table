"""
Starts an HTTP server letting you move the motors in various ways.

To see the client source pages, look at the "client" folder.

The actual server content is handled in the "get" and "post" functions.
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import typing
import json
import subprocess
import math
import os
import threading
import time

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

class HttpResponse(typing.TypedDict):
	status: int
	headers: dict[str, str]
	content: "str | bytes"

# Keep track of the motor position.
motor_pos: "None | tuple[float, float]" = None

def generate_file(filename: str, time: float, xMotion: float, yMotion: float):
	"""Generate a file using a simple sine wave function. Accessed from the 'create.xml' file."""
	points: list[tuple[float, float, float]] = []
	for i in range(round(time * 2)):
		x = xMotion * math.sin(i)
		y = yMotion * math.sin(i + 1)
		points.append((i / 2, x, y))
	while os.path.exists("datas/" + filename + ".json"):
		filename += "2"
	f = open("datas/" + filename + ".json", "w")
	f.write(json.dumps(points))
	f.close()

def set_motor_rel_pos(xDiff: float, yDiff: float, duration: float):
	"""Moves the motor by a specific amount. xDiff and yDiff should be from -0.5 to 0.5, and duration is in seconds."""
	speeds = [
		round(xDiff * (1 / duration) * -300),
		round(yDiff * (1 / duration) * -300)
	]
	if speeds[0] >= 255: speeds[0] = 255
	if speeds[1] >= 255: speeds[1] = 255
	if speeds[0] <= -255: speeds[0] = -255
	if speeds[1] <= -255: speeds[1] = -255
	subprocess.run(["python3", "sendcmd.py", f"1{speeds[1]}"])
	subprocess.run(["python3", "sendcmd.py", f"2{speeds[0]}"])
	time.sleep(duration)
	subprocess.run(["python3", "sendcmd.py", "10"])
	subprocess.run(["python3", "sendcmd.py", "20"])

def set_motor_pos(x: float, y: float, duration: float):
	"""Uses the `motor_pos` variable to move the motor to an absolute location. x and y are from -0.5 to 0.5, and duration is in seconds."""
	global motor_pos
	assert motor_pos != None
	diff = [
		x - motor_pos[0],
		y - motor_pos[1]
	]
	motor_pos = (x, y)
	set_motor_rel_pos(diff[0], diff[1], duration)

def run_file(data: list[tuple[float, float, float]]):
	"""Runs a file by moving to all the points in order."""
	print(f"[0/{len(data)}]")
	set_motor_pos(data[0][1], data[0][2], 1)
	print(f"[1/{len(data)}]")
	for i in range(len(data)):
		if i == 0: continue
		timeStart = data[i - 1][0]
		timeEnd = data[i][0]
		timeDiff = timeEnd - timeStart
		# decrease: list[float] = [*posDiff]
		# if posDiff[0] >= 256: decrease[0] += posDiff[0] - 255
		# if posDiff[1] >= 256: decrease[1] += posDiff[1] - 255
		set_motor_pos(data[i - 1][1], data[i - 1][2], timeDiff * 2)
		print(f"[{i + 1}/{len(data)}]")

def start_running_file(data: str):
	"""Starts a thread that runs a specified file. Allows the server to continue handling other requests after this one has finished."""
	t: list[tuple[float, float, float]] = json.loads(data)
	# t = [
	# 	(i / 10, round(math.sin(0.5 * math.pi * i) * 0.01, 2), 0)
	# 	for i in range(20)
	# 	# (0,   0.5, 0.5),
	# 	# (0.1, 0.4, 0.5),
	# 	# (0.2, 0.4, 0.4),
	# 	# (0.3, 0.6, 0.4),
	# 	# (0.4, 0.5, 0.5)
	# ]
	# write_file("datas/sine.json", json.dumps(t))
	threading.Thread(target=run_file, args=(t,)).start()

def get(path: str) -> HttpResponse:
	"""Return the results of a GET request."""
	if path == "/":
		return {
			"status": 200,
			"headers": {
				"Content-Type": "image/svg+xml"
			},
			"content": read_file("client/home.xml")
		}
	elif path == "/motors":
		return {
			"status": 200,
			"headers": {
				"Content-Type": "image/svg+xml"
			},
			"content": read_file("client/motors.xml").replace(b"{{MOTORLOC}}", b"null" if motor_pos == None else f"[{motor_pos[0]}, {motor_pos[1]}]".encode("UTF-8"))
		}
	elif path == "/create":
		return {
			"status": 200,
			"headers": {
				"Content-Type": "image/svg+xml"
			},
			"content": read_file("client/create.xml")
		}
	elif path == "/run":
		return {
			"status": 200,
			"headers": {
				"Content-Type": "image/svg+xml"
			},
			"content": read_file("client/run.xml")
		}
	elif path.startswith("/set/run/"):
		setname = path[9:-1]
		contents = read_file("datas/" + setname + ".json").decode("UTF-8")
		start_running_file(contents)
		return {
			"status": 200,
			"headers": {
				"Content-Type": "image/svg+xml"
			},
			"content": read_file("client/watch.xml").decode("UTF-8").replace("{{FILENAME}}", setname).replace("{{FILEINFO}}", contents)
		}
	elif path.startswith("/set/"):
		setname = path[5:-1]
		contents = read_file("datas/" + setname + ".json")
		return {
			"status": 200,
			"headers": {
				"Content-Type": "image/svg+xml"
			},
			"content": read_file("client/view.xml").decode("UTF-8").replace("{{FILENAME}}", setname).replace("{{FILEINFO}}", contents.decode("UTF-8"))
		}
	elif path == "/data/ls":
		return {
			"status": 200,
			"headers": {
				"Content-Type": "text/plain"
			},
			"content": "\n".join([x[:-5] for x in os.listdir("datas")])
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
	if path == "/create":
		info = json.loads(body.decode("UTF-8"))
		generate_file(info["filename"], info["time"], info["xMotion"], info["yMotion"])
		return {
			"status": 200,
			"headers": {},
			"content": f""
		}
	elif path == "/guess/pos":
		info = json.loads(body.decode("UTF-8"))
		motor_pos = [info[0], info[1]] # type: ignore
		return {
			"status": 200,
			"headers": {},
			"content": f""
		}
	elif path == "/guess/remove":
		motor_pos = None
		return {
			"status": 200,
			"headers": {},
			"content": f""
		}
	elif path == "/move_motor":
		if motor_pos == None: return {
			"status": 400,
			"headers": {},
			"content": "Please define the motor position first"
		}
		info = [float(x) for x in body.decode("UTF-8").split("\n")]
		dist = math.dist(info, [*motor_pos])
		threading.Thread(target=set_motor_pos, args=(*info, dist * 7)).start()
		return {
			"status": 200,
			"headers": {},
			"content": f""
		}
	else:
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
		return;
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
