import pandas as pd
import numpy as np

import os
import datetime
import pytz
import re
import requests
import netCDF4
import datetime
import time
from bs4 import BeautifulSoup
import json


# 14743 - Motion Control July 10th
# 14750 - Magnetometer Control July 11th
# 14814 - Pool Displacement Control July 17th
# 14815 - Compass Orientation (Lying on Charger Side) July 19th
# 14816 - Orientation w Higher Sampling (Lying on Charger Side) July 20th
# 14827 - Pool Displacement Control w Higher Sampling (Jul 23)
# 14888 - First Buoy Calibration Experiment (July 30)
# 15218 - Jasmine's Second Ride Sesh filmed with GoPro (Aug 29) //no footage
# 15629 - Jasmine's First Ride Sesh filmed with VIRB (Oct. 24) //first labelled footage!
# 15669 - Jasmine's Second Ride Sesh filmed with VIRB (Nov. 7) //second labelled footage!
# 15692 - Jasmine's 3rd Ride Sesh filmed with VIRB (Nov. 9) //third labelled footage!
# 15686 - Jasmine's 4th Ride Sesh filmed with VIRB (Nov. 11) //fourth labelled footage!


#%% Fin ID scraper
# Input fin ID, get all ride IDs
# base URL to which we'll append given fin IDs
fin_url_base = 'http://surf.smartfin.org/fin/'

# Look for the following text in the HTML contents in fcn below
str_id_ride = 'rideId = \'' # backslash allows us to look for single quote
str_id_date = 'var date = \'' # backslash allows us to look for single quote

#%% Ride ID scraper
# Input ride ID, get ocean and motion CSVs
# Base URL to which we'll append given ride IDs
ride_url_base = 'https://surf.smartfin.org/ride/'

# Look for the following text in the HTML contents in fcn below
str_id_csv = 'img id="temperatureChart" class="chart" src="' 

"""
Smartfin Web Scrape API is an interface that allows smartfin users to get data of their smartfin ride. This module interacts with both the smartfin website and CDIP THREDDS API to get smartfin and CDIP data. 
"""
class Ride:
    
    def __init__(self): 
        print('ride initialized')
 

        
    # MAIN RIDE FUNCTION
    def get_ride_data(self, ride_id, convert_imu=True):
        """
        adds a ride dataframe to this dictionary 
        
        """
        # get df from ride number
        # get given ride's CSV from its ride ID using function above
        dfs = self.get_csv_from_ride_id(ride_id) 
        odf = dfs[0]
        mdf = dfs[1]

        latitude = mdf['Latitude'].mean() / 100000
        longitude = mdf['Longitude'].mean() / 100000
                       
        #Drop the latitude and longitude values since most of them are Nan:
        # mdf_dropped = mdf.drop(columns=['Latitude', 'Longitude'])
        mdf_dropped = mdf.drop(['Latitude', 'Longitude'], axis=1)
        odf_dropped = odf.drop(['salinity', 'Calibrated Salinity', 'Salinity Stable', 'pH', 'Calibrated pH', 'pH Stable'], axis=1)

        #Drop the NAN values from the motion data:
        mdf = mdf_dropped.dropna(axis=0, how='any')
        odf = odf_dropped.dropna(axis=0, how='any')
            
        # convert imu data 
        if(convert_imu):
            mdf = mdf.apply(lambda reading: reading / 512 * 9.80665 - 9.80665 
                                                         if reading.name == 'IMU A2'
                                                         else reading)
            mdf = mdf.apply(lambda reading: reading / 512 * 9.80665
                                                         if reading.name == 'IMU A1' or reading.name == 'IMU A3'
                                                         else reading)

            # convert time into seconds
            mdf['Time'] = [time / 1000 for time in mdf['Time']]
            
        # get timeframe
        start_time, end_time = self.get_timeframe(mdf)
        print(f'calcualting start_time: {start_time}')
        print(f'calcualting end_time: {end_time}')
        
    
        # get nearest CDIP buoy
        mean_CDIP, means_CDIP, temp_CDIP, temps_CDIP, nearest_CDIP = self.CDIP_web_scrape(start_time, end_time, latitude, longitude)
        print(f'retrieved nearest CDIP buoy: {nearest_CDIP}')
        print(f'retrieved CDIP means height for ride: {means_CDIP}')
        print(f'retrieved CDIP means temp for ride: {temps_CDIP}')

        data = {
            'ride_id': ride_id, 
            'start_time': start_time,
            'end_time': end_time,
            'CDIP_buoy': nearest_CDIP, 
            'CDIP_height': mean_CDIP, 
            'CDIP_temp': temp_CDIP, 
            'latitude': latitude,
            'longitude': longitude,
        }

        # data = json.dumps(data)
        print(type(data['ride_id']))
        print(type(data['start_time']))
        print(type(data['end_time']))
        print(type(data['CDIP_buoy']))
        print(type(data['CDIP_height']))
        print(type(data['CDIP_temp']))
        print(type(data['latitude']))
        print(type(data['longitude']))
    
        return data
       
            
        


    # HELPER FUNCTIONS
    
    # Find nearest value in ncTime array to inputted UNIX Timestamp
    def find_nearest(self, array, value):
        idx = (np.abs(array-value)).argmin()
        return array[idx]
    
    
    # Convert human-formatted date to UNIX timestamp
    def getUnixTimestamp(self, humanTime, dateFormat):
        unixTimestamp = int(time.mktime(datetime.datetime.strptime(humanTime, dateFormat).timetuple()))
        return unixTimestamp
    
    
    
    
    def get_csv_from_ride_id (self, ride_id):
        # Build URL for each individual ride
        ride_url = ride_url_base+str(ride_id)
        print(f'fetching ride from: {ride_url}')

        # Get contents of ride_url
        html_contents = requests.get(ride_url).text

        # Find CSV identifier 
        loc_csv_id = html_contents.find(str_id_csv)

        # Different based on whether user logged in with FB or Google
        offset_googleOAuth = [46, 114]
        offset_facebkOAuth = [46, 112]
        if html_contents[loc_csv_id+59] == 'f': # Facebook login
            off0 = offset_facebkOAuth[0]
            off1 = offset_facebkOAuth[1]
        else: # Google login
            off0 = offset_googleOAuth[0]
            off1 = offset_googleOAuth[1]

        csv_id_longstr = html_contents[loc_csv_id+off0:loc_csv_id+off1]
        
        # Stitch together full URL for CSV
        # other junk URLs can exist and break everything
        if ("media" in csv_id_longstr) & ("Calibration" not in html_contents): 

            urls = [f'https://surf.smartfin.org/{csv_id_longstr}Ocean.CSV', f'https://surf.smartfin.org/{csv_id_longstr}Motion.CSV']
            print(f'fetching ocean data from: {urls[0]}')
            print(f'fetching motion data from: {urls[1]}')

            # Go to ocean_csv_url and grab contents (theoretically, a CSV)
            dfs = [pd.read_csv(url, parse_dates = [0]) for url in urls]
           
            # Reindex on timestamp if there are at least a few rows
            dfs = [df.set_index('UTC', drop = True, append = False) for df in dfs]
            
            # resample data at new interval
            sample_interval = '1000ms'
            dfs = [df.resample(sample_interval).mean() for df in dfs]
            dfs[0]['TimeDelta'] = (dfs[0]['Time']-dfs[0]['Time'][0])
            dfs[1]['TimeDelta'] = (dfs[1]['Time']-dfs[1]['Time'][0])

            return dfs

        else:
            print('here')
            df = pd.DataFrame() # empty DF just so something is returned
            return df
      
    

    
    def get_timeframe(self, df):
        
        # get the times of the first and last reading
        df = df.reset_index()
        df = df.set_index('UTC')
        start_time = pd.to_datetime(df.index[0]).strftime('%d/%m/%Y %H:%M:%S')
        end_time = pd.to_datetime(df.index[-1]).strftime('%d/%m/%Y %H:%M:%S')
        return start_time, end_time
    

    
        
        
    def CDIP_web_scrape(self, start_time, end_time, latitude, longitude):
                
        # get nearest station
        station = '201'#self.get_nearest_station(latitude, longitude)
        
        data_url = f'http://thredds.cdip.ucsd.edu/thredds/dodsC/cdip/archive/{station}p1/{station}p1_historic.nc'
        print(f'retriving CDIP wave heights from: {data_url}')
        
        # netCDF data object fetched from CDIP API
        nc = netCDF4.Dataset(data_url)

        
        
        
        # GET WAVE DATA
        # UNIX based time from 1991-yeardate in 30 minute increments
        waveTime = nc.variables['waveTime'][:]

        # wave heights
        Hs = nc.variables['waveHs'][:]
        
        # find the 30 minute chunks that correspond with smartfin ride timeframe
        unixstart = self.getUnixTimestamp(start_time,"%d/%m/%Y %H:%M:%S")
        nearest_date = self.find_nearest(waveTime, unixstart)  # Find the closest unix timestamp
        wave_start_index = np.where(waveTime==nearest_date)[0][0]  # Grab the index number of found date

        unixend = self.getUnixTimestamp(end_time,"%d/%m/%Y %H:%M:%S")
        future_date = self.find_nearest(waveTime, unixend)  # Find the closest unix timestamp
        wave_end_index = np.where(waveTime==future_date)[0][0]  # Grab the index number of found date 
        
        # account for index offsets
#         wave_start_index -= 14
#         wave_end_index -= 14
        
        print(f'calculating significant wave height between {start_time} - {end_time}')
        
        # all wave height averages per 30 minute increments over each month
        ride_hs = Hs[wave_start_index:wave_end_index]
        ride_hs = ride_hs.data
       
    
    
        # GET TEMPERATURE DATA
        # UNIX based time from 1991-yeardate in 30 minute increments
        sstTime = nc.variables['sstTime'][:]
        # ocean temp
        Ts = nc.variables['sstSeaSurfaceTemperature'][:]
        
        # find the 30 minute chunks that correspond with smartfin ride timeframe
        unixstart = self.getUnixTimestamp(start_time,"%d/%m/%Y %H:%M:%S")
        nearest_date = self.find_nearest(sstTime, unixstart)  # Find the closest unix timestamp
        temp_start_index = np.where(sstTime==nearest_date)[0][0]  # Grab the index number of found date

        unixend = self.getUnixTimestamp(end_time,"%d/%m/%Y %H:%M:%S")
        future_date = self.find_nearest(sstTime, unixend)  # Find the closest unix timestamp
        temp_end_index = np.where(sstTime==future_date)[0][0]  # Grab the index number of found date 
        
#         temp_start_index -= 14
#         temp_end_index -= 14
                
        print(f'calculating significant wave height between {start_time} - {end_time}')
            
        # get ocean surface temperature during ride
        ride_ts = Ts[temp_start_index:temp_end_index]
        ride_ts = ride_ts.data
   
        
        
        # CALCULATE MEANS of each month dataset in box_data
        mean_h = ride_hs.mean()
        mean_t = ride_ts.mean()
        
        print(f'mean wave height: {mean_h}')
        print(f'mean ocean temp: {mean_t}')
        
        return mean_h, list(ride_hs), mean_t, list(ride_ts), station

    
    
    def get_nearest_station(self, latitude, longitude):

        # get all active buoys with archived data
        stns = self.get_active_buoys()
   
        # intialize the lowest distance to be some rediculously big number
        lowest_distance = 1000000000
        stn = -1
        count = 0

        # iterate through 0-450 (station numbers are from 28-433 with gaps in between)
        for i in stns:
            
            count += 1

            # format i into a 3 digit string
            i = str(i)
            if len(i) == 1:
                i = '00' + i
            elif len(i) == 2:
                i = '0' + i

            # see if there is a station with the current iteration number
            try:
                data_url = 'http://thredds.cdip.ucsd.edu/thredds/dodsC/cdip/archive/' + i + 'p1/' + i+ 'p1_historic.nc'
                nc = netCDF4.Dataset(data_url)

                # get latitude and longitude of current station
                nc_latitude = nc.variables['metaStationLatitude'][:]
                nc_longitude = nc.variables['metaStationLongitude'][:]
                
                print('', end='\r')
                print(f'checking for nearest buoy... {count}/{len(stns)}')

                # if the current station distance is lower than the lowest distance so far, save it
                curr_distance = abs(nc_latitude - latitude) + abs(nc_longitude - longitude)
                if curr_distance < lowest_distance:
                    lowest_distance = curr_distance
                    stn = i
                else: continue

            except OSError as err:
                continue

        if stn == -1:
            print('no station found error')
            
        return stn

    
    

    def get_active_buoys(self):
        # CDIP active buoys URL
        url="http://cdip.ucsd.edu/m/deployment/station_view/?mode=active"

        # Make a GET request to fetch the raw HTML content
        html_content = requests.get(url).text

        # Parse the html content
        soup = BeautifulSoup(html_content, "lxml")
        table = soup.find("table")
        table_data = table.tbody.find_all("tr")  # contains 2 rows
        stns = []
        for node in table_data:
            try:
                stn = node.findAll('td', text=True)[0]
                stns.append(stn.text.strip(' '))
            except:
                continue

        return stns
        

       

# %%
