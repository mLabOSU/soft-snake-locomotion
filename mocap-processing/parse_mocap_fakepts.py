import csv
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from collections import defaultdict

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

order = [2, 5, 1, 4, 6, 3]
skip_frames = 5
xidx, yidx, zidx = 0, 1, 2

if __name__ == "__main__":
	time = []
	bodies = defaultdict(list)
	
	# read csv file and save a list of coordinates over time for each rigid body
	with open('optitrack_sample.csv') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
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
			except ValueError:
				print "Unable to parse number from some row."
				continue
	
	# add a fake point at the midpoint of each leg by doing some silly average math
	# (we need a third point to get circles)
	for i in range(len(bodies[1])):
		x1, y1, z1 = bodies[order[0]][i]
		x2, y2, z2 = bodies[order[2]][i]
		bodies[5].append((x2+((x2-x1)*0.1), (y1+y2)/2, (z1+z2)/2))
		
		x1, y1, z1 = bodies[order[3]][i]
		x2, y2, z2 = bodies[order[5]][i]
		bodies[6].append((x2+((x2-x1)*0.2), (y1+y2)/2, (z1+z2)/2))
	
	# add initial points to lists for first plot
	xlist = [bodies[j][0][xidx] for j in order]
	zlist = [bodies[j][0][zidx] for j in order]
	
	fig, ax = plt.subplots()
	plt.ylim((0, 0.3))
	plt.xlim((-0.15, 0.15))
	
	# initialize snake and curves to be updated
	line, = ax.plot(xlist, zlist)
	plt.setp(line, linewidth=3)
	circ1 = plt.Circle((0, 0), radius=1, color='g', fill=False)
	ax.add_patch(circ1)
	circ2 = plt.Circle((0, 0), radius=1, color='r', fill=False)
	ax.add_patch(circ2)
	text = ax.text(-0.1, 0.02, '')
	
	# update all rigid body points, both circles, and curvature label text
	def animate(i):
		xlist = [bodies[j][i*skip_frames][xidx] for j in order]
		zlist = [bodies[j][i*skip_frames][zidx] for j in order]
		line.set_xdata(xlist)
		line.set_ydata(zlist)

		p1 = bodies[order[0]][i*skip_frames]
		p2 = bodies[order[1]][i*skip_frames]
		p3 = bodies[order[2]][i*skip_frames]
		radius1, center1 = find_circle(p1, p2, p3)
		circ1.center = (center1[0], center1[2])
		circ1.radius = radius1
		
		p1 = bodies[order[3]][i*skip_frames]
		p2 = bodies[order[4]][i*skip_frames]
		p3 = bodies[order[5]][i*skip_frames]
		radius2, center2 = find_circle(p1, p2, p3)
		circ2.center = (center2[xidx], center2[zidx])
		circ2.radius = radius2
		
		text.set_text('k1=' + str(1/radius1) + ', k2=' + str(1/radius2))
		return line, circ1, circ2, text

	ani = animation.FuncAnimation(fig, animate, frames=len(bodies[1])/skip_frames, interval=2, blit=False)
	
	# uncomment this to save the animation to a video file
	#Writer = animation.writers['ffmpeg']
	#writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)	
	#ani.save('curvatures.mp4', writer=writer)
	
	plt.show()