import serial # python -m pip install pyserial
import numpy as np
from time import sleep
import matplotlib.pyplot as plt

# TODO: determine actual mapping function from curvature -> pressure -> pwm dutycycle
# TODO: check that these sleep times work

if __name__ == "__main__":	
	# TODO: change these?
	k_amplitude = 1
	max_dutycycle = 20 / k_amplitude
	
	tlist = np.arange(0, 20, 0.1)
	# curvatures vary circularly together
	k1 = k_amplitude * np.cos(tlist)
	k2 = k_amplitude * np.sin(tlist)
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
	
	ser = serial.Serial('COM4', 9600)
	print "Starting up control board..."
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
			ser.write(c)
			print c
			sleep(0.01)
		sleep(0.1)

	# turn everything off and close handles
	commands = [b'v 0 0', b'v 1 0', b'v 2 0', b'v 3 0']
	for c in commands:
		ser.write(c)
		print c
		sleep(0.01)
		
	ser.write(b'n')
	print b'n'
	ser.close()