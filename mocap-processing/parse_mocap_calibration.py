import csv
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from collections import defaultdict
from parse_utilities import *

# this "order" mapping is used to record the actual order of points along snake marker moving in one direction
# so marker 2 is left most, then 5, 1, ... 
# this should be fixed in future data during mocap configuration so that  marker indexes are ordered in a reasonable way (ex: left to right on snake marker)
order = [6, 5, 2, 4, 3, 1]
skip_frames = 10 # set this to control how many frames we sample for calculations/plots
xidx, yidx = 0, 2 # (set plot yaxis to mocap zaxis) this mapping is determined based on mocap calibration - check whether y or z is second axis in ground plane
xview = (-0.2, 0.2) # set this based on actual range of coordinates in mocap collection
yview = (0, 0.4) # set this based on actual range of coordinates in mocap collection
dirname = 'optitrack_calibration_1_23_17'
dt_frame = 0.008333

if __name__ == "__main__":
	time = []
	dt = dt_frame * skip_frames
	points_per_sec = 1 / dt
	markers = defaultdict(list)
	# markers structure stores all coordinates for all markers
	# format: markers[marker index][frame index] = (x, y, z)
	# marker index may not correspond to points in order across snake marker - we should fix this in future data
	
	# data structures to save shape variable properties for each frame
	k1, k2, center1, center2, bodyref = [], [], [], [], []
	angle1, angle2 = [], []
	length1, length2 = [], []
	
	# read csv file and save a list of coordinates over time for each marker
	with open(dirname + '/data.csv') as csvfile:
		reader = csv.DictReader(csvfile)
		for (i, row) in enumerate(reader):
			if i % skip_frames == 0:
				# subtract time/frame columns and then divide by three (x, y, z) to get total number of  markers
				num_markers = (len(row) - 2) / 3
				try:
					time.append(float(row['Time']))
					for i in range(1, num_markers + 1):
						key = 'Marker ' + str(i)
						x = float(row[key + ' X'])
						y = float(row[key + ' Y'])
						z = float(row[key + ' Z'])
						markers[i].append((x, y, z))
							
					# add a fake point at the midpoint of each leg by doing some silly average math
					# (we need a third point to get circles)
					# this will not be a part of future scripts when we collect data with three points per actuator	
					x1, y1, z1 = markers[order[0]][-1]
					x2, y2, z2 = markers[order[1]][-1]
					x3, y3, z3 = markers[order[2]][-1]
					# compute shape variable in this frame
					radius, center = find_circle((x1, y1, z1), (x2, y2, z2), (x3, y3, z3))
					direction = curvature_dir((x1, y1, z1), (x2, y2, z2), (x3, y3, z3), xidx, yidx)
					k1.append(direction/radius)
					center1.append(center)
					angle1.append(direction*find_angle(radius, (x1, y1, z1), (x3, y3, z3)))
					length1.append(abs(radius*angle1[-1]))
					
					x1, y1, z1 = markers[order[3]][-1]
					x2, y2, z2 = markers[order[4]][-1]
					x3, y3, z3 = markers[order[5]][-1]
					# compute shape variable in this frame
					radius, center = find_circle((x1, y1, z1), (x2, y2, z2), (x3, y3, z3))
					direction = curvature_dir((x1, y1, z1), (x2, y2, z2), (x3, y3, z3), xidx, yidx)
					k2.append(direction/radius)
					center2.append(center)
					angle2.append(direction*find_angle(radius, (x1, y1, z1), (x3, y3, z3)))
					length2.append(abs(radius*angle2[-1]))
					
					# find center point of line between actuator end points
					x1, y1, z1 = markers[order[2]][-1]
					x2, y2, z2 = markers[order[3]][-1]
					x3, y3, z3 = (x1+x2)/2, (y1+y2)/2, (z1+z2)/2
					bodyref.append((x3, y3, z3))
					
				except ValueError:
					print "Unable to parse number from some row."
					time.pop()
					
					continue
	
	# get bounds for plots
	kmin = min(min(k1), min(k2)) # smallest negative curvature
	kmax = max(max(k1), max(k2)) # largest positive curvature
	
	# this is kind of a gross way of estimating where to sync the pwm and curvature time series
	maxidx = k1.index(kmax)
	minidx = k2.index(kmin)
	startidx = maxidx - int(np.floor(65*points_per_sec))
	stopidx = minidx + int(np.floor(60*points_per_sec))
	
	# generate three different step functions to correspond to pwm calibration steps
	pwmup = [2 * np.floor((t-time[startidx])/5.5) for (i, t) in enumerate(time) if i < maxidx and i >= startidx]
	pwmdown = [20 - (2 * np.floor((t-time[maxidx])/5.5)) for (i, t) in enumerate(time) if i < minidx and i >= maxidx]
	pwmup2 = [-20 + (2 * np.floor((t-time[minidx])/5.5)) for (i, t) in enumerate(time) if i < stopidx and i >= minidx]
	
	plt.title("Shape/PWM over time")
	plt.plot(time[startidx:stopidx], k1[startidx:stopidx])
	plt.plot(time[startidx:stopidx], k2[startidx:stopidx])
	plt.plot(time[startidx:stopidx], pwmup+pwmdown+pwmup2)
	plt.xlabel("Time (s)")
	plt.legend(['k1', 'k2', 'pwm'], loc='upper right')
	plt.savefig(dirname + '/k1_k2_vs_t.png')
	plt.show()

	plt.title("Shape (angle1) as a function of PWM")
	plt.plot(pwmup, angle1[startidx:maxidx], marker='o', linestyle='None')
	plt.plot(pwmdown, angle1[maxidx:minidx], marker='o', linestyle='None')
	plt.plot(pwmup2, angle1[minidx:stopidx], marker='o', linestyle='None')
	plt.xlabel("PWM Duty Cycle (%)")
	plt.ylabel("Angle (rad)")
	plt.savefig(dirname + '/a1_vs_pwm.png')
	plt.show()
	
	plt.title("Shape (angle2) as a function of PWM")
	plt.plot(pwmup, angle2[startidx:maxidx], marker='o', linestyle='None')
	plt.plot(pwmdown, angle2[maxidx:minidx], marker='o', linestyle='None')
	plt.plot(pwmup2, angle2[minidx:stopidx], marker='o', linestyle='None')
	plt.xlabel("PWM Duty Cycle (%)")
	plt.ylabel("Angle (rad)")
	plt.savefig(dirname + '/a2_vs_pwm.png')
	plt.show()
	
	# fit polynomials to PWM as a function of curvature for gait control
	# https://docs.scipy.org/doc/numpy/reference/generated/numpy.polyfit.html
	f = open(dirname + '/coefficients.txt', 'w')
	f.write("Coefficients for best-fit cubic functions:\n")
	p = np.polyfit(angle1[startidx:maxidx], pwmup, 3)
	f.write("a1 positive " + str(p) + "\n")
	f_a1_pos = np.poly1d(p)
	p = np.polyfit(angle2[startidx:maxidx], pwmup, 3)
	f.write("a2 positive" + str(p) + "\n")
	f_a2_pos = np.poly1d(p)
	mididx = (maxidx + minidx) / 2
	p = np.polyfit(angle1[mididx:minidx], pwmdown[(maxidx-minidx)/2:], 3)
	f.write("a1 negative " + str(p) + "\n")
	f_a1_neg = np.poly1d(p)
	p = np.polyfit(angle2[mididx:minidx], pwmdown[(maxidx-minidx)/2:], 3)
	f.write("a2 negative " + str(p) + "\n")
	f_a2_neg = np.poly1d(p)
	f.close()
	
	plt.title("PWM as a function of shape angle (a1)")
	plt.plot(angle1[startidx:stopidx], pwmup+pwmdown+pwmup2, marker='o', linestyle='None')
	plt.plot(angle1[startidx:maxidx], f_a1_pos(angle1[startidx:maxidx]))
	plt.plot(angle1[mididx:minidx], f_a1_neg(angle1[mididx:minidx]))
	plt.ylabel("PWM Duty Cycle (%)")
	plt.xlabel("Angle (rad)")
	plt.savefig(dirname + '/pwm_vs_a1.png')
	plt.show()
	
	plt.title("PWM as a function of angle (a2)")
	plt.plot(angle2[startidx:stopidx], pwmup+pwmdown+pwmup2, marker='o', linestyle='None')
	plt.plot(angle2[startidx:maxidx], f_a2_pos(angle2[startidx:maxidx]))
	plt.plot(angle2[mididx:minidx], f_a2_neg(angle2[mididx:minidx]))
	plt.ylabel("PWM Duty Cycle (%)")
	plt.xlabel("Angle (rad)")
	plt.savefig(dirname + '/pwm_vs_a2.png')
	plt.show()
	