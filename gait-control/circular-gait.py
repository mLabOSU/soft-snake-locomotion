# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 11:20:09 2017

@author: jrs
"""

import serial # python -m pip install pyserial
import numpy as np
import matplotlib.pyplot as plt
from PneumaticBoard import *

board = PneumaticBoard()

max_dutycycle = 24 #24 for extensible

tlist = np.arange(0, 10, 0.2)
	# curvatures vary circularly together
k1 = np.cos(tlist)
k2 = np.sin(tlist)
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

for (i, t) in enumerate(tlist):  
    board.setPWMList([pwmpair1[i], pwmpair2[i]])
board.close()