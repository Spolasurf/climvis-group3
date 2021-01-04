#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 28 18:57:38 2020

@author: rebecca
"""

import os
import gpxpy
import gpxpy.gpx
import os.path 
import sys
import geopy.distance #install it! coordinates distance calculator package (height?)
import math
        
current_dir = os.path.dirname(os.path.abspath(__file__))

 
class Gpx_point:
    """ 
    A class used to represent a single coordinate point
    
    Attributes
    ------------
    lat: float
        the latitude of the point
        default value set to zero
    lon: float
        the longitude of the point
        default value set to zero
    alt: float
        the altitude of the point
        default value set to zero
    """
        
    
    #initializer
    def __init__(self, lat = 0, lon = 0, alt = 0):# dist_km = 0):
        """ 
        Parameters
        ------------
        lat: float
            the latitude of the point
            default value set to zero
        lon: float
            the longitude of the point
            default value set to zero
        alt: float
            the altitude of the point
            default value set to zero""" 
        
        
        self.lat = lat
        self.lon = lon
        self.alt = alt
        
       


# a class for track (list) of extracted points, the elements are of the class Gpx_point
class Gpx_track:
    """ 
    A class used to represent a track of gps points, as taken from a user input .gpx file
    Directly in the initialization, the .gpx file-path is asked as input and its' existence is checked 
    
    Attributes
    ------------
    track: list
        list containing an ordered series of Gpx_point() objects
    

    Methods
    ------------
    extract_gpx_points()
        extracts the gps coordinates from the user input .gpx file, puts them in separate Gpx_point() objects
        the gps coordinates are either segments, waypoints or routes as per standard of gpx documents. 
        Only one type is chosen if multiple types are present. 
        appends each point to Gpx_track.track list is an ordered series 
        alt attribute is assigned to the Gpx_point if given, if not it is default 0
    
    get_all()
        prints lat, lon and alt attributes of each Gpx_point in Gpx_track.track iteratively
        
    get_mean()
        returns mean lat and lon values for the track
    
    get_one(i = int)
        returns lat, lon and alt of Gpx_point at Gpx_track.track[i]
    
    tot_dist()
        returns the total length of the gps track in km per default
        
    Example 
    ---------
     test_track = Gpx_track(gpx_f_path = "write path here")
     test_track.extract_gpx_points() 
     print(test_track.get_all())
     print(test_track.tot_dist())
     
     start_pt = test_track.get_one()
     print(start_pt)       
    """
    
    #initializer
    def __init__(self, track = [], gpx_f_path = None): 
        """
        Property
        ------------
        track: list
            list containing an ordered series of Gpx_point() objects
        gpx_f_path: string
            user input total path to the .gpx file to process
    
        """   

        self.track = track
        self.gpx_f_path = gpx_f_path
            
    
        
    #Methods
    
    def extract_gpx_points(self):       
        """
        method that extracts the gps coordinates from the user input .gpx file, puts them in separate Gpx_point() objects
        the gps coordinates are either segments, waypoints or routes as per standard of gpx documents. 
        Only one type is chosen if multiple types are present. 
        appends each point to Gpx_track.track list is an ordered series 
        alt attribute is assigned to the Gpx_point if given, if not it is default 0

        Returns
        -------
        None.

        """
        #first go in and read and parse gpx_file    
        try:
            gpx_open = open(self.gpx_f_path)
            gpx_parsed = gpxpy.parse(gpx_open)

        except FileNotFoundError:
            print('File does not exist! Program will shut down')
            print("***Stop script***")
            sys.exit() 
    
        #then go in and take lat, lon, height 
        for track in gpx_parsed.tracks:
            for segment in track.segments:
                for point in segment.points:
                    if point.elevation == None:
                        self.track.append(Gpx_point(point.latitude, point.longitude, 0))
                    else:
                        self.track.append(Gpx_point(point.latitude, point.longitude, point.elevation))
                  
            if self.track == []:
                for route in gpx_parsed.routes:
                    for point in route.points:
                        if point.elevation == None:
                            self.track.append(Gpx_point(point.latitude, point.longitude, 0))
                        else:
                            self.track.append(Gpx_point(point.latitude, point.longitude, point.elevation))   
            else: 
                pass

            if self.track == []:
                for waypoint in gpx_parsed.waypoints:
                    if point.elevation == None:
                        self.track.append(Gpx_point(waypoint.latitude, waypoint.longitude, 0))
                    else:
                        self.track.append(Gpx_point(waypoint.latitude, waypoint.longitude, waypoint.elevation))
            else:
                pass
    
    #method to retrieve single point attributes        
    def get_all(self):
        """
        Method to get lat, lon and alt attributes of each Gpx_point in Gpx_track.track iteratively

        Returns
        -------
        None.

        """
       
        for pt in self.track: 
                print(pt.lat, pt.lon, pt.alt)
              
             #not happy with this 
             #because it can print them all but 
             #return statement gives only one out with
             #return (pt.lat, pt.lon, pt.alt)  
             
    #method to retrieve mean of lat and lon      
    def get_mean(self):
        """
        Method to get mean lat and lon attributes o Gpx_track.track iteratively

        Returns
        -------
        mean_lat: float
            mean latitude
        
        mean_lon: float
            mean longitude

        """
        mean_lat = 0
        mean_lon = 0
        for pt in self.track: 
                mean_lat = mean_lat + pt.lat
                mean_lon = mean_lon + pt.lon
        mean_lat = mean_lat/ len(self.track)
        mean_lon = mean_lon/ len(self.track)        
        
        return mean_lat, mean_lon
    
    #method to get single coordinate
    def get_one(self, i = 0):
        """
        Parameters
        ----------
        i : int
            index of self.track list. The default is 0.

        Returns
        -------
        float
            self.track[i] lat attribute
         float
            self.track[i] lon attribute
         float
            self.track[i] alt attribute
        
        """
        
        return self.track[i].lat, self.track[i].lon, self.track[i].alt
    
    #method to compute length of track
    def tot_dist(self):
        """
        Method to compute the total length of the user input gpx track. 
        
        Returns
        -------
        dist_km : float
            Total length of track. Default value in km, rounded to 2 decimal places.

        """
        
    
        dist_mt = 0 
        #compute distance between i and i-1 points, the order is lat, lon
        for i in range(1, len((self.track))):
           pt_temp_coord_2 = (self.track[i].lat, self.track[i].lon)
           pt_temp_coord_1 = (self.track[i-1].lat, self.track[i-1].lon)
           #horizontal (sea level) distance in meters
           horiz_dist = (geopy.distance.distance(pt_temp_coord_1, pt_temp_coord_2).km)*1000
           #vertical altitude delta
           delta_alt = (self.track[i].alt - self.track[i-1].alt)
           #point to point distance
           pt_pt_dist = math.sqrt(horiz_dist**2 + delta_alt**2)
           dist_mt = dist_mt + pt_pt_dist
           dist_km = dist_mt/ 1000
           # print(delta_alt)
           # print(horiz_dist)
           # print(pt_pt_dist)
        #print(dist_km,' km')
        self.dist_km = dist_km
        return  round(dist_km, 2)




## Program Start
# gpx_file_name = input('Give the name of the gpx file: ')
# gpx_file_path = os.path.join(current_dir, gpx_file_name)
#         #gpx_file_path = os.path.abspath(gpx_file_name) 
# if os.path.isfile(gpx_file_path):
#     gpx_file_path = gpx_file_path
# else:
#                 print('File not found in cwd!')
#                 gpx_file_path = input('Please give whole path to gpx file: ')
#                 if os.path.isfile(gpx_file_path):
#                     gpx_file_path = gpx_file_path
#                 else:
#                     print('File does not exist! Program will shut down')
#                     print("***Stop script***")
# #                     sys.exit()   

# a = Gpx_track( gpx_f_path = '/home/rebecca/Desktop/AtmWiss/SciPro/climvis-master/climvis/tt.gpx' )
# print(a.track)

# #print(a._Gpx_track__gpx_file_path) #-ClassName to access hidden attributes to check!        
# print(a.extract_gpx_points() )

# print(a.get_all())
# print(a.tot_dist())
# b = a.get_one()
# print(type(b), b[0], b)
# print(a.get_mean())







