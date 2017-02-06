import csv
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from collections import defaultdict
from parse_utilities import *

skip_frames = 10 # set this to control how many frames we sample for calculations/plots
xidx, yidx = 0, 2 # (set plot yaxis to mocap zaxis) this mapping is determined based on mocap calibration - check whether y or z is second axis in ground plane
xview = (-0.2, 0.2) # set this based on actual range of coordinates in mocap collection
yview = (0, 0.4) # set this based on actual range of coordinates in mocap collection
dirname = 'optitrack_pressure_2_3_17'
pmin = 0
pmax = 350
pdelta = 50
prefixes = ['b', 'g', 'r', 'nt']

if __name__ == "__main__":
	time = []
	markers = defaultdict(list)
	# markers structure stores all coordinates for all  markers
	# format: markers[marker index][frame index] = (x, y, z)
	# marker index may not correspond to points in order across snake marker - we should fix this in future data
	
	pressure, curvature, angle, length = defaultdict(list), defaultdict(list), defaultdict(list), defaultdict(list)
	
	for s in prefixes:
		for p in range(pmin, pmax+pdelta, pdelta):
			# data structures to save shape variable properties for each frame
			ktemp, atemp, ltemp = [], [], []
			
			# read csv file and save a list of coordinates over time for each marker
			with open(dirname + '/' + s + '/' + s + str(p) + '.csv') as csvfile:
				reader = csv.DictReader(csvfile)
				for (i, row) in enumerate(reader):
					if i % skip_frames == 0:
						# subtract time/frame columns and then divide by three (x, y, z) to get total number of  markers
						num_markers = (len(row) - 2) / 3
						try:
							time.append(float(row['Time']))
							for j in range(1, num_markers + 1):
								key = 'Marker ' + str(j)
								x = float(row[key + ' X'])
								y = float(row[key + ' Y'])
								z = float(row[key + ' Z'])
								markers[j].append((x, y, z))
							
							# this is really a hack! 
							# use the knowledge that actuator points are aligning along z to order them correctly
							points = []
							for j in range(1, num_markers + 1):	
								x1, y1, z1 = markers[j][-1]
								points.append((z1, (x1, y1, z1)))
							points.sort()
							
							for j in range(1, num_markers + 1):
								markers[j][-1] = points[j-1][1]
							
							# compute shape variable in this frame
							radius, center = find_circle(points[0][1], points[1][1], points[2][1])
							direction = curvature_dir(points[0][1], points[1][1], points[2][1], xidx, yidx)
							ktemp.append(direction/radius)
							atemp.append(direction*find_angle(radius, points[0][1], points[2][1]))
							ltemp.append(abs(radius*atemp[-1]))
							
						except ValueError:
							print "Unable to parse number from some row."
							time.pop()
							continue
				
			pressure[s].append(float(p) / 100.0)
			curvature[s].append(abs(sum(ktemp)) / len(ktemp))
			angle[s].append(abs(sum(atemp)) / len(atemp))
			length[s].append(abs(sum(ltemp)) / len(ltemp))
	
	plt.title(r"Pressure-Angle Curve (Alpha)")
	for s in prefixes:
		plt.plot(pressure[s], angle[s], marker='o')
	plt.xlabel("Pressure (psi)")
	plt.ylabel("Angle (rad)")
	plt.legend(prefixes, loc='upper left')
	plt.savefig(dirname + '/a_vs_p.png')
	plt.show()
	
	plt.title(r"Pressure-Curvature Curve (Kappa)")
	for s in prefixes:
		plt.plot(pressure[s], curvature[s], marker='o')
	plt.xlabel("Pressure (psi)")
	plt.ylabel("Curvature (1/m)")
	plt.legend(prefixes, loc='upper left')
	plt.savefig(dirname + '/k_vs_p.png')
	plt.show()
	
	plt.title("Pressure-Length Curve (L)")
	for s in prefixes:
		plt.plot(pressure[s], length[s], marker='o')
	plt.xlabel("Pressure (psi)")
	plt.ylabel("Actuator Length (m)")
	plt.legend(prefixes, loc='upper left')
	plt.savefig(dirname + '/l_vs_p.png')
	plt.show()

	fig, ax = plt.subplots()
	plt.title("Animated view of snake body")
	plt.xlabel("Mocap xaxis (m)")
	plt.ylabel("Mocap zaxis (m)")
	plt.ylim(yview)
	plt.xlim(xview)
	ax.set_aspect(1)
	
	# add initial points to lists for first plot - get x, z coordinate for every marker at frame 0
	xlist = [markers[j][0][xidx] for j in [1, 2, 3]]
	ylist = [markers[j][0][yidx] for j in [1, 2, 3]]
	
	# initialize snake and curves to be updated
	line, = ax.plot(xlist, ylist)
	plt.setp(line, linewidth=3)
	
	# update all marker points, both circles, and curvature label text
	def animate(i):
		xlist = [markers[j][i][xidx] for j in [1, 2, 3]]
		ylist = [markers[j][i][yidx] for j in [1, 2, 3]]
		line.set_xdata(xlist)
		line.set_ydata(ylist)
		return line

	ani = animation.FuncAnimation(fig, animate, frames=len(markers[1]), interval=1, blit=False)
	plt.show()
	