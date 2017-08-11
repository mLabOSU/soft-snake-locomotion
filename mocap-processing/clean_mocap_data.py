#PYTHON 3

import csv
import matplotlib.pyplot as plt
import numpy as np


directoryName = 'optitrack_circular_gait_extensible_inextensible_8_4_17'
fileName = '\circular_inextensible_tsample_0pt5s_dutycycle35_paper' #DONT include .csv in filenamve
newName = directoryName + fileName + "_cleaned.csv"
spineDimension = 'Z' #dimension that spine of snake is aligned on (can be 'X', 'Y', or 'Z')
dimensions = {'X':0, 'Y':1, 'Z':2}
marker_num = 6
print("cleaned", fileName)
#opens file that will be cleaned
with open (directoryName + fileName + ".csv") as csvfile:
    reader = csv.reader(csvfile)
    #creates new file for cleaned data
    with open (newName, 'w+') as cleanedcsvfile: #w+ means the file will be created if it does not exist, otherwise existing file will be cleared
        writer = csv.writer(cleanedcsvfile, lineterminator = '\n') #python was inserting extra lines between rows
        #skips first 6 lines of csv file
        for i in range(7):
            row = next(reader)

        #creates the first row of headers in the correct format (['Time', 'Frame', 'Marker 1 X', 'Marker 1 Y'...])
        firstRow = ['Frame', 'Time']
        firstData = next(reader)
        #sometimes mocap puts more xyz headers in than there are columns of data so we use length of first row of data instead of length of header
        while '' in firstData:
            firstData.remove('')

        for i in range(2, len(firstData)): #use firstData for length because we don't want extra xyz headers
            header = 'Marker ' + str(int(((i-2) / 3) + 1)) + ' ' + row[i]
            firstRow.append(header)

        #writes first row, first row of data, then all the rows in the file
        writer.writerow(firstRow)
        writer.writerow(firstData)

        for (i, row) in enumerate(reader):
            #creates a list of lists where inner list is x, y, z points, outer list is list of points
            point_list = []
            frame = row[0]
            time = row[1]

            #removes any blank datapoints from the row
            row = row[0:(3*marker_num)+2]

            if not('' in row):
                for j in range(2, len(row), 3):


                    XYZlist = [row[j], row[j+1], row[j+2]]
                    point_list.append(XYZlist)
                #sort the list of points based on spineDimension (x, y, or z). Makes sure mocap didn't get marker order wrong
                sorted_point_list = sorted(point_list, key= lambda point:point[dimensions[spineDimension]])
                #adds the each element of inner lists to [frame, time]
                sorted_row = sum(sorted_point_list, [frame, time])

                writer.writerow(sorted_row)
