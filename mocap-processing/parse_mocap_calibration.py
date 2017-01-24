import csv
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from collections import defaultdict

# this "order" mapping is used to record the actual order of points along snake body moving in one direction
# so rigid body 2 is left most, then 5, 1, ... 
# this should be fixed in future data during mocap configuration so that rigid body indexes are ordered in a reasonable way (ex: left to right on snake body)
order = [6, 5, 2, 4, 3, 1]
skip_frames = 10 # set this to control how many frames we sample for calculations/plots
xidx, yidx = 0, 2 # (set plot yaxis to mocap zaxis) this mapping is determined based on mocap calibration - check whether y or z is second axis in ground plane
xview = (-0.2, 0.2) # set this based on actual range of coordinates in mocap collection
yview = (0, 0.4) # set this based on actual range of coordinates in mocap collection
dirname = 'optitrack_calibration_1_23_17'
dt_frame = 0.008333

# borrowed this circle function from online:
# http://stackoverflow.com/questions/20314306/find-arc-circle-equation-given-three-points-in-space-3d
def find_circle(p1, p2, p3):
	A = np.array(list(p1))
	B = np.array(list(p2))
	C = np.array(list(p3))
	a = np.linalg.norm(C - B)
	b = np.linalg.norm(C - A)
	c = np.linalg.norm(B - A)
	s = (a + b + c) / 2
	R = a*b*c / 4 / np.sqrt(s * (s - a) * (s - b) * (s - c))
	b1 = a*a * (b*b + c*c - a*a)
	b2 = b*b * (a*a + c*c - b*b)
	b3 = c*c * (a*a + b*b - c*c)
	P = np.column_stack((A, B, C)).dot(np.hstack((b1, b2, b3)))
	P /= b1 + b2 + b3
	return R, P
		
# get cross product of "vectors" between center point of actuator and both ends (in horizontal plane)
# use direction (into/outof horizontal plane) of this vector to designate positive/negative curvature
# return 1 or -1 to indicate direction
def curvature_dir(p1, p2, p3):
	A = np.array([p1[xidx], p1[yidx]])
	B = np.array([p2[xidx], p2[yidx]])
	C = np.array([p3[xidx], p3[yidx]])
	nv = np.cross((B-A), (B-C))
	if nv != 0:
		return nv / abs(nv)
	else:
		return 0

if __name__ == "__main__":
	time = []
	dt = dt_frame * skip_frames
	points_per_sec = 1 / dt
	bodies = defaultdict(list)
	# bodies structure stores all coordinates for all rigid bodies
	# format: bodies[rigid body index][frame index] = (x, y, z)
	# rigid body index may not correspond to points in order across snake body - we should fix this in future data
	
	# data structures to save shape variable properties for each frame
	k1, k2, center1, center2, bodyref = [], [], [], [], []
	
	# read csv file and save a list of coordinates over time for each rigid body
	with open(dirname + '/data.csv') as csvfile:
		reader = csv.DictReader(csvfile)
		for (i, row) in enumerate(reader):
			if i % skip_frames == 0:
				# subtract time/frame columns and then divide by three (x, y, z) to get total number of rigid bodies
				num_bodies = (len(row) - 2) / 3
				try:
					time.append(float(row['Time']))
					for i in range(1, num_bodies + 1):
						key = 'Marker ' + str(i)
						x = float(row[key + ' X'])
						y = float(row[key + ' Y'])
						z = float(row[key + ' Z'])
						bodies[i].append((x, y, z))
							
					# add a fake point at the midpoint of each leg by doing some silly average math
					# (we need a third point to get circles)
					# this will not be a part of future scripts when we collect data with three points per actuator	
					x1, y1, z1 = bodies[order[0]][-1]
					x2, y2, z2 = bodies[order[1]][-1]
					x3, y3, z3 = bodies[order[2]][-1]
					# compute shape variable in this frame
					radius, center = find_circle((x1, y1, z1), (x2, y2, z2), (x3, y3, z3))
					direction = curvature_dir((x1, y1, z1), (x2, y2, z2), (x3, y3, z3))
					k1.append(direction/radius)
					center1.append(center)
					
					x1, y1, z1 = bodies[order[3]][-1]
					x2, y2, z2 = bodies[order[4]][-1]
					x3, y3, z3 = bodies[order[5]][-1]
					# compute shape variable in this frame
					radius, center = find_circle((x1, y1, z1), (x2, y2, z2), (x3, y3, z3))
					direction = curvature_dir((x1, y1, z1), (x2, y2, z2), (x3, y3, z3))
					k2.append(direction/radius)
					center2.append(center)
					
					# find center point of line between actuator end points
					x1, y1, z1 = bodies[order[2]][-1]
					x2, y2, z2 = bodies[order[3]][-1]
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
	plt.plot(time[maxidx], k1[maxidx], marker='o')
	plt.plot(time[minidx], k1[minidx], marker='o')
	plt.xlabel("Time (s)")
	plt.legend(['k1', 'k2', 'pwm'], loc='upper right')
	plt.savefig(dirname + '/k1_k2_vs_t.png')
	plt.show()

	plt.title("Curvature (k1) as a function of PWM")
	plt.plot(pwmup, k1[startidx:maxidx], marker='o', linestyle='None')
	plt.plot(pwmdown, k1[maxidx:minidx], marker='o', linestyle='None')
	plt.plot(pwmup2, k1[minidx:stopidx], marker='o', linestyle='None')
	plt.xlabel("PWM Duty Cycle (%)")
	plt.ylabel("Curvature (m)")
	plt.savefig(dirname + '/k1_vs_pwm.png')
	plt.show()
	
	plt.title("Curvature (k2) as a function of PWM")
	plt.plot(pwmup, k2[startidx:maxidx], marker='o', linestyle='None')
	plt.plot(pwmdown, k2[maxidx:minidx], marker='o', linestyle='None')
	plt.plot(pwmup2, k2[minidx:stopidx], marker='o', linestyle='None')
	plt.xlabel("PWM Duty Cycle (%)")
	plt.ylabel("Curvature (m)")
	plt.savefig(dirname + '/k2_vs_pwm.png')
	plt.show()
	
	# fit polynomials to PWM as a function of curvature for gait control
	# https://docs.scipy.org/doc/numpy/reference/generated/numpy.polyfit.html
	f = open(dirname + '/coefficients.txt', 'w')
	f.write("Coefficients for best-fit cubic functions:\n")
	p = np.polyfit(k1[startidx:maxidx], pwmup, 3)
	f.write("k1 positive " + str(p) + "\n")
	f_k1_pos = np.poly1d(p)
	p = np.polyfit(k2[startidx:maxidx], pwmup, 3)
	f.write("k2 positive" + str(p) + "\n")
	f_k2_pos = np.poly1d(p)
	mididx = (maxidx + minidx) / 2
	p = np.polyfit(k1[mididx:minidx], pwmdown[(maxidx-minidx)/2:], 3)
	f.write("k1 negative " + str(p) + "\n")
	f_k1_neg = np.poly1d(p)
	p = np.polyfit(k2[mididx:minidx], pwmdown[(maxidx-minidx)/2:], 3)
	f.write("k2 negative " + str(p) + "\n")
	f_k2_neg = np.poly1d(p)
	f.close()
	
	plt.title("PWM as a function of curvature (k1)")
	plt.plot(k1[startidx:stopidx], pwmup+pwmdown+pwmup2, marker='o', linestyle='None')
	plt.plot(k1[startidx:maxidx], f_k1_pos(k1[startidx:maxidx]))
	plt.plot(k1[mididx:minidx], f_k1_neg(k1[mididx:minidx]))
	plt.ylabel("PWM Duty Cycle (%)")
	plt.xlabel("Curvature (m)")
	plt.savefig(dirname + '/pwm_vs_k1.png')
	plt.show()
	
	plt.title("PWM as a function of curvature (k2)")
	plt.plot(k2[startidx:stopidx], pwmup+pwmdown+pwmup2, marker='o', linestyle='None')
	plt.plot(k2[startidx:maxidx], f_k2_pos(k2[startidx:maxidx]))
	plt.plot(k2[mididx:minidx], f_k2_neg(k2[mididx:minidx]))
	plt.ylabel("PWM Duty Cycle (%)")
	plt.xlabel("Curvature (m)")
	plt.savefig(dirname + '/pwm_vs_k2.png')
	plt.show()
	

