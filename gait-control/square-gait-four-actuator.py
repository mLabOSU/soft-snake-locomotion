# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 11:14:11 2017

@author: jrs
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 11:20:09 2017

@author: jrs
"""

import numpy as np
import matplotlib.pyplot as plt
from PneumaticBoard import *

board = PneumaticBoard(actuators=4, port='COM4')

max_dutycycle = 12#24 for extensible
phase = 4 #length of 1 cycle in seconds (left and right actuators actuate)
data_points = 2 * phase
cycles = 20
time = phase * cycles
cycle_gap = 1 #lag in seconds between the different square waves
cycle_gap_points = int(cycle_gap * 2)
rest_gap = 1
rest_gap_points = rest_gap * 2

#square wave --also think about square wave w rest (output = 0) in middle
zero_list = np.zeros(data_points)
zero_list[0:int(data_points/2)] = 1
zero_list[int(data_points/2):int(data_points)] = -1
zero_list = np.insert(zero_list, int(data_points), rest_gap_points* [0])
zero_list = np.insert(zero_list, int(data_points/2), rest_gap_points* [0])
print(zero_list)
square_wave = np.tile(zero_list, cycles)

wave_list = []
#indices = range(cycle_gap_points, data_points + cycle_gap_points)
for i in range(4): #in range actuators -1
    square_wave = square_wave * -1
    wave = square_wave
    wave = np.insert(wave, 0, [0] * i * cycle_gap_points)
    wave = np.insert(wave, len(wave), [0] * (4 -i) * cycle_gap_points)
    wave_list.append(max_dutycycle * wave)

print(wave_list)

board.on()
for i in range(len(wave_list[0])):
    board.setPWMList([wave_list[0][i], 0*wave_list[1][i], 0*wave_list[2][i], 0 *wave_list[3][i]])
board.off()
board.close()
