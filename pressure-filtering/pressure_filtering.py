import csv
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

num_sensors = 4
dt_ms = 200
window = 7

if __name__ == "__main__":
	pressures, filtered = defaultdict(list), defaultdict(list)
	times = []
	
	# read csv file and save a list of coordinates over time for each rigid body
	with open('pressure_outputs.csv') as csvfile:
		reader = csv.DictReader(csvfile)
		t0 = 0.0
		for row in reader:
			try:
				times.append(t0 / 1000)
				t0 += dt_ms
				for i in range(1, num_sensors+1):
					key = 'Pressure Sensor ' + str(i)
					p = float(row[key])
					pressures[i].append(p)
					
			except ValueError:
				print "Unable to parse number from some row."
				continue
	
	for i in range(1, num_sensors+1):
		for j in range(len(pressures[i])):
			idx0 = max(0, j-window)
			idx1 = min(len(pressures[i])-1, j+window)
			f = np.median(pressures[i][idx0:idx1])
			filtered[i].append(f)
			
		plt.plot(times, pressures[i])
		plt.xlabel("Time (s)")
		plt.ylabel("Pressure (psi)")
		plt.title("Pressure Sensor " + str(i))
		plt.show()
		plt.plot(times, filtered[i])
		plt.xlabel("Time (s)")
		plt.ylabel("Pressure (psi)")
		plt.title("Pressure Sensor " + str(i))
		plt.show()
	