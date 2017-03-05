import serial # python -m pip install pyserial
import numpy as np
from time import sleep
import matplotlib.pyplot as plt

# TODO: determine actual mapping function from curvature -> pressure -> pwm dutycycle

if __name__ == "__main__":
	# TODO: change these?
	a = np.pi / 2 # wide dimension of ellipse
	b = (np.pi / 2) # narrow dimension of ellipse
	max_dutycycle = 28
	tilt_angle = np.pi / 4
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
	plt.plot(np.round(pwmpair1), np.round(pwmpair2))
	plt.xlabel("k1 (m)")
	plt.ylabel("k2 (m)")
	ax.set_aspect(1)
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
