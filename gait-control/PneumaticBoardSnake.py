# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 10:44:14 2017

@author: Lily Orth-Smith
#python 3
"""

import serial # python -m pip install pyserial
from time import sleep

class PneumaticBoard:
    def __init__(self, actuators=2, port='COM3', baud=9600):
        self.pwmList = [0] * actuators
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
		
    def setPWMList(self, pwmList):
        self.pwmList = pwmList
        self.updatePWM()

    def setPWM(self, pwm, index):
        self.pwmList[index] = pwm
        self.updatePWM()
		
    def updatePWM(self):
        command = b'v '
        count = 0
        for pwm in self.pwmList:
            count+=1
            if pwm <= 0:                            #if pwm < 0, then send to left side (even indices), 
                pwm = abs(int(round(pwm)))          #if pwm > 0, then send to right side (odd indices)
                command = command + str(abs(pwm)).encode('ascii') + b' 0'#sends pwm to left, 0 to right 
            else: 
                pwm = abs(int(round(pwm)))
                command = command + b'0 ' + str(abs(pwm)).encode('ascii') #send 0 to right, pwm to left
            if count < len(self.pwmList):
                command = command + b' '
        self.ser.write(command)#.encode('utf-8'))
        print(command)
        sleep(0.5)
        
    def printPWM(self):
        for pwm in self.pwmList:
            print (pwm)
            
            

