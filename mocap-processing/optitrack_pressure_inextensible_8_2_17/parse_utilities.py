import numpy as np


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
    R = a * b * c / 4 / np.sqrt(s * (s - a) * (s - b) * (s - c))
    b1 = a * a * (b * b + c * c - a * a)
    b2 = b * b * (a * a + c * c - b * b)
    b3 = c * c * (a * a + b * b - c * c)
    P = np.column_stack((A, B, C)).dot(np.hstack((b1, b2, b3)))
    P /= b1 + b2 + b3
    return R, P


# get cross product of "vectors" between center point of actuator and both ends (in horizontal plane)
# use direction (into/outof horizontal plane) of this vector to designate positive/negative curvature
# return 1 or -1 to indicate direction
def curvature_dir(p1, p2, p3, xidx, yidx):
    A = np.array([p1[xidx], p1[yidx]])
    B = np.array([p2[xidx], p2[yidx]])
    C = np.array([p3[xidx], p3[yidx]])
    nv = np.cross((B - A), (B - C))
    if nv != 0:
        return nv / abs(nv)
    else:
        return 0


def find_angle(radius, p1, p2):
    A = np.array(list(p1))
    B = np.array(list(p2))
    c = np.linalg.norm(B - A)
    cos_angle = 1 - ((c ** 2) / (2 * radius ** 2))
    return np.arccos(cos_angle)
