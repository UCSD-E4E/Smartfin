import pandas as pd
import numpy as np

import os
import datetime
import pytz
import re
import statsmodels.api as sm
import requests
import netCDF4
import datetime
import time

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


class Ride:
    
    def __init__(self, ride_id, data):
        
        """
        smartfin web scraper module interacts with Smartfin and CDIP websites to retrieve data of a given smartfin session
        
        keyword arguments:
            - ride_id (string): smartfin ride id 
            - data (string): type of smartfin ride data to scrape 
                'ocean': get data of ocean conditions of session
                'motion': get IMU sensor data of session
        """
        
        data = data.lower()
        
        # get df from ride number
        try:
            # get given ride's CSV from its ride ID using function above
            df = self.get_csv_from_ride_id(ride_id, data) 
           
        except: 
            print("Ride threw an exception!")

        if (data == 'motion'):
            #Drop the latitude and longitude values since most of them are Nan:
            df_dropped = df.drop(columns=['Latitude', 'Longitude'])

        #Drop the NAN values from the motion data:
        df_dropped = df_dropped.dropna(axis=0, how='any')
        self.df = df_dropped
    
    
    
    def get_csv_from_ride_id (self, ride_id, data):
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

            csv_url = ''
            if (data == 'ocean'):
                csv_url = f'https://surf.smartfin.org/{csv_id_longstr}Ocean.CSV'
                print(f'fetching ocean data from: {csv_url}')

            elif (data == 'motion'):
                csv_url = f'https://surf.smartfin.org/{csv_id_longstr}Motion.CSV'
                print(f'fetching motion data from: {csv_url}')

            else: 
                print(f'{data} csv file not found')

            # Go to ocean_csv_url and grab contents (theoretically, a CSV)
            df = pd.read_csv(csv_url, parse_dates = [0])
            elapsed_timedelta = (df['UTC']-df['UTC'][0])
            df['elapsed'] = elapsed_timedelta/np.timedelta64(1, 's')

            # Reindex on timestamp if there are at least a few rows
            if len(df) > 1:
                df.set_index('UTC', drop = True, append = False, inplace = True)

                # resample data at new interval
                sample_interval = '33ms'
                df_resample = df.resample(sample_interval).mean()
                return df

        else:
            df = pd.DataFrame() # empty DF just so something is returned
            return df
      
    
    
        
    def get_ride_dataframe (self):
        
        """
        returns dataframe of this ride session
        
        returns:
            - df: dataframe of session
        """
        
        return self.df
        

    
    def get_ride_timeframe(self):
        
        """
        Calculates the start and end time of this smartfin session in format: %d/%m/%Y %H:%M:%S
        
        returns:
            - start_time (float): start time of session
            - end_time (float): end time of session
        """
        
        # get the times of the first and last reading
        df = self.df
        df = df.reset_index()
        df = df.set_index('UTC')
        start_time = pd.to_datetime(df.index[0]).strftime('%d/%m/%Y %H:%M:%S')
        end_time = pd.to_datetime(df.index[-1]).strftime('%d/%m/%Y %H:%M:%S')
        return start_time, end_time
    
    
    # Find nearest value in ncTime array to inputted UNIX Timestamp
    def find_nearest(self, array, value):
        idx = (np.abs(array-value)).argmin()
        return array[idx]
    
    
    # Convert human-formatted date to UNIX timestamp
    def getUnixTimestamp(self, humanTime, dateFormat):
        unixTimestamp = int(time.mktime(datetime.datetime.strptime(humanTime, dateFormat).timetuple()))
        return unixTimestamp
    
    
    def get_CDIP_heights(self, station):
        
        """
        Retrieves the average wave height for a smartfin ride according to the CDIP website
        
        keyword arguments:
            - station (string): buoy number
        
        returns:
            - mean (float): mean significant wave height for the entire session
            - ride_hs (float list): mean significant wave height for each 30 minute period during the session
        """
        
        start_time, end_time = self.get_ride_timeframe()
        data_url = f'http://thredds.cdip.ucsd.edu/thredds/dodsC/cdip/archive/{station}p1/{station}p1_historic.nc'
        print(f'retriving CDIP wave heights from: {data_url}')
        
        # netCDF data object fetched from CDIP API
        nc = netCDF4.Dataset(data_url)

        # UNIX based time from 1991-yeardate in 30 minute increments
        ncTime = nc.variables['sstTime'][:]
        timeall = [datetime.datetime.fromtimestamp(t) for t in ncTime]

        # wave heights
        Hs = nc.variables['waveHs']
        
        # find the 30 minute chunks that correspond with smartfin ride timeframe
        unixstart = self.getUnixTimestamp(start_time,"%m/%d/%Y %H:%M:%S")
        nearest_date = self.find_nearest(ncTime, unixstart)  # Find the closest unix timestamp
        start_index = np.where(ncTime==nearest_date)[0][0]  # Grab the index number of found date

        unixend = self.getUnixTimestamp(end_time,"%m/%d/%Y %H:%M:%S")
        future_date = self.find_nearest(ncTime, unixend)  # Find the closest unix timestamp
        end_index = np.where(ncTime==future_date)[0][0]  # Grab the index number of found date 
        
        print(f'calculating significant wave height between {start_time} - {end_time}')
        
        # all wave height averages per 30 minute increments over each month
        ride_hs = Hs[start_index:end_index]
        ride_hs = ride_hs.data
        
        # calculate means of each month dataset in box_data
        mean = ride_hs.mean()

        print(f'mean wave height: {mean}')
        
        return mean, ride_hs
        
           


        


