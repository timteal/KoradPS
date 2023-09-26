'''
Serial controller for Korad Power suplies.

The KoradPS class implements all the serial commands the power supply uses.

Presumably this will work for all KD3000/6000 power supplies since I think the serial commands are the same.
(It can handle multiple channels but defaults to 1), but I've only tested this on my KD3005P, so... Caveat User.

'''


import serial
import time

class KoradPS:

	def __init__(self,port='/dev/ttyACM0'):
		print("connecting..")
		self.ser = serial.Serial(port=port, baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=1)
		self.responseTime = 0.050 # per the manual response time is 50ms. 

	# ISET<X>:<parameter> - Set Current Limit, example ISET1:3.5 sets the channel 1 current limit to 3.5A
	# ISET<X>? - Return Current Limit setting
	# IOUT<X>? - Return actual output current
	def read_current_limit(self, channel=1):
		cmd = "ISET{}?".format(channel)
		return self.read(cmd)
	
	def set_current_limit(self, amps, channel=1):
		cmd = 'ISET{}:{}'.format(channel, amps)
		self.send(cmd)

	def read_current_output(self, channel=1):

		cmd = "IOUT{}?".format(channel)
		return self.read(cmd)

	# VSET<X>:<parameter> - Set Voltage Limit
	# VSET<X>? - Return Voltage Limit setting
	# VOUT<X>? - Return actual output voltage
	def read_voltage_limit(self, channel=1):
		cmd = "VSET{}?".format(channel)
		return self.read(cmd)
	
	def set_voltage_limit(self, volts, channel=1):
		cmd = 'VSET{}:{}'.format(channel, volts)
		self.send(cmd)

	def read_voltage_output(self, channel=1):
		cmd = "VOUT{}?".format(channel)
		return self.read(cmd)

	# OUT<Y> - Turns output on or off. 1=On, 0=Off	
	def output_on(self):
		cmd = "OUT1"
		self.send(cmd)

	def output_off(self):
		cmd = "OUT0"
		self.send(cmd)

	# STATUS? - Returns the power supply status as two bytes.
	# bit 0 is the CC/CV mode
	# bit 8 is the output on/off (I think. I'm guessing a bit because I think the manual is wrong.)
	def get_status(self):
		cmd = "STATUS?"
		self.ser.write(cmd.encode())
		response = self.ser.read(2)

		if ((bin(ord(response))[2]) == '0'):
			mode = "CC"
		elif ((bin(ord(response))[2]) == '1'):
			mode = "CV"
		else:
			mode=(bin(ord(response))[2])

		if ((bin(ord(response))[-1]) == '0'):
			output = "OFF"
		elif ((bin(ord(response))[-1]) == '1'):
			output = "ON"
		else:
			output =(bin(ord(response))[-1])

		return ("Mode: {}, Output: {}".format(mode,output))

	# *IDN? - Returns the device identification
	def get_id(self):
		cmd = "*IDN?"
		self.ser.write(cmd.encode())
		response = self.ser.readline().decode()
		return response	

	# RCL<X> - Recalls a panel setting, where X is a number 1-5. Example: RCL2 recalls panel setting 2
	# SAV<X> - Stores the panel settings in memory number X
	# Both RCL and SAV turn the power suplies output OFF, I have intentionally not changed that behavior
	def recall_settings(self, setting):
		cmd = "RCL{}".format(setting)
		self.send(cmd)

	def save_settings(self, setting):
		cmd = "SAV{}".format(setting)
		self.send(cmd)

	# OCP<X> - Over current. OCP1 sets OCP on, OCP0 to off
	def ocp_on(self):
		cmd = "OCP1"
		self.send(cmd)

	def ocp_off(self):
		cmd = "OCP0"
		self.send(cmd)

	# send() and read() do the actual serial communication for most of the other functions
	def send(self,cmd):
		self.ser.write(cmd.encode())
		time.sleep(self.responseTime)

	def read(self,cmd):
		self.ser.write(cmd.encode())
		response = self.ser.read(5)
		return float(response.decode())
