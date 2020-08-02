import pandas as pd
import numpy as np

import os
import datetime
import pytz
import re
import statsmodels.api as sm
import requests

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
    
    def __init__(self, ride_id):
        self.df = self.get_ride_dataframe(ride_id)
    
    def get_csv_from_ride_id (self, rid):
        # Build URL for each individual ride
        ride_url = ride_url_base+str(rid)
        print(ride_url)

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

    #    print(csv_id_longstr)

        # Stitch together full URL for CSV
        # other junk URLs can exist and break everything
        if ("media" in csv_id_longstr) & ("Calibration" not in html_contents): 

            ocean_csv_url = 'https://surf.smartfin.org/'+csv_id_longstr+'Ocean.CSV'
            motion_csv_url = 'https://surf.smartfin.org/'+csv_id_longstr+'Motion.CSV'

            print(ocean_csv_url)
            # Go to ocean_csv_url and grab contents (theoretically, a CSV)
            ocean_df_small = pd.read_csv(ocean_csv_url, parse_dates = [0])
            elapsed_timedelta = (ocean_df_small['UTC']-ocean_df_small['UTC'][0])
            ocean_df_small['elapsed'] = elapsed_timedelta/np.timedelta64(1, 's')

            motion_df_small = pd.read_csv(motion_csv_url, parse_dates = [0])

            # Reindex on timestamp if there are at least a few rows
            if len(ocean_df_small) > 1:
                ocean_df_small.set_index('UTC', drop = True, append = False, inplace = True)
                motion_df_small.set_index('UTC', drop = True, append = False, inplace = True)

                #print(ocean_df_small)
                #print(motion_df_small)

                #May need to change this sampling interval:
                sample_interval = '33ms'


                ocean_df_small_resample = ocean_df_small.resample(sample_interval).mean()
                motion_df_small_resample = motion_df_small.resample(sample_interval).mean()

                # No need to save many extra rows with no fix
                motion_df_small = motion_df_small[~np.isnan(motion_df_small.Latitude)]

                return ocean_df_small_resample, motion_df_small_resample

        else:
            ocean_df_small_resample = pd.DataFrame() # empty DF just so something is returned
            motion_df_small_resample = pd.DataFrame() 
            return ocean_df_small_resample, motion_df_small_resample
        
        
    def get_ride_dataframe (self, ride_id):
        
        appended_ocean_list = [] # list of DataFrames from original CSVs
        appended_motion_list = []
        appended_multiIndex = [] # fin_id & ride_id used to identify each DataFrame

        # get df from ride number
        try:
            # get given ride's CSV from its ride ID using function above
            ocean_df, motion_df = self.get_csv_from_ride_id(ride_id) 
           
        except: 
            print("Ride threw an exception!")

       
        #Drop the latitude and longitude values since most of them are Nan:
        motion_df_dropped = motion_df.drop(columns=['Latitude', 'Longitude'])

        #Drop the NAN values from the motion data:
        motion_df_dropped = motion_df_dropped.dropna(axis=0, how='any')
        return motion_df_dropped

    
    def get_ride_timeframe(self):
        
        df = self.df
        df = df.reset_index()
        df = df.set_index('UTC')
        start_time = pd.to_datetime(df.index[0]).strftime('%d/%m/%Y %H:%M:%S')
        end_time = pd.to_datetime(df.index[-1]).strftime('%d/%m/%Y %H:%M:%S')
        year_date = start_time[6:10]
        return start_time, end_time, year_date
