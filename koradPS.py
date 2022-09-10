'''
Serial controller for Korad Power suplies.

The KoradPS class implements all the serial commands the power supply uses.

Presumably this will work for all KD3000/6000 power supplies since I think the serial commands are the same.
(It can handle multiple channels but defaults to 1), but I've only tested this on my KD3005P, so... Caveat User.

There are also some functions defined outside of the class that I find helpful on occasion. They are more script-y and less polished,
I just modify them as needed.
	testPS() puts the power supply (and the code) through most of it's paces and was mainly written for debugging
	stream() is just that, constantly reads the voltage and current output, fast-ish. 

'''


import serial
import time

class KoradPS:

	def __init__(self,port='/dev/ttyACM0'):
		print("connecting..")
		self.ser = serial.Serial(port=port, baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=1)
		self.responseTime = 0.050 # per the manual response time is 50ms. 

	def iset(self, amps=None, channel=1):
	# iset() sets the current limit, or returns the limit setting if no "amps" value is passed
	# ISET<X>:<parameter> - Set Current Limit, example ISET1:3.5 sets the channel 1 current limit to 3.5A
	# ISET<X>? - Return Current Limit setting
		if amps != None:
			cmd = 'ISET{}:{}'.format(channel, amps)
			self.send(cmd)
		else:
			cmd = "ISET{}?".format(channel)
			return self.read(cmd)


	def vset(self, volts=None, channel=1):
	# vset() sets the voltage limit, or returns the limit setting if no "volts" value is passed
	# VSET<X>:<parameter> - Set Voltage Limit
	# VSET<X>? - Return Voltage Limit setting
		if volts != None:
			cmd = 'VSET{}:{}'.format(channel, volts)
			self.send(cmd)
		else:
			cmd = "VSET{}?".format(channel)
			return self.read(cmd)


	def iout(self, channel=1):
	# IOUT<X>? - Return actual output current
		cmd = "IOUT{}?".format(channel)
		return self.read(cmd)		


	def vout(self, channel=1):
	# VOUT<X>? - Return actual output voltage
		cmd = "VOUT{}?".format(channel)
		return self.read(cmd)	


	def on(self):
	# OUT<Y> - Turns output on or off. 1=On, 0=Off	
		cmd = "OUT1"
		self.send(cmd)

	def off(self):
	# OUT<Y> - Turns output on or off. 1=On, 0=Off	
		cmd = "OUT0"
		self.send(cmd)


	def status(self):
	# STATUS? - Returns the power supply status as two bytes.
	# bit 0 is the CC/CV mode
	# bit 8 is the output on/off (I think. I'm guessing a bit because I think the manual is wrong.)

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

	def id(self):
	# *IDN? - Returns the device identification
		cmd = "*IDN?"
		self.ser.write(cmd.encode())
		response = self.ser.readline().decode()
		return response	

	def recall(self, setting=1):
	# RCL<X> - Recalls a panel setting, where X is a number 1-5. Example: RCL2 recalls panel setting 2
	# Both RCL and SAV turn the power suplies output OFF, I have intentionally not changed that behavior
		cmd = "RCL{}".format(setting)
		self.send(cmd)

	def save(self, setting=1):
	# SAV<X> - Stores the panel settings in memory number 1
	# Both RCL and SAV turn the power suplies output OFF, I have intentionally not changed that behavior
		cmd = "SAV{}".format(setting)
		self.send(cmd)

	def ocp(self, setting=1):
	# OCP<X> - Over current. OCP1 sets OCP on, OCP0 to off, defaults to on
		cmd = "OCP{}".format(setting)
		self.send(cmd)

	def send(self,cmd):
	# send() and read() do the actual serial communication for most of the other functions
			self.ser.write(cmd.encode())
			time.sleep(self.responseTime)

	def read(self,cmd):
	# send() and read() do the actual serial communication for most of the other functions
		self.ser.write(cmd.encode())
		response = self.ser.read(5)
		return float(response.decode())




'''
--- outside of class functions below here ---
'''

def testPS():
	# simple test function
	#	calls all the KoradPS functions at some point in the test
	#	cycles the power supply from 0 to 5V 
	#	reads the actual voltage and current outputs periodically
	#	typically I'll connect the power supply output to a load like a dc motor

	ps = KoradPS(port='/dev/cu.usbmodem00368207024E1')

	print(ps.id())

	ps.iset(.4)
	ps.on()
	ps.ocp()

	while(True):
		print(ps.status())
		for i in range(0,30,3):
			ps.vset(i/6)
			if (i==6):
				ps.save(setting=1)
				ps.on()
			if (i==18):
				ps.recall(setting=1)
				ps.on()
			print("Settings: {}V, {}A. Output: {}V, {}A".format(ps.vset(),ps.iset(),ps.vout(),ps.iout()))
			time.sleep(2)

		ps.off()
		print("Waiting 3 seconds..")
		print(ps.status())
		time.sleep(3)
		ps.on()

def stream():
	ser = serial.Serial(port='/dev/ttyACM0', baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=1)
	while True:
		channel=1
		cmd = "VOUT{}?".format(channel)
		ser.write(cmd.encode())
		volts = ser.read(5)
		cmd = "IOUT{}?".format(channel)
		ser.write(cmd.encode())
		amps = ser.read(5)
		print("V: {}V C: {}A".format(volts.decode(),amps.decode()))
		time.sleep(.1)




if __name__ == "__main__":

	testPS()
	#stream()



