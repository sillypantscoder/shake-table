import serial
import sys

crc = 0
def crc_clear():
	global crc
def crc_update(data: int):
	global crc
	crc = crc ^ (data << 8)
	for _bit in range(0, 8):
		if (crc&0x8000)  == 0x8000:
			crc = ((crc << 1) ^ 0x1021)
		else:
			crc = crc << 1
	return

# Set up serial connection with the Roboclaw controller
ser = serial.Serial('/dev/ttyS0', 38400, timeout=5)

def writebyte(val: int):
	crc_update(val)
	ser.write(bytes([val]))
def readbyte():
	data = ser.read(1)
	print(repr(data))
	if len(data):
		val = ord(data)
		crc_update(val)
		return (1, val)
	return (0, 0)
# Function to send a command to the Roboclaw controller
def move_motor(motor: int = 1, speed: int = 64):
	# sendcommand
	crc_clear()
	crc_update(0x80)
	ser.write(bytes([0x80]))
	cmd_int = 0 if speed >= 0 else 1
	# Speed greater than 0 is forwards
	# Less than 0 is backwards
	cmd_int += [0, 4][motor - 1]
	crc_update(cmd_int)
	ser.write(bytes([cmd_int]))
	# writebyte(val)
	writebyte(abs(speed))
	# writeword(crc & 0xFFFF)
	wordwrite = crc & 0xFFFF
	writebyte((wordwrite >> 8) & 0xFF)
	writebyte(wordwrite & 0xFF)
	return
	val = readbyte()
	if len(val) > 0:
		if val[0]:
			return True
	return False

# move_motor(-32)
move_motor(int(sys.argv[1][0]), int(sys.argv[1][1:]))

# input()
# move_motor(0)

ser.close()