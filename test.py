"""
This is going to be replacing the files
"""

import subprocess
import time

time_interval = 0.2

try:
	while True:
		time.sleep(time_interval)
		subprocess.run(["python3", "sendcmd.py", "2100"])
		time.sleep(time_interval)
		subprocess.run(["python3", "sendcmd.py", "2-100"])
except KeyboardInterrupt:
	print("Stopped")
	subprocess.run(["python3", "sendcmd.py", "20"])
