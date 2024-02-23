"""
A simple terminal interface that lets you manually type in the command line argument.
"""

import subprocess

while True:
	m = input()
	subprocess.run(["python3", "newshaketable4.py", m])
