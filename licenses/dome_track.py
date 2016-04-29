#!/usr/bin/python

# * dome_track 
#
#   * Look up the right ascension and declination of the telescope field
#   * Calculate the optimal azimuth of the dome shutter
#   * Look up the current azimuth of the dome shutter
#   * Drive the dome to the optimal azimuth

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



# Define values appropriate for this dome


# Switch settings for the DLI device

SWITCHIP="192.168.0.100"
USER=""
PASSWORD=""

# Rotation rate in degrees per second

dps = 2.5

# Azimuth tolerance for setting should be greater than tag increment

tolazimuth = 5.

# Lower limit of azimuth allowed

minazimuth = 0.

# Upper limit of azimuth allowed

maxazimuth = 270.


# Longitude is + west of prime meridian 

# Longitude and latitude for Moore Observatory       
# site_longitude = 85.5288888888
# site_latitude = 38.3334

# Longitude and latitude for Mt. Kent Observatory    
# site_longitude = -151.855528  
# site.latitude = -27.797778

site_longitude = 85.5288888888
site_latitude = 38.3334


# Radius of dome

# CDK20N and CDK20S 
# dome_radius = 1.75

# RC24
# dome_radius = 2.83

dome_radius = 1.75
  

# Offset to dec axis from center of dome

# CDK20N  
# mount_dec_offset = 0.24

# CDK20S 
# mount_dec_offset = 0.24

# RC24
# mount_dec_offset =0.66

mount_dec_offset = 0.20
  

# Height of intersection of declination and polar axes above dome equator

# CDK20N  
# mount_dec_height = 0.0

# CDK20S 
# mount_dec_height = 0.0

# RC24
# mount_dec_height = -0.25
 
mount_dec_height = 0.0
  

# Length from polar to optical axes
# CDK20N  
# mount_dec_length = 0.6

# CDK20S 
# mount_dec_length = 0.6

# RC24
# mount_dec_length = 0.
  
mount_dec_length = 0.65


# Mount type  altaz = 0,  fork = 1, german equatorial = 2

telmount = 2


################################################################################
################################################################################

import sys
import argparse
import time
from datetime import datetime
from math import sin, cos, asin, acos, atan2, sqrt, pi

# The dli module needs to be in the python path.  
# Add current directory to the path so we can find the dli module

sys.path.append('.')
import dli


parser= argparse.ArgumentParser(description='Track telescope with dome azimuth')

if len(sys.argv) > 1:    
  sys.exit("Usage: dome_track")
  exit()   


# Map a time in hours to the range  0  to 24 

def map24(hour):
  
  if (hour < 0.0): 
    n = int(hour / 24.0) - 1
    hour24 = hour - n * 24.0
    return (hour24)
   
  elif (hour >= 24.0):   
    n = int(hour / 24.0)
    hour24= hour - n * 24.0
    return (hour24)
   
  else: 
    hour24 = hour
    return (hour24)


#Map an hourangle in hours to  -12 <= ha < +12 

def map12(hour):
  
  hour12=map24(hour)
  
  if (hour12 >= 12.0): 
    hour12 = hour12 - 24.
    return (hour12)
   
  else:   
    return (hour12)
  

    

# Map an angle in degrees to  0 <= angle < 360 

def map360(angle):

  if (angle < 0.0):   
    n = int(angle / 360.0) - 1
    return (angle - float(n) * 360.0)
   
  elif (angle >= 360.0):  
    n = int(angle / 360.0)
    return (angle - float(n) * 360.0)
   
  else:   
    return (angle)
  

# Map an angle in degrees to  -180 <= angle < 180 

def map180(angle):

  angle360 = map360(angle)
   
  if (angle360 >= 180.0):  
    return (angle360 - 360.0)
   
  else:   
    return (angle360)

    
# Find the fractional part handling negative values properly

def frac(x):

  newx = x - int(x)
  if (newx < 0.):
    newx = newx + 1.
      
  return (newx)


# Calculate the current universal time in hours with millisecond resolution

def utnow():
  
  dt = datetime.utcnow()
  
  hours = dt.hour
  minutes = dt.minute
  seconds = dt.second
  microseconds = dt.microsecond
  ut = hours + minutes/60. + seconds/3600. + microseconds/3600000000.
  
  return (ut)
    

# Calculate the Julian day number for a given year, month, day, and universal time

def calcjd(year,month,day,ut):
  
  day = day + ut / 24.0
  
  
  if int(month)== 1 or int(month)== 2:
    year = year - 1.
    month = month + 12.
  
  if (year + month/12.0 + day/365.25) >= (1582.0 + 10.0 / 12.0 + 15.0 / 365.25):
    na = int(year/100.)
    a = float(na)
    b = 2.0 - a + int(a/4.0)
  else:
    b = 0.
    
  if year < 0.:
    nc = int(float(int(365.25 * year)) - 0.75)
    c = float(nc)
  else:
    nc = int(365.25 * year)          
    c = float(nc)
  
  nd = int(30.6001 * (month + 1.)) 
  d = float(nd)
  jd = b + c + d + day + 1720994.5
  
  return (jd)


# Calculate the Julian day number at this moment

def jdnow():
  dt = datetime.utcnow()
  
  year = dt.year
  month = dt.month
  day = dt.day
  hours = dt.hour
  minutes = dt.minute
  seconds = dt.second
  microseconds = dt.microsecond
  ut = hours + minutes/60. + seconds/3600. + microseconds/3600000000.
  jd = calcjd(year, month, day, ut)
  
  return (jd)

# Calculate the sidereal time for a year, month, day and universal time at the define site latitude  
  
def calclst(year, month, day, ut, glong):
  jdeod =  calcjd(year, month, day, 0.0)
  tu = (jdeod - 2451545.0) / 36525.0
  t0 = (24110.54841 / 3600.0) + (8640184.812866 / 3600.0) * tu + (0.093104 / 3600.0) * tu * tu - (6.2e-6 / 3600.0) * tu * tu * tu
  t0 = map24(t0)
  gmst = map24(t0 + ut * 1.002737909)
  lmst = 24.0 * frac( (gmst - (glong / 15.0) ) / 24.0)
  
  return (lmst)
  

# Calculate the sidereal time at this moment for the defined site latitude

def lstnow():
  
  dt = datetime.utcnow()
  
  year = dt.year
  month = dt.month
  day = dt.day
  hours = dt.hour
  minutes = dt.minute
  seconds = dt.second
  microseconds = dt.microsecond
  ut = hours + minutes/60. + seconds/3600. + microseconds/3600000000.
  glong = site_longitude
  lst = calclst(year,month,day,ut,glong)
  
  return (lst)


# Convert local ha and dec to local az and alt  
# Geographic azimuth convention is followed: 
#   Due north is zero and azimuth increases from north to east 

def equatorial_to_horizontal(ha, dec):

  ha = ha*pi/12.
  phi = site_latitude*pi/180.
  dec = dec*pi/180.
  altitude = asin(sin(phi)*sin(dec)+cos(phi)*cos(dec)*cos(ha))
  altitude = altitude*180.0/pi
  azimuth = atan2(-cos(dec)*sin(ha),
    sin(dec)*cos(phi)-sin(phi)*cos(dec)*cos(ha))
  azimuth = azimuth*180.0/pi
  azimuth = map360(azimuth)

  return (azimuth, altitude)


# Iteratively solve for the azimuth of the dome given the telescope RA and Dec

def solve_dome_azimuth(ra, dec, nloops):

  # Initialize the dome and mount parameters

  R = dome_radius
  H = mount_dec_height
  L = mount_dec_length  
  P = mount_dec_offset
  
  # Find the current hour angle for the telescope pointing

  ha = lstnow()   
  ha = ha - ra
  ha = map24(ha)
  ha0 = map12(ha)
  
  # Find the altitude and azimuth of the current pointing 
  # Function requires ha in 0 to 24 basis                 
  # This should be valid in either hemisphere             
 
  telaz, telalt = equatorial_to_horizontal(ha, dec)

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


  # Set default parameters

  if (telmount != 2) :

  # We have an altaz or fork mount and the origin is simple

    x0 = 0.
    y0 = P
    z0 = H
    
  else:
  
  # We have a German equatorial and the origin changes with ha  
  
  # Assign phi based on an assumption about the basis derived from the ha
    
    if (site_latitude >= 0.):
    
      if (ha0 > 0.):
      
      # Looking west with OTA east of pier 
      # HA is between 0 and +12 hours 

        phi = (6. - ha0)*pi/12.
        
      
      else:
        
      # Looking east with OTA west of pier 
      # HA is between -12 and 0 hours 
        
        phi = -(6. + ha0)*pi/12.
        
      
    
    else:
    
      if (ha0 > 0.):
      
        # Looking west with OTA east of pier 
        # HA is between 0 and +12 hours 
        
        phi = -(6. - ha0)*pi/12.
        
      
      else:
        
        # Looking east with OTA west of pier 
        # HA is between -12 and 0 hours 
        
        phi = (6. + ha0)*pi/12.
        
              
    # Assign theta 
        
    if (site_latitude >= 0.):
    
      theta = site_latitude*pi/180.
    
    else:
    
      theta = -1.*site_latitude*pi/180.
    
 
  # Find the dome coordinates of the OTA reference point for a German equatorial 
  # This works in either hemisphere                      
         
  x0 = L*sin(phi)
  y0 = -L*cos(phi)*sin(theta) + P 
  z0 = L*cos(phi)*cos(theta) + H
  
  
  # (x,y,z) is on the optical axis 
  # Iterate to make this point also lie on the dome surface 
  # Begin iteration assuming the zero point is at the center of the dome
  # Telescope azimuth is measured from the direction to the pole  

  d = 0.
  r = R

  if (site_latitude >= 0.):
  
    telaz2 = telaz * pi / 180.    
    telalt2 = telalt * pi / 180.
  
  else:
  
    telaz2 = telaz - 180.
    telaz2 = map360(telaz2) 
    telaz2 = telaz2 * pi / 180.
    telalt2 = telalt * pi / 180.       
  
  
  # Iterate for convergence

  n = 0  
  while (n < nloops):
    d = d - (r - R)      
    rp = R + d
    x = x0 + rp * cos(telalt2) * sin(telaz2)
    y = y0 + rp * cos(telalt2) * cos(telaz2)
    z = z0 + rp * sin(telalt2)
    r = sqrt(x*x + y*y + z*z)
    
  # Repeat the calculation correcting the assumed OTA path length each time 
  # This converges quickly  so just do a few loops and assume it is ok 
    
  # print "n, r, rp: ", n, r, rp
    
    n = n + 1
    
  # Use (x,y,0) from the interation to find the azimuth of the dome 
  # Azimuth is N (0), E (90), S (180), W (270) in both hemispheres 
  # However x and y are different in the hemispheres so we fix that here 
  
  zeta  = atan2(x,y)
  if ( (zeta > - 2.*pi) and (zeta < 2.*pi)):
  
    if ( site_latitude > 0. ):
    
      zeta = (180./pi)*zeta
      zeta = map360(zeta)
    
    else :
    
      zeta = (180./pi)*zeta
      zeta = zeta + 180.
      zeta = map360(zeta)   
      
  
  else:
  
    zeta = telaz
  
  return (zeta)

# Look up the current telescope coordinates

telcoordsstatus = open('/usr/local/observatory/status/telcoords','r')
telcoordsstr = telcoordsstatus.read(40)
telcoordsstatus.close()

# print ("Coordinates: %s " % telcoordsstr)

rastr, decstr = telcoordsstr.split()
ra = float(rastr)
dec = float(decstr)

# Iteratively solve for the optimal dome azimuth

nloops = 5
newazimuth = solve_dome_azimuth(ra, dec, nloops)

print ("New azimuth: " '{0:.2f}'.format(newazimuth))

# Look up the current dome azimuth

nowazimuthstatus = open('/usr/local/observatory/status/domeazimuth','r')
nowazimuthstr = nowazimuthstatus.read(40)
nowazimuthstatus.close()
nowazimuth = float(nowazimuthstr)

print ("Current azimuth: "  '{0:.2f}'.format(nowazimuth))

# Limit motion if needed

#if minazimuth > newazimuth:
#  newazimuth = minazimuth
#  print ("Limiting dome track to minimum azimuth ...")
  
#if maxazimuth < newazimuth:
#  newazimuth = maxazimuth
#  print (" Limiting dome track to maximum azimuth ...")
  

# Calculate the required change in azimuth

# Use this if crossing the zero point is allowed

#delazimuth = map180(newazimuth - nowazimuth)

# Use this if zero crossing is forbidden

delazimuth = newazimuth - nowazimuth

if abs(delazimuth) > tolazimuth:

  # Use the DLI switch to rotate the dome

  # Open (connect) to the power switch, if the
  # parameters are not passed it defaults to the
  # IP address, user and password the switch is 
  # set with from the factory.  Only changed items
  # actually need to be passed.
  switch=dli.powerswitch(hostname=SWITCHIP,userid=USER,password=PASSWORD)

  # Verify the switch
  if not switch.verify():
    print "Cannot talk to the switch"
    sys.exit(1)

  # Print the current state of all the outlets
  # switch.printstatus()
    
  if (delazimuth > 0.):

    # Power increase azimuth on
    switch.on(2)

    #  print 'Increase dome azimuth switch is  ',switch.status(2)

    # Wait the dome to rotate the requested angle
    dps = 2.5
    delay = delazimuth/dps
    time.sleep(delay)

    # Power increase dome azimuth off
    switch.off(2)

    #  print 'Increase dome azimuth switch is  ',switch.status(2)

  elif (delazimuth < 0.):

    # Power decrease azimuth on
    switch.on(1)

    #  print 'Decrease dome azimuth switch is  ',switch.status(1)

    # Wait the dome to rotate the requested angle
    delay = -1.*delazimuth/dps
    time.sleep(delay)

    # Power decrease dome azimuth off
    switch.off(1)

    #  print 'Decrease dome azimuth switch is  ',switch.status(1)

  else:
    pass
    #  print 'No rotation requested.'  

else:
  pass
  # print "Dome azimuth within tolerance"  
  
exit()
