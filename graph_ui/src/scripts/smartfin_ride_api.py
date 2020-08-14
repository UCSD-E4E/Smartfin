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
        self.rides = {}
        
 
        
    def get_rides(self, ride_ids=[], data='motion', convert_imu=False):
        """
        returns dataframes of smartfin rides
        
        keyword args:
            - ride_ids (string array): an array of the ride_ids we want to get. Default is all rides
            - data (string): type of dataframe to return (motion, ocean)
            - convert_imu (boolean): whether or not to convert IMU accelerations into m/s^2
            
        returns:
            - dictionary of ride dataframes in the format {ride_id: dataframe}
        """
        returns = {}
        
        ids = self.generate_id_list(ride_ids)
        
        # if data is ocean, don't convert imu
        if(data == 'ocean'): convert_imu = False
        
        # load in dataframes if not in directory
        self.add_rides(ids)

        # fill returns with dataframes of ids
        for ride_id in ids:
            returns[ride_id] = self.rides[ride_id][data]
            
            # convert imu data 
            if(convert_imu):
                returns[ride_id] = returns[ride_id].apply(lambda reading: reading / 512 * 9.80665 - 9.80665 
                                                              if reading.name == 'IMU A2' 
                                                              else reading)
                
                # convert time into seconds
                returns[ride_id]['Time'] = [time / 1000 for time in returns[ride_id]['Time']]

            
        return returns       
         
    
    def get_ride_timeframes(self, ride_ids=[]): 
        """
        Calculates the start and end time of smartfin sessions in format: %d/%m/%Y %H:%M:%S
        
        keyword arguments:
            - ride_ids (string list): the rides to get the timeframes of. Default is all rides
        
        returns:
            - dictionary of start and end times in the format {ride_id: [start_time, end_time]}
        """
        returns = {}
        
        ids = self.generate_id_list(ride_ids)
        
        # load in dataframes if not in directory
        self.add_rides(ids)
        
        # get timeframes of all rides in ids list
        for ride_id in ids:
            returns[ride_id] = self.get_timeframe(self.rides[ride_id]['motion'])
            
        return returns
    
    
    
    def get_timeframe(self, df):
        
        # get the times of the first and last reading
        df = df.reset_index()
        df = df.set_index('UTC')
        start_time = pd.to_datetime(df.index[0]).strftime('%d/%m/%Y %H:%M:%S')
        end_time = pd.to_datetime(df.index[-1]).strftime('%d/%m/%Y %H:%M:%S')
        return [start_time, end_time]
    
    
    
    
    def get_CDIP_heights(self, station='201', ride_ids=[]):
        """
        Retrieves the average wave height for smartfin rides according to CDIP
        
        keyword arguments:
            - station (string): buoy number
            - ride_ids (string list): smartfin ride ids to get CDIP wave heights from 
        
        returns:
            - dictionary of CDIP wave heights in the format {ride_id: [mean_wave_height, [list of mean wave heights every 30 mins]]}
        """
        returns = {}
        
        ids = self.generate_id_list(ride_ids)
        
        for ride_id in ids:
            returns[ride_id] = self.CDIP_web_scrape(ride_id, station)
            
        return returns
        
        
    def CDIP_web_scrape(self, ride_id, station):
        
        start_time, end_time = self.get_ride_timeframes(ride_id)[ride_id]
        data_url = f'http://thredds.cdip.ucsd.edu/thredds/dodsC/cdip/archive/{station}p1/{station}p1_historic.nc'
        print(f'retriving CDIP wave heights from: {data_url}')
        
        # netCDF data object fetched from CDIP API
        nc = netCDF4.Dataset(data_url)

        # UNIX based time from 1991-yeardate in 30 minute increments
        ncTime = nc.variables['waveTime'][:]

        # wave heights
        Hs = nc.variables['waveHs']
        
        # find the 30 minute chunks that correspond with smartfin ride timeframe
        unixstart = self.getUnixTimestamp(start_time,"%d/%m/%Y %H:%M:%S")
        nearest_date = self.find_nearest(ncTime, unixstart)  # Find the closest unix timestamp
        start_index = np.where(ncTime==nearest_date)[0][0]  # Grab the index number of found date

        unixend = self.getUnixTimestamp(end_time,"%d/%m/%Y %H:%M:%S")
        future_date = self.find_nearest(ncTime, unixend)  # Find the closest unix timestamp
        end_index = np.where(ncTime==future_date)[0][0]  # Grab the index number of found date 
        
        # account for index offsets
        start_index -= 14
        end_index -= 14
        
        print(f'calculating significant wave height between {start_time} - {end_time}')
        
        # all wave height averages per 30 minute increments over each month
        ride_hs = Hs[start_index:end_index]
        ride_hs = ride_hs.data
        
        # calculate means of each month dataset in box_data
        mean = ride_hs.mean()
        
        print(f'mean wave height: {mean}')
        
        return [mean, list(ride_hs)]
        
        
        
           
    #simple method: only walking, paddling, floating, surfing
    #complex method: columns created based on footage file labels
    def label_data( self, labelled_df, footage_file = '../Labelled_Footage/Footage.txt', labelling_method = 'simple', sync_threshold = 20000 ):
        """
        Returns a labelled dataframe of a smartfin ride according to a corresponding footage file
        
        keyword arguments:
            - ride_id (string): id of the ride to label
            - footage_file (path string): file with time labels that will be used to label the dataframe
            - labelling_method (string: either 'simple' or 'complex'): 
                    defines the list of labels used to label the dataframe
                        complex = longer list of specific surfer actions
                        simple = labels are: surfing, floating, paddling, walking
            - sync_threshold: idk what this means but hey, i guess we just leave it here
            
            
        returns:
            - labelled dataframe of smartfin ride
        """
        
        df = labelled_df
        # calculate sync_buf which will be used to merge the footage data and the imu data    
        #First, perform sync
        sync_buf = 0
        with open(footage_file) as file:
            # for each reading in footage file: 
            for line in file:     

                # get labeled time and format it into a time structure object            
                labelled_time = line.split(None, 2) 
    #             print('labelled_time: ', labelled_time)
                try:
                    cur_time = time.strptime(labelled_time[0], '%M:%S')
    #                 print('curr_time: ', cur_time)
                except:
                    continue

                #             
                labelled_time[1] = labelled_time[1].rstrip()
                if labelled_time[1].lower() == 'sync': #Assumption that first word in sync line is "sync"
                    sync_time = cur_time.tm_min * 60 * 1000 + cur_time.tm_sec * 1000
#                     print(f'sync_time: {sync_time}')
                    index = 0
                    start = 0
                    end = 0
                    #Syncing occurs when IMU A2 data is negative for a longer period than the provided threshold
                    #Default is 20 seconds
                    for data in df['IMU A2']:
    #                     print(data)
                        # 
                        if data < 0 and start == 0:
                            start = df['TimeDelta'][index]
    #                         print('start: ', start)
                        elif data > 0 and start != 0:
                            end = df['TimeDelta'][index]
    #                         print('end: ', end)

                            # calculate the buffer between the time of sync start and the sync time                        
                            if end - start > sync_threshold:
                                sync_buf = start - sync_time

                                break
                            start = 0
                        index += 1

        accepted_labels = set()
#         print(f'sync_buf: {sync_buf}')


        # SYNC DONE NOW START LABELING
        # if in simple label mode, create 4 classifications of footage data, if not, 
        # then just use the labels in the footage file 
        if labelling_method == 'simple':
            accepted_labels = {'WALKING', 'PADDLING', 'FLOATING', 'SURFING'}

            # add label columns and fill with default 0        
            #Create new DataFrame containing label info
            label_frame = pd.DataFrame(0, index = df.index, columns = accepted_labels)
            for label in accepted_labels:
#                 print(f'label: {label}')
                label_frame[label] = [0] * len(df['Time'])


        # use the calulated sync_buf to alignt he footage data with the imu data
        #Convention of labelled footage text: "MINUTE:SECOND LABEL"
        elapsed_time = 0
        cur_label = ''
        buffer = 0
        with open(footage_file) as file:
            for line in file:

                # if simple method, just look for first word
                # labelled time is a tuple containing the time of event and the type of event
                if labelling_method == 'simple':
                    labelled_time = line.split(None, 2) #simple categorizes on a one-word basis
                else:
                    labelled_time = line.split(None, 1) #complex requires the entire label\


                #If the first word is not a properly formatted time, the line cannot be read
                try:
                    # format time in time structure
                    cur_time = time.strptime(labelled_time[0], '%M:%S')
                    # calculate the current time in ms using sync_buf                
                    cur_timeMS = cur_time.tm_min * 60 * 1000 + cur_time.tm_sec * 1000 + sync_buf
                except:
                    continue

                labelled_time[1] = labelled_time[1].rstrip() #Remove potential newline



                #Check for end of video and modify buffer accordingly
                # assign the time of the 'end of video' to buffer
                if labelled_time[1].lower() == 'end of video': #Assumption that label end video with "end of video"
                    buffer += cur_timeMS


                #----Complex "mode" below: --------

                #Modify accepted labels list if reading a new label and in complex mode
                elif labelling_method == 'complex' and (labelled_time[1].upper() not in accepted_labels):
                    accepted_labels.add(labelled_time[1].upper())
                    if not cur_label:
                        label_frame = pd.DataFrame(0, index = df.index, columns = accepted_labels)
                    label_frame[labelled_time[1].upper()] = [0] * len(df['Time'])

                if labelled_time[1].upper() in accepted_labels:
#                     print(df['TimeDelta'][elapsed_time] < cur_timeMS + buffer)
                    # when cur_label is unchanged, fill keep filling rows with same label
                    while (elapsed_time < len(df['Time']) and
                          (np.isnan(df['TimeDelta'][elapsed_time]) or
                           df['TimeDelta'][elapsed_time] < cur_timeMS + buffer)):

                        # mark label in dataframe
                        if cur_label != '':
                            label_frame[cur_label][elapsed_time] = 1

                        # increment to fill the next row
                        elapsed_time += 1

                    # change label 
                    if labelled_time[1].upper() != 'end of video':
    #                     print('labelled_time: ', labelled_time)
    #                     print(f'elapsed_time: {elapsed_time}')
                        cur_label = labelled_time[1].upper()
#                         print(f'cur_label: {cur_label}')


        # concatinate time labels with their corresponsing measurements by time index    
        labelled = pd.concat([df, label_frame], axis = 1)
        return labelled

       


    # helper methods 
    def add_ride(self, ride_id):
        """
        adds a ride dataframe to this dictionary 
        
        """
        # if ride already exists then don't add it again
        if (ride_id in self.rides):
            print('ride already in here')
            return 

        # get df from ride number
        # get given ride's CSV from its ride ID using function above
        dfs = self.get_csv_from_ride_id(ride_id) 
        odf = dfs[0]
        mdf = dfs[1]


        #Drop the latitude and longitude values since most of them are Nan:
        mdf_dropped = mdf.drop(columns=['Latitude', 'Longitude'])

        #Drop the NAN values from the motion data:
        mdf = mdf_dropped.dropna(axis=0, how='any')
        odf = odf.dropna(axis=0, how='any')
        
      
        self.rides[ride_id] = {}

        # add dataframe to dictionary
        self.rides[ride_id]['motion'] = mdf
        self.rides[ride_id]['ocean'] = odf
            
        
    def add_rides(self, ride_ids=[]):
        """
        adds multiple ride dataframes to this dictionary 
        
        """
        for ride in ride_ids:
            self.add_ride(ride)
        
    
    def generate_id_list (self, ride_ids):
        
        ids = []
        
        # add only 1 ride to ids
        if(type(ride_ids) == str):
            ids.append(ride_ids)
        
        # add all rides to ids
        elif(ride_ids == []):   
            ids = list(self.rides.keys())

        # add only specified rides to ids
        else:
            ids = ride_ids
          
        return ids
    
    
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
            sample_interval = '33ms'
            dfs = [df.resample(sample_interval).mean() for df in dfs]
            dfs[0]['TimeDelta'] = (dfs[0]['Time']-dfs[0]['Time'][0])
            dfs[1]['TimeDelta'] = (dfs[1]['Time']-dfs[1]['Time'][0])

            return dfs

        else:
            print('here')
            df = pd.DataFrame() # empty DF just so something is returned
            return df
      
    
    
    

# %%
