from Geometry3D import *
import numpy as np
import math

class wVector(Vector):
    def __init__(self, *args):
        super().__init__(*args)

    def rotateMatrix(self, angle):
        """Return the rotation matrix around the vector by angle"""
        """angle in degree"""
        """Math see: https://en.wikipedia.org/wiki/Rotation_matrix#Rotation_matrix_from_axis_and_angle"""
        naxis = self.normalized() # normalized
        x = naxis._v[0]
        y = naxis._v[1]
        z = naxis._v[2]
        angle = math.radians(angle)
        cosv = math.cos(angle)
        mcosv = 1 - cosv
        sinv = math.sin(angle)

        rm = np.ones((3,3))
        rm[0,0] = cosv + math.pow(x,2) * mcosv
        rm[0,1] = x * y * mcosv - z * sinv
        rm[0,2] = x * z * mcosv + y * sinv
        rm[1,0] = x * y * mcosv + z * sinv
        rm[1,1] = cosv + math.pow(y,2) * mcosv
        rm[1,2] = y * z * mcosv - x * sinv
        rm[2,0] = x * z * mcosv - y * sinv
        rm[2,1] = y * z * mcosv + x * sinv
        rm[2,2] = cosv + math.pow(z,2) * mcosv

        return rm

    def rotateByAxis(self, axis, angle):
        """Returns the vector after rotating around axis counter-clockwise by angle"""
        """The axis must be a vector"""
        """Angle in degree"""
        if isinstance(axis, Vector):
            rm = axis.rotateMatrix(angle)
            return self.rotateByMatrix(rm)

        else:
            print("Error, the axis must be a vector!")
            return 0

    def rotateByMatrix(self, rm):
        """ calculate the rotated vector after the rotation matrix rm"""
        _vec = np.matrix([self._v[0], self._v[1], self._v[2]]).T
        rot = rm * _vec
        return wVector(Vector(rot[0,0], rot[1,0], rot[2,0]).normalized())

    def projectOnPlane(self, nvec):
        """Calculate the projection of the vector on the plane"""
        """ Note: nvec must be the normal Vector of your plane, not the Plane """
        if isinstance(nvec, Vector):
            nvec = nvec.normalized()
            ratio = get_relative_projection_length(self, nvec)
#            if ratio <= math.sin( math.radians(0.375) ): # the vector is in the plane
            if ratio <= get_eps(): # the vector is in the plane
                return self
            normalized = wVector( self._v[0]/ratio, self._v[1]/ratio, self._v[2]/ratio )
            return wVector((normalized-nvec).normalized())

        else:
            print("Error, the input must be the normal vector of the plane!!")
            return 0

    def angle(self, other):
        """Override the parent's angle function"""
        v = self * other / (self.length() * other.length() )
        v = round(v, get_sig_figures())
        return math.acos( v )

if __name__ == '__main__':
    v1 = wVector(1,0,0)
    v2 = z_unit_vector()
#    print(v1.rotateByAxis(v2, 90))
    print( wVector(1,-3,1).projectOnPlane(Vector(0,0,1)) )
    v1 = wVector(-0.013648865632917572, -0.9999068498949963, 0.0)
    v2 = wVector(0.013648865632929403, 0.9999068498949961, 0.0)
    print(v1*v2/(v1.length()*v2.length()))
    print(v1.angle(v2))
