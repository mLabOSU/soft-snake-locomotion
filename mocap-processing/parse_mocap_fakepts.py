import csv
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from collections import defaultdict

# TODO: write out bodyref and curvature to a new csv

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

# this "order" mapping is used to record the actual order of points along snake body moving in one direction
# so rigid body 2 is left most, then 5, 1, ... 
# this should be fixed in future data during mocap configuration so that rigid body indexes are ordered in a reasonable way (ex: left to right on snake body)
order = [2, 5, 1, 4, 6, 3]
skip_frames = 5 # set this to control how many frames we sample for calculations/plots
xidx, yidx = 0, 2 # (set plot yaxis to mocap zaxis) this mapping is determined based on mocap calibration - check whether y or z is second axis in ground plane
xview = (-0.15, 0.15) # set this based on actual range of coordinates in mocap collection
yview = (0, 0.3) # set this based on actual range of coordinates in mocap collection

if __name__ == "__main__":
	time = []
	bodies = defaultdict(list)
	# bodies structure stores all coordinates for all rigid bodies
	# format: bodies[rigid body index][frame index] = (x, y, z)
	# rigid body index may not correspond to points in order across snake body - we should fix this in future data
	
	# data structures to save shape variable properties for each frame
	k1, k2, center1, center2, bodyref = [], [], [], [], []
	
	# read csv file and save a list of coordinates over time for each rigid body
	with open('optitrack_sample.csv') as csvfile:
		reader = csv.DictReader(csvfile)
		for (i, row) in enumerate(reader):
			if i % skip_frames == 0:
				# subtract time/frame columns and then divide by three (x, y, z) to get total number of rigid bodies
				num_bodies = (len(row) - 2) / 3 
				try:
					time.append(float(row['Time']))
					for i in range(1, num_bodies + 1):
						key = 'Rigid Body ' + str(i)
						x = float(row[key + ' X'])
						y = float(row[key + ' Y'])
						z = float(row[key + ' Z'])
						bodies[i].append((x, y, z))
							
					# add a fake point at the midpoint of each leg by doing some silly average math
					# (we need a third point to get circles)
					# this will not be a part of future scripts when we collect data with three points per actuator	
					x1, y1, z1 = bodies[order[0]][-1]
					x2, y2, z2 = bodies[order[2]][-1]
					x3, y3, z3 = x2+((x2-x1)*0.1), (y1+y2)/2, (z1+z2)/2
					bodies[5].append((x3, y3, z3))
					# compute shape variable in this frame
					radius, center = find_circle((x1, y1, z1), (x2, y2, z2), (x3, y3, z3))
					direction = curvature_dir((x1, y1, z1), (x2, y2, z2), (x3, y3, z3))
					k1.append(direction/radius)
					center1.append(center)
					
					x1, y1, z1 = bodies[order[3]][-1]
					x2, y2, z2 = bodies[order[5]][-1]
					x3, y3, z3 = x2+((x2-x1)*0.2), (y1+y2)/2, (z1+z2)/2
					bodies[6].append((x3, y3, z3))
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
					continue
	
	# get bounds for plots
	kmin = min(min(k1), min(k2)) # smallest negative curvature
	kmax = max(max(k1), max(k2)) # largest positive curvature
	kabs = max(abs(kmin), abs(kmax)) # largest curvature magnitude
	
	plt.title("Shape variables over time")
	plt.ylim((kmin, kmax))
	plt.xlim((0, max(time)/2))
	plt.plot(time, k1)
	plt.plot(time, k2)
	plt.xlabel("Time (s)")
	plt.ylabel("Curvature (m)")
	plt.legend(['k1', 'k2'], loc='upper right')
	plt.show()

	fig, ax = plt.subplots()
	plt.title("Gait plot (k1 vs k2)")
	plt.ylim((-1*kabs, kabs))
	plt.xlim((-1*kabs, kabs))
	plt.plot(k1, k2)
	plt.xlabel("k1 (m)")
	plt.ylabel("k2 (m)")
	ax.set_aspect(1)
	plt.show()
	
	fig, ax = plt.subplots()
	plt.title("Animated view of snake body")
	plt.xlabel("Mocap xaxis (m)")
	plt.ylabel("Mocap zaxis (m)")
	plt.ylim(yview)
	plt.xlim(xview)
	ax.set_aspect(1)
	
	# add initial points to lists for first plot - get x, z coordinate for every rigid body at frame 0
	xlist = [bodies[j][0][xidx] for j in order]
	ylist = [bodies[j][0][yidx] for j in order]
	
	# initialize snake and curves to be updated
	line, = ax.plot(xlist, ylist)
	plt.setp(line, linewidth=3)
	circ1 = plt.Circle((center1[0][xidx], center1[0][yidx]), radius=(abs(1/k1[0])), color='g', fill=False)
	ax.add_patch(circ1)
	circ2 = plt.Circle((center2[0][xidx], center2[0][yidx]), radius=(abs(1/k2[0])), color='r', fill=False)
	ax.add_patch(circ2)
	text = ax.text(-0.1, 0.02, '')
	
	# update all rigid body points, both circles, and curvature label text
	def animate(i):
		xlist = [bodies[j][i][xidx] for j in order]
		ylist = [bodies[j][i][yidx] for j in order]
		line.set_xdata(xlist)
		line.set_ydata(ylist)

		circ1.center = (center1[i][xidx], center1[i][yidx])
		circ1.radius = abs(1 / (k1[i]))
		
		circ2.center = (center2[i][xidx], center2[i][yidx])
		circ2.radius = abs(1 / (k2[i]))
		
		text.set_text('k1=' + str(k1[i]) + ', k2=' + str(k2[i]))
		return line, circ1, circ2, text

	ani = animation.FuncAnimation(fig, animate, frames=len(bodies[1]), interval=2, blit=False)
	
	# uncomment this to save the animation to a video file
	#Writer = animation.writers['ffmpeg']
	#writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)	
	#ani.save('curvatures.mp4', writer=writer)
	
	plt.show()
	
	# write curvatures and bodyref to another csv file