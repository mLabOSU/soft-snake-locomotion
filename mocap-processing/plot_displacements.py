import csv
from matplotlib import rc
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from collections import defaultdict
from parse_utilities import *

# this "order" mapping is used to record the actual order of points along snake marker moving in one direction
# so  marker 2 is left most, then 5, 1, ... 
# this should be fixed in future data during mocap configuration so that  marker indexes are ordered in a reasonable way (ex: left to right on snake marker)
orders = [[4, 5, 3, 2, 1, 6], [2, 5, 4, 1, 3, 6], [6, 1, 2, 4, 5, 3], [5, 4, 3, 2, 1, 6], [2, 6, 5, 1, 3, 4]]
skip_frames = 10 # set this to control how many frames we sample for calculations/plots
xidx, yidx = 0, 2 # (set plot yaxis to mocap zaxis) this mapping is determined based on mocap calibration - check whether y or z is second axis in ground plane
xview = (-0.2, 0.2) # set this based on actual range of coordinates in mocap collection
yview = (0, 0.4) # set this based on actual range of coordinates in mocap collection
dirnames = ['1_api2_bpi2_dc28_tilt_pi4_2017-02-08', '2_api2_bpi4_dc28_tilt_pi4_2017-02-08', '5_api2_bpi8_dc28_tilt_pi4_2017-02-08', '3_api2_bpi4_dc28_tilt_3pi4_2017-02-08', '4_api2_bpi8_dc28_tilt_3pi4_2017-02-08']
legend = ['$a:b=1$', '$a:b=2, \phi=\pi/4$', '$a:b=4, \phi=\pi/4$', '$a:b=4, \phi=3\pi/4$', '$a:b=4, \phi=3\pi/4$']

font = {'family' : 'normal',
        'size'   : 18}

rc('font', **font)

if __name__ == "__main__":
	time = defaultdict(list)
	
	# data structures to save shape variable properties for each frame
	bodyref = defaultdict(list)
	
	fig, ax = plt.subplots()
	box = ax.get_position()
	ax.set_position([box.x0, box.y0+box.height*0.5, box.width, box.height*0.5])
	
	for (i, name) in enumerate(dirnames):
		# read csv file and save a list of coordinates over time for each marker
		markers = defaultdict(list)
		order = orders[i]
		# markers structure stores all coordinates for all  markers
		# format: markers[marker index][frame index] = (x, y, z)
		# marker index may not correspond to points in order across snake marker - we should fix this in future data
		
		with open(name + '/data.csv') as csvfile:
			reader = csv.DictReader(csvfile)
			for (i, row) in enumerate(reader):
				if i % skip_frames == 0:
					# subtract time/frame columns and then divide by three (x, y, z) to get total number of  markers
					num_markers = (len(row) - 2) / 3
					try:
						time[name].append(float(row['Time']))
						for i in range(1, num_markers + 1):
							key = 'Marker ' + str(i)
							x = float(row[key + ' X'])
							y = float(row[key + ' Y'])
							z = float(row[key + ' Z'])
							markers[i].append((x, y, z))
						
						# find center point of line between actuator end points
						x1, y1, z1 = markers[order[2]][-1]
						x2, y2, z2 = markers[order[3]][-1]
						x3, y3, z3 = (x1+x2)/2, (y1+y2)/2, (z1+z2)/2
						bodyref[name].append((x3, y3, z3))
						
					except ValueError:
						print "Unable to parse number from some row."
						time[name].pop()
						
						continue
	
		x1, y1, z1 = markers[order[2]][0]
		x2, y2, z2 = markers[order[3]][0]
		frameangle = np.arctan((z2-z1)/(x2-x1))
		x0, y0, z0 = bodyref[name][0]

		xpos = [-1*((x-x0)*np.cos(frameangle) + (z-z0)*np.sin(frameangle))*100 for (x, y, z) in bodyref[name]]
		zpos = [((z-z0)*np.cos(frameangle) + (x-x0)*np.sin(frameangle))*100 for (x, y, z) in bodyref[name]]
		ax.plot(time[name], xpos)
		#plt.plot(time[name], zpos)
		
	plt.title("Displacement")
	plt.xlabel("Time (s)")
	plt.ylabel("Distance (cm)")
	plt.ylim((-2, 15))
	fig.set_size_inches(10, 10)
	ax.legend(legend, loc='lower center', bbox_to_anchor=(0.5, -1))
	plt.savefig('alldisplacements.png')
	plt.show()
	