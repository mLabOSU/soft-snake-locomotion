import serial # python -m pip install pyserial
import numpy as np
from time import sleep
import matplotlib.pyplot as plt

if __name__ == "__main__":	
	amplitude = np.pi / 2 # maximum bend angle
	tlist = np.arange(0, 6*np.pi, 0.2)
	
	# curvatures vary circularly together
	pwmpair1 = amplitude*np.cos(tlist)
	pwmpair2 = amplitude*np.sin(tlist)
	
	# show gait shape cycle that we are about to send
	fig, ax = plt.subplots()
	plt.title("Gait plot ($\Theta_1$ vs $\Theta_2$)")
	plt.plot(pwmpair1, pwmpair2)
	plt.xlabel("$\Theta_1$ (rad)")
	plt.ylabel("$\Theta_2$ (rad)")
	ax.set_aspect(1)
	plt.show()
	
	f_a1_pos = np.poly1d(np.array([5.13055934, -10.16367391,  14.63574296,   5.4293181]))
	f_a2_pos = np.poly1d(np.array([3.70092955,  -4.62358907,  15.60205793,   5.81143012]))
	f_a1_neg = np.poly1d(np.array([-0.61980325, -1.99119348,  7.55328677, -3.6788138]))
	f_a2_neg = np.poly1d(np.array([0.47923358,   3.19683353,  13.80613014,  -1.73902919]))
	
	# each pwmpair will be used to inflate one chamber or the other on a single actuator 
	# (negative value => chamber 1, positive value => chamber 2)
	# This is NumPy "fancy indexing" to remap positive and negative array values differently (http://stackoverflow.com/questions/12424824/how-i-can-i-conditionally-change-the-values-in-a-numpy-array-taking-into-account)
	pwmpair1[pwmpair1 > 0] = f_a1_pos(pwmpair1[pwmpair1 > 0])
	pwmpair1[pwmpair1 < 0] = f_a1_neg(pwmpair1[pwmpair1 < 0])
	pwmpair2[pwmpair2 > 0] = f_a2_pos(pwmpair2[pwmpair2 > 0])
	pwmpair2[pwmpair2 < 0] = f_a2_neg(pwmpair2[pwmpair2 < 0])
	
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