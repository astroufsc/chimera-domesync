# Copyright (c) 2010-2012 John Kielkopf, Jeff Hay and Karen Collins
# kielkopf@louisville.edu
#
#
# Date: April 19, 2012
# Version: 1.1
#
# This file is part of PyDome
#
# PyDome is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyDome is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# Iteratively solve for the azimuth of the dome given the telescope RA and Dec
from math import pi, sin, cos, sqrt, atan2

from chimera.core.site import Site
from chimera.util.coord import CoordUtil, Coord
from chimera.util.position import Position


class AzimuthModel(object):
    def __init__(self, site_latitude, dome_radius, mount_dec_height, mount_dec_length, mount_dec_offset):
        self.site_latitude = site_latitude
        self.dome_radius = dome_radius
        self.mount_dec_height = mount_dec_height
        self.mount_dec_length = mount_dec_length
        self.mount_dec_offset = mount_dec_offset

    def solve_dome_azimuth(self, telescope_pos, lst, nloops=10):

        # Find the altitude and azimuth of the current pointing
        # This should be valid in either hemisphere
        pos = Position.raDecToAltAz(telescope_pos, self.site_latitude, lst)
        telaz, telalt, ha = pos.az.R, pos.alt.R, CoordUtil.raToHa(telescope_pos.ra, lst).R

        # Find the reference point on the optical axis in dome coordinates
        # z: vertical
        # y: north - south
        # x: east - west
        # theta: altitude of the polar axis from the horizontal plane
        # phi: rotation of dec axis about polar axis

        # Meaning of x and y compared to sky depends on the hemisphere!
        # z: always + up
        # y: always + toward N for +lat or S for -lat
        # x: maintains right-handed coordinate system with z and y
        #  thus x is + to E for +lat and to W for -lat
        # theta: always positive from the horizontal plane to the pole
        # phi: rotation about polar axis
        #  and is +90 for a horizontal axis with OTA toward +x
        #  and is   0 for OTA over mount with dec axis counterweight down
        #  and is -90 for a horizontal axis with OTA toward -x


        # We have a German equatorial and the origin changes with ha
        # Assign phi based on an assumption about the basis derived from the ha
        phi = ha

        # Assign theta
        theta = abs(self.site_latitude.R)

        # Find the dome coordinates of the OTA reference point for a German equatorial
        # This works in either hemisphere
        x0 = self.mount_dec_length * sin(phi)
        y0 = -self.mount_dec_length * cos(phi) * sin(theta) + self.mount_dec_offset
        z0 = self.mount_dec_length * cos(phi) * cos(theta) + self.mount_dec_height

        # (x,y,z) is on the optical axis
        # Iterate to make this point also lie on the dome surface
        # Begin iteration assuming the zero point is at the center of the dome
        # Telescope azimuth is measured from the direction to the pole

        d = 0.
        r = self.dome_radius

        if self.site_latitude.R <= 0.:
            telaz2 = telaz - pi
            # between (0, 2pi):
            if telaz2 > 2 * pi:
                telaz2 -= 2 * pi
            elif telaz2 < 0:
                telaz2 += 2 * pi

            telalt2 = telalt

        # Iterate for convergence

        n = 0
        while n < nloops:
            d -= r - self.dome_radius
            rp = self.dome_radius + d
            x = x0 + rp * cos(telalt2) * sin(telaz2)
            y = y0 + rp * cos(telalt2) * cos(telaz2)
            z = z0 + rp * sin(telalt2)
            r = sqrt(x * x + y * y + z * z)

            # Repeat the calculation correcting the assumed OTA path length each time
            # This converges quickly  so just do a few loops and assume it is ok

            # print "n, r, rp: ", n, r, rp

            n += 1

        # Use (x,y,0) from the interation to find the azimuth of the dome
        # Azimuth is N (0), E (90), S (180), W (270) in both hemispheres
        # However x and y are different in the hemispheres so we fix that here

        zeta = atan2(x, y)
        if (zeta > - 2. * pi) and (zeta < 2. * pi):
            if self.site_latitude.R <= 0.:
                zeta += pi
        else:
            zeta = telaz

        if zeta < 0:
            zeta = zeta + 2 * pi
        elif zeta > 2 * pi:
            zeta - 2 * pi

        return zeta * 180 / pi


if __name__ == '__main__':
    import numpy as np

    dome_radius, mount_dec_height, mount_dec_length, mount_dec_offset = 147, 0, 49.2, 0
    site = Site()
    Model = AzimuthModel(site['latitude'], dome_radius, mount_dec_height, mount_dec_length, mount_dec_offset)
    # for dra in np.arange(10, 200, 36):
    #     for ddec in np.arange(1, 360, 10):
    for az, alt in [(ii, jj) for ii in np.arange(5, 360, 10) for jj in np.arange(25, 90, 20)]:
        tel_pos = Position.altAzToRaDec(Position.fromAltAz(Coord.fromD(alt), Coord.fromD(az)), site['latitude'], site.LST())
        model = Model.solve_dome_azimuth(tel_pos, site.LST_inRads())
        print 'here', alt, az, model, model - az
