import serial # python -m pip install pyserial
from time import sleep

class PneumaticBoard:
	def __init__(self, valves=8, port='COM3', baud=9600):
		self.pwmList = [0] * valves
		self.ser = serial.Serial(port, baud)
		print ("Please wait for control board connection...")
		sleep(5)
		print ("Done.")
		
	def on(self):
		print ("Valves on.")
		self.ser.write(b'y')
	
	def off(self):
		print ("Valves off.")
		self.ser.write(b'n')
		
	def close(self):
		self.ser.close()
		
	def setPWM(self, pwmList):
		self.pwmList = pwmList
		self.updatePWM()
		
	def setPWM(self, pwm, index):
		self.pwmList[index] = pwm
		self.updatePWM()
		
	def updatePWM(self):
		command = 'v'
		for pwm in self.pwmList:
			pwm = abs(int(round(pwm)))
			command = command + ' ' + str(abs(pwm))
		
		self.ser.write(command.encode('utf-8'))
		#print (command)
		
	def printPWM(self):
		for pwm in self.pwmList:
			print (pwm)
		
		
