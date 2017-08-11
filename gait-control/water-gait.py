# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 11:01:18 2017

@author: jrs
"""
"""
important note: each actuator should be plugged in the same way, i.e., left side, right side, left side, right side (no alternating)
"""
import numpy as np
import matplotlib.pyplot as plt
from PneumaticBoard import *

board = PneumaticBoard()

max_dutycycle = 12 #24 for extensible
vertical_dilation = 1
phase_shift = 3 * np.pi/4
front_dilation = 1
back_dilation = 1.5
horizontal_dilation = 1

#tlist = np.arange(0, 10, 0.2)
tlist = np.arange(0, 180, 0.5) #changed to 0.5 (from 0.2) to match sleep value in pneumatic board.
                              #if values NOT the same, get dilation of functions that does not show up in graphs.
	# curvatures vary circularly together
k1 = front_dilation * vertical_dilation * np.cos(tlist)
k2 = back_dilation * vertical_dilation * -1 * np.sin(tlist * horizontal_dilation + phase_shift)

	# note that the two lines below are temporary - we need an actual function to map curvature -> pwm rate
	# each pwmpair will be used to inflate one chamber or the other on a single actuator
	# (negative value => chamber 1, positive value => chamber 2)
pwmpair1 = max_dutycycle * k1
pwmpair2 = max_dutycycle * k2

fig, ax = plt.subplots()
plt.title("Gait plot (k1 vs k2)")
plt.plot(k1, k2)
plt.xlabel("k1 (m)")
plt.ylabel("k2 (m)")
ax.set_aspect(1)
plt.show()

board.on()
for (i, t) in enumerate(tlist):
    board.setPWMList([pwmpair1[i], pwmpair2[i]])
board.off()
board.close()