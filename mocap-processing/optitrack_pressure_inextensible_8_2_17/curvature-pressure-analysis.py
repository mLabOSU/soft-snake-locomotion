import csv
from matplotlib import rc
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from collections import defaultdict
from parse_utilities import *

skip_frames = 10  # set this to control how many frames we sample for calculations/plots
xidx, yidx = 0, 2  # (set plot yaxis to mocap zaxis) this mapping is determined based on mocap calibration - check whether y or z is second axis in ground plane
xview = (-0.2, 0.2)  # set this based on actual range of coordinates in mocap collection
yview = (0, 0.4)  # set this based on actual range of coordinates in mocap collection
dirname = 'Users\jrs\Documents\OSUREU\Mocap Data Analysis\08-01-17 data'
pmin = 1.0
pmax = 3.0
pdelta = 0.5
prefixes = ['E1L', 'E1R', 'E2L', 'E2R', 'I1L', 'I1R', 'I2L', 'I2R']
#colors = ['g', 'r', 'k', 'y']
labels = ['Actuator 1 +', 'Actuator 1 -', 'Actuator 2 +', 'Actuator 2 -']

kpa_per_psi = 6.89476

font = {'size': 18}

rc('font', **font)

if __name__ == "__main__":
    time = []
    markers = defaultdict(list)
    # markers structure stores all coordinates for all  markers
    # format: markers[marker index][frame index] = (x, y, z)
    # marker index may not correspond to points in order across snake marker - we should fix this in future data

    pressure, curvature, angle, length = defaultdict(list), defaultdict(list), defaultdict(list), defaultdict(list)

    for s in prefixes:
        for p in range(int(10*pmin), int(10*(pmax + pdelta)), int(10*pdelta)):
            # data structures to save shape variable properties for each frame
            ktemp, atemp, ltemp = [], [], []
            p = float(p)/10

            # read csv file and save a list of coordinates over time for each marker
            with open(s + '_' + str(p) + '_psi.csv') as csvfile:
                #SKIP the first un-needed lines in RAW mocap data
                for i in range(8):
                    line = csvfile.readline() #readline for python 3, next for python 2.7

                reader = csv.reader(csvfile)

                for (i, row) in enumerate(reader):

                    if i % skip_frames == 0:
                        # subtract time/frame columns and then divide by three (x, y, z) to get total number of  markers
                        num_markers = int((len(row) - 2) / 3)

                        try:
                            time.append(float(row[1])) #Row 1 is time row
                            """
                            for j in range(1, num_markers + 1):
                                key = 'Marker ' + str(j)
                                x = float(row[key + ' X'])
                                y = float(row[key + ' Y'])
                                z = float(row[key + ' Z'])
                                markers[j].append((x, y, z))
                            """
                            # this is really a hack!
                            # use the knowledge that actuator points are aligning along z to order them correctly
                            points = []
                            for j in range(2, len(row), 3): #2 is first position row
                                x1 = float(row[j])
                                y1 = float(row[j + 1])
                                z1 = float(row[j + 2])

                                points.append((z1, (x1, y1, z1)))
                            points.sort()

                            # compute shape variable in this frame

                            radius, center = find_circle(points[0][1], points[1][1], points[2][1])
                            direction = curvature_dir(points[0][1], points[1][1], points[2][1], xidx, yidx)
                            ktemp.append(direction / radius)
                            atemp.append(direction * find_angle(radius, points[0][1], points[2][1]))
                            ltemp.append(abs(radius * atemp[-1]))


                        except ValueError:
                            print
                            "Unable to parse number from some row."
                            time.pop()
                            continue

            pressure[s].append(kpa_per_psi * float(p) / 100.0)
            curvature[s].append(abs(sum(ktemp)) / len(ktemp))
            angle[s].append(abs(sum(atemp)) / len(atemp))
            length[s].append(abs(sum(ltemp)) / len(ltemp))

    plt.title(r"Pressure-Angle Curve ($\alpha$)")
    for (i, s) in enumerate(prefixes):
        plt.plot(pressure[s], angle[s], marker='o')
    plt.xlabel("Pressure (kPa)")
    plt.ylabel("Angle (rad)")
    plt.legend(prefixes, loc='upper left')
    #plt.savefig(prefixex[i] + ''a_vs_p.png')

    fig, ax = plt.subplots()
    plt.title(r"Pressure-Curvature Curve ($\kappa$)")
    for (i, s) in enumerate(prefixes):
        plt.plot(pressure[s], curvature[s], marker='o')
    plt.xlabel("Pressure (kPa)")
    plt.ylabel("Curvature (1/m)")
    plt.legend(prefixes, loc='upper left')
    #plt.savefig(dirname + '/k_vs_p.png')

    fig, ax = plt.subplots()
    plt.title("Pressure-Length Curve (L)")
    for (i, s) in enumerate(prefixes):
        plt.plot(pressure[s], length[s], marker='o')
    plt.xlabel("Pressure (kPa)")
    plt.ylabel("Actuator Length (m)")
    plt.legend(prefixes, loc='upper left')
    #plt.savefig(dirname + '/l_vs_p.png')

plt.show()
