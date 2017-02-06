import serial # python -m pip install pyserial
import numpy as np
from time import sleep
import matplotlib.pyplot as plt

# TODO: determine actual mapping function from curvature -> pressure -> pwm dutycycle

if __name__ == "__main__":
	# TODO: change these?
	a = np.pi / 2 # wide dimension of ellipse
	b = 3*(np.pi / 8) # narrow dimension of ellipse
	max_dutycycle = 28
	tilt_angle = 3 * np.pi / 4
	sin_tilt = np.sin(tilt_angle)
	cos_tilt = np.cos(tilt_angle)
	
	tlist = np.arange(0, 20, 0.2)
	# parametric form of a rotated ellipse
	k1 = (a * cos_tilt * np.cos(tlist)) - (b * sin_tilt * np.sin(tlist))
	k2 = (a * sin_tilt * np.cos(tlist)) + (b * cos_tilt * np.sin(tlist))
	# note that the two lines below are temporary - we need an actual function to map curvature -> pwm rate
	# each pwmpair will be used to inflate one chamber or the other on a single actuator 
	# (negative value => chamber 1, positive value => chamber 2)
	pwmpair1 = max_dutycycle * k1
	pwmpair2 = max_dutycycle * k2
	
	# show gait shape cycle that we are about to send
	fig, ax = plt.subplots()
	plt.title("Gait plot (k1 vs k2)")
	plt.plot(k1, k2)
	plt.xlabel("k1 (m)")
	plt.ylabel("k2 (m)")
	ax.set_aspect(1)
	plt.show()
	
	ser = serial.Serial('COM3', 9600)
	print "Starting up control board..."
	sleep(5)
	ser.write(b'y')
	
	commands = [b'', b'', b'', b'']
	for (i, t) in enumerate(tlist):
		# we'll have to see how effective integer rounding is on this limited pwm range
		pwm1 = int(round(pwmpair1[i]))
		pwm2 = int(round(pwmpair2[i]))
		if pwm1 < 0:
			commands[0] = b'v 0 ' + str(abs(pwm1))
			commands[1] = b'v 1 0'
		else:
			commands[0] = b'v 0 0'
			commands[1] = b'v 1 '+ str(abs(pwm1))
			
		if pwm2 < 0:
			commands[2] = b'v 2 ' + str(abs(pwm2))
			commands[3] = b'v 3 0'
		else:
			commands[2] = b'v 2 0'
			commands[3] = b'v 3 '+ str(abs(pwm2))
		
		for c in commands:
			sleep(0.1)
			ser.write(c)
			print c

	# turn everything off and close handles
	commands = [b'v 0 0', b'v 1 0', b'v 2 0', b'v 3 0']
	for c in commands:
		ser.write(c)
		print c
		sleep(0.2)
		
	ser.write(b'n')
	print b'n'
	ser.close()
