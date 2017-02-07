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
	
		command = b''
	for (i, t) in enumerate(tlist):
		# we'll have to see how effective integer rounding is on this limited pwm range
		pwm1 = int(round(pwmpair1[i]))
		pwm2 = int(round(pwmpair2[i]))
		if pwm1 < 0:
			command = b'v ' + str(abs(pwm1)) + b' 0 '
		else:
			command = b'v 0 ' + str(abs(pwm1)) + b' '
			
		if pwm2 < 0:
			command += str(abs(pwm2)) + b' 0'
		else:
			command += b' 0 ' + str(abs(pwm2))
		
		ser.write(command)
		print command
		sleep(0.5)

	# turn everything off and close handles
	command = b'v 0 0 0 0'
	ser.write(command)
	sleep(1)
		
	ser.write(b'n')
	print b'n'
	ser.close()