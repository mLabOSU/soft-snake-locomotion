import serial # python -m pip install pyserial
import numpy as np
from time import sleep
import matplotlib.pyplot as plt

# TODO: determine actual mapping function from curvature -> pressure -> pwm dutycycle

if __name__ == "__main__":	
	max_dutycycle = 20
	delta_t = 5
	delta_pwm = 2
	
	pwmlist = range(0, max_dutycycle+delta_pwm, delta_pwm) # step up to max
	pwmlist += range(max_dutycycle-delta_pwm, -1*(max_dutycycle+delta_pwm), -1*delta_pwm) # step down to -max
	pwmlist += range(-1*(max_dutycycle-delta_pwm), delta_pwm, delta_pwm) # step up to 0
	tlist = range(0, (len(pwmlist))*delta_t, delta_t)
	print pwmlist
	
	# show gait shape cycle that we are about to send
	fig, ax = plt.subplots()
	plt.title("PWM step plot for gait calibration")
	plt.step(tlist, pwmlist)
	plt.xlabel("time (s)")
	plt.ylabel("PWM (% duty cycle)")
	plt.show()
	
	ser = serial.Serial('COM3', 9600)
	print "Starting up control board..."
	sleep(5)
	ser.write(b'y')
	
	commands = [b'', b'', b'', b'']
	for pwm in pwmlist:
		if pwm < 0:
			commands[0] = b'v 0 ' + str(abs(pwm))
			commands[1] = b'v 1 0'
			commands[2] = b'v 2 ' + str(abs(pwm))
			commands[3] = b'v 3 0'
		else:
			commands[0] = b'v 0 0'
			commands[1] = b'v 1 '+ str(abs(pwm))
			commands[2] = b'v 2 0'
			commands[3] = b'v 3 '+ str(abs(pwm))
		
		for c in commands:
			sleep(0.1)
			ser.write(c)
			print c
		sleep(delta_t)

	# turn everything off and close handles
	commands = [b'v 0 0', b'v 1 0', b'v 2 0', b'v 3 0']
	for c in commands:
		ser.write(c)
		print c
		sleep(0.2)
		
	ser.write(b'n')
	print b'n'
	ser.close()