import csv
from matplotlib import rc
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from collections import defaultdict
from parse_utilities import *

#orders = [[4, 5, 3, 2, 1, 6], [2, 5, 4, 1, 3, 6], [6, 1, 2, 4, 5, 3], [5, 4, 3, 2, 1, 6], [2, 6, 5, 1, 3, 4]]
skip_frames = 10 # set this to control how many frames we sample for calculations/plots
xidx, yidx = 0, 2 # (set plot yaxis to mocap zaxis) this mapping is determined based on mocap calibration - check whether y or z is second axis in ground plane
xview = (-0.2, 0.2) # set this based on actual range of coordinates in mocap collection
yview = (0, 0.4) # set this based on actual range of coordinates in mocap collection




#dirnames = ['circular_extensible_tsample_0pt2s_cleaned.csv', 'circular_extensible_tsample_0pt5s_cleaned.csv', 'circular_inextensible_tsample_0pt2s_cleaned.csv', 'circular_inextensible_tsample_0pt5s_cleaned.csv', 'circular_inextensible_tsample_0pt2s_paper_cleaned.csv', 'circular_inextensible_tsample_0pt5s_paper_cleaned.csv', 'circular_extensible_tsample_0pt5s_paper_cleaned.csv']
#legend = ['extensible 0.2', 'extensible 0.5', 'inextensible 0.2', 'inextensible 0.5', 'inextensible paper 0.2', 'inextensible paper 0.5', 'extensible paper 0.5']

dirnames = ['circular_extensible_tsample_0pt5s_dutycycle35_cleaned.csv', 'circular_inextensible_tsample_0pt5s_dutycycle35_cleaned.csv', 'circular_extensible_tsample_0pt5s_dutycycle35_paper_cleaned.csv', 'circular_inextensible_tsample_0pt5s_dutycycle35_paper_cleaned.csv']
legend = ['extensible 35 millet', 'inextensible 35 millet', 'extensible 35 paper', 'inextensible 35 paper']

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
		#order = orders[i]
		# markers structure stores all coordinates for all  markers
		# format: markers[marker index][frame index] = (x, y, z)
		# marker index may not correspond to points in order across snake marker - we should fix this in future data
		
		with open(name) as csvfile:
			reader = csv.DictReader(csvfile)
			for (i, row) in enumerate(reader):
				if i > 100:
					if i % skip_frames == 0:
						# subtract time/frame columns and then divide by three (x, y, z) to get total number of  markers
						num_markers = int((len(row) - 2) / 3)
						try:
							time[name].append(float(row['Time']))
							for i in range(1, num_markers + 1):
								key = 'Marker ' + str(i)
								x = float(row[key + ' X'])
								y = float(row[key + ' Y'])
								z = float(row[key + ' Z'])

								markers[i].append((x, y, z))


							# find center point of line between actuator end points
							x1, y1, z1 = markers[2][-1]
							x2, y2, z2 = markers[3][-1]
							x3, y3, z3 = (x1+x2)/2, (y1+y2)/2, (z1+z2)/2
							bodyref[name].append((x3, y3, z3))

						except ValueError:
							print ("Unable to parse number from some row.")
							time[name].pop()

							continue
	
		x1, y1, z1 = markers[3][0]
		x2, y2, z2 = markers[4][0]

		frameangle = np.arctan((z2-z1)/(x2-x1))
		x0, y0, z0 = bodyref[name][0]

		xpos = [abs((x-x0)*np.cos(frameangle) + (z-z0)*np.sin(frameangle))*100 for (x, y, z) in bodyref[name]]
		zpos = [abs((z-z0)*np.cos(frameangle) + (x-x0)*np.sin(frameangle))*100 for (x, y, z) in bodyref[name]]
		ax.plot(time[name], xpos)
		#plt.plot(time[name], zpos)

		fourier = np.fft.fft(xpos)
		n = np.asarray(xpos).size
		timestep = 0.008333
		freq = np.fft.fftfreq(n, d=timestep)
		fig, ax = plt.subplots()
		plt.plot(freq, fourier.real)
		ax.set_xlim(-10, 10)
		print(freq)
		#print(fourier.real)
		plt.title(name)

	plt.show()
"""
	plt.title("Displacement")
	plt.xlabel("Time (s)")
	plt.yticks(np.arange(0, 40, 5))
	plt.ylabel("Distance (cm)")
	#plt.ylim((-2, 15))
	#fig.set_size_inches(10, 10)
	ax.legend(legend, loc='lower center', bbox_to_anchor=(0.5, -1.25))
	plt.savefig('alldisplacements.png')
	plt.show()
"""