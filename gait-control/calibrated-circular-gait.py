import serial # python -m pip install pyserial
import numpy as np
from time import sleep
import matplotlib.pyplot as plt

if __name__ == "__main__":	
	amplitude = 12
	tlist = np.arange(0, 20, 0.2)
	
	# curvatures vary circularly together
	pwmpair1 = amplitude*np.cos(tlist)
	pwmpair2 = amplitude*np.sin(tlist)
	
	# show gait shape cycle that we are about to send
	fig, ax = plt.subplots()
	plt.title("Gait plot (k1 vs k2)")
	plt.plot(pwmpair1, pwmpair2)
	plt.xlabel("k1 (m)")
	plt.ylabel("k2 (m)")
	ax.set_aspect(1)
	plt.show()
	
	f_k1_pos = np.poly1d(np.array([ 0.01051142, -0.15138011,  1.48211063,  5.8264363 ]))
	f_k2_pos = np.poly1d(np.array([ 0.00836058, -0.07102387,  1.64875152,  5.95781371]))
	f_k1_neg = np.poly1d(np.array([  4.16024921e-04,  -1.92087293e-02,   7.24122142e-01,  -3.67617749e+00]))
	f_k2_neg = np.poly1d(np.array([  1.25008787e-03,   4.03949229e-02,   1.54652035e+00,  -1.53512998e+00]))
	
	# each pwmpair will be used to inflate one chamber or the other on a single actuator 
	# (negative value => chamber 1, positive value => chamber 2)
	# This is NumPy "fancy indexing" to remap positive and negative array values differently (http://stackoverflow.com/questions/12424824/how-i-can-i-conditionally-change-the-values-in-a-numpy-array-taking-into-account)
	pwmpair1[pwmpair1 > 0] = f_k1_pos(pwmpair1[pwmpair1 > 0])
	pwmpair1[pwmpair1 < 0] = f_k1_neg(pwmpair1[pwmpair1 < 0])
	pwmpair2[pwmpair2 > 0] = f_k2_pos(pwmpair2[pwmpair2 > 0])
	pwmpair2[pwmpair2 < 0] = f_k2_neg(pwmpair2[pwmpair2 < 0])
	
	# show pwm sequences that we are about to send
	plt.title("PWM command sequence plot")
	plt.plot(tlist, pwmpair1)
	plt.plot(tlist, pwmpair2)
	plt.xlabel("Time (s)")
	plt.ylabel("PWM duty cycle (%)")
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