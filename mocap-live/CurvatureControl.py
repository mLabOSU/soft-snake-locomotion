from parse_utilities import *

min_pwm = 10
max_pwm = 30
xidx, yidx = 0, 2 # (set plot yaxis to mocap zaxis)
scale_p = 0.3

class CurvatureControl:
	def __init__(self):
		self.markers = []
		self.k = 0
		self.klast = 0
		self.center = (0, 0, 0)
		self.angle = 0
		self.length = 0
		self.pwm = 0
		self.valve = 0
		
	def setMarkers(self, markers):
		assert len(markers) == 3, "Expected 3 marker points."
		self.markers = markers
		
	def calculateGeometry(self):
		self.klast = self.k
		radius, self.center = find_circle(self.markers[0], self.markers[1], self.markers[2])
		direction = curvature_dir(self.markers[0], self.markers[1], self.markers[2], xidx, yidx)
		self.k = direction / radius
		self.angle = direction * find_angle(radius, self.markers[0], self.markers[2])
		self.length = abs(radius * self.angle)
		
	def adjustPWM(self, ktarget):
		error = ktarget - self.k
		self.pwm = self.pwm + scale_p * error
		if self.pwm > max_pwm:
			self.pwm = max_pwm
		return self.pwm
		
	def update(self, markers, ktarget):
		self.setMarkers(markers)
		self.calculateGeometry()
		
		if (self.k - self.klast) * self.k > 0 and self.k * ktarget < 0:
			self.valve = 1 - self.valve

		newPWM = self.adjustPWM(ktarget)	
		#print ("k = ", self.k, "pwm = ", newPWM) 
		return self.k, self.valve, newPWM, 1 - self.valve, 0
	