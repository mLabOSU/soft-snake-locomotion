import csv
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from collections import defaultdict
from parse_utilities import *

# this "order" mapping is used to record the actual order of points along snake marker moving in one direction
# so  marker 2 is left most, then 5, 1, ... 
# this should be fixed in future data during mocap configuration so that  marker indexes are ordered in a reasonable way (ex: left to right on snake marker)
order = [2, 4, 6, 5, 3, 1]
skip_frames = 10 # set this to control how many frames we sample for calculations/plots
xidx, yidx = 0, 2 # (set plot yaxis to mocap zaxis) this mapping is determined based on mocap calibration - check whether y or z is second axis in ground plane
xview = (-0.2, 0.2) # set this based on actual range of coordinates in mocap collection
yview = (0, 0.4) # set this based on actual range of coordinates in mocap collection
dirname = 'optitrack_circle_1_30_17'

if __name__ == "__main__":
	time = []
	markers = defaultdict(list)
	# markers structure stores all coordinates for all  markers
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
	amin = min(min(angle1), min(angle2)) # smallest negative curvature
	amax = max(max(angle1), max(angle2)) # largest positive curvature
	aabs = max(abs(amin), abs(amax)) # largest curvature magnitude
	
	plt.title("Shape over time ($\Theta_1$ and $\Theta_2$)")
	plt.xlim((0, max(time)))
	plt.plot(time, angle1)
	plt.plot(time, angle2)
	plt.xlabel("Time (s)")
	plt.ylabel("Angle (rad)")
	plt.legend(['$\Theta_1$', '$\Theta_2$'], loc='upper right')
	plt.savefig(dirname + '/a1_a2_vs_t.png')
	plt.show()

	fig, ax = plt.subplots()
	plt.title("Gait Plot ($\Theta_1$ vs $\Theta_2$)")
	plt.ylim((-1*np.pi, np.pi))
	plt.xlim((-1*np.pi, np.pi))
	plt.plot(angle1, angle2)
	tlist = np.arange(0, 6*np.pi, 0.2)
	plt.plot(np.pi/2*np.sin(tlist), np.pi/2*np.cos(tlist))
	plt.xlabel("$\Theta_1$ (rad)")
	plt.ylabel("$\Theta_2$ (rad)")
	plt.legend(['Experimental (mocap)', 'Ideal gait'], loc='upper right')
	ax.set_aspect(1)
	plt.savefig(dirname + '/a1_vs_a2.png')
	plt.show()
	
	plt.title("Elongation over time")
	plt.xlim((0, max(time)/2))
	plt.plot(time, length1)
	plt.plot(time, length2)
	plt.xlabel("Time (s)")
	plt.ylabel("Actuator length (m)")
	plt.legend(['length1', 'length2'], loc='upper right')
	plt.savefig(dirname + '/l1_l2_vs_t.png')
	plt.show()
	
	plt.title("Body frame position")
	xpos = [x for (x, y, z) in bodyref]
	zpos = [z for (x, y, z) in bodyref]
	plt.plot(xpos, zpos)
	plt.xlabel("Mocap zaxis")
	plt.ylabel("Mocap xaxis (m)")
	plt.savefig(dirname + '/bodyx_vs_bodyz.png')
	plt.show()

	fig, ax = plt.subplots()
	plt.title("Animated view of snake body")
	plt.xlabel("Mocap xaxis (m)")
	plt.ylabel("Mocap zaxis (m)")
	plt.ylim(yview)
	plt.xlim(xview)
	ax.set_aspect(1)
	
	# add initial points to lists for first plot - get x, z coordinate for every marker at frame 0
	xlist = [markers[j][0][xidx] for j in order]
	ylist = [markers[j][0][yidx] for j in order]
	
	# initialize snake and curves to be updated
	line, = ax.plot(xlist, ylist)
	plt.setp(line, linewidth=3)
	circ1 = plt.Circle((center1[0][xidx], center1[0][yidx]), radius=(abs(1/k1[0])), color='g', fill=False)
	ax.add_patch(circ1)
	circ2 = plt.Circle((center2[0][xidx], center2[0][yidx]), radius=(abs(1/k2[0])), color='r', fill=False)
	ax.add_patch(circ2)
	text = ax.text(-0.1, 0.02, '')
	
	# update all marker points, both circles, and curvature label text
	def animate(i):
		xlist = [markers[j][i][xidx] for j in order]
		ylist = [markers[j][i][yidx] for j in order]
		line.set_xdata(xlist)
		line.set_ydata(ylist)

		circ1.center = (center1[i][xidx], center1[i][yidx])
		circ1.radius = abs(1 / (k1[i]))
		
		circ2.center = (center2[i][xidx], center2[i][yidx])
		circ2.radius = abs(1 / (k2[i]))
		
		text.set_text('k1=' + str(k1[i]) + ', k2=' + str(k2[i]))
		return line, circ1, circ2, text

	ani = animation.FuncAnimation(fig, animate, frames=len(markers[1]), interval=1, blit=False)
	# uncomment this to save the animation to a video file
	#Writer = animation.writers['ffmpeg']
	#writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)	
	#ani.save('curvatures.mp4', writer=writer)
	
	plt.show()
	