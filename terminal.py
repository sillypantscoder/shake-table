"""
A simple terminal interface that lets you manually type in
the command line argument to `sendcmd.py`.
"""

import subprocess

while True:
	m = input()
	subprocess.run(["python3", "sendcmd.py", m])
