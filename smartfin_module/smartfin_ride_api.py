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

"""
Smartfin Web Scrape API is an interface that allows smartfin users to get data of their smartfin ride. This module interacts with both the smartfin website and CDIP THREDDS API to get smartfin and CDIP data. 
"""
class Ride:
    
    def __init__(self):
        self.rides = {}
        
        
        
    def add_ride(self, ride_id, data='motion', convert_imu=False):
        """
        adds a ride dataframe to this dictionary 
        
        keyword arguments:
            - ride_id (string): smartfin ride id 
            - data (string): type of smartfin ride data to scrape 
                'ocean': get data of ocean conditions of session
                'motion': get IMU sensor data of session
            - convert_imu (boolean): whether to return dataframe with converted IMU values to m/s^2 with gravity accounted 
        
        """
        # if ride already exists then don't add it again
        if (ride_id in self.rides):
            print('ride already in here')
            return 
        
        
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
        df = df_dropped.dropna(axis=0, how='any')

        # add dataframe to dictionary
        self.rides[ride_id] = df

        if(convert_imu):
            print(self.rides[ride_id]['IMU A2'].mean())
            self.rides[ride_id] = df.apply(lambda reading: reading / 512 * 9.80665 + 9.80665 if reading.name == 'IMU A2' else reading)
            print(self.rides[ride_id]['IMU A2'].mean())
            
        
    def add_rides(self, ride_ids=[], data='motion', convert_imu=False):
        """
        adds multiple ride dataframes to this dictionary 
        
        keyword arguments:
            - ride_id (string): smartfin ride id 
            - data (string): type of smartfin ride data to scrape 
                'ocean': get data of ocean conditions of session
                'motion': get IMU sensor data of session
            - convert_imu (boolean): whether to return dataframe with converted IMU values to m/s^2 with gravity accounted 
        
        """
        for ride in ride_ids:
            self.add_ride(ride, data, convert_imu)
    
    
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
            


            # Reindex on timestamp if there are at least a few rows
            if len(df) > 1:
                df.set_index('UTC', drop = True, append = False, inplace = True)

                # resample data at new interval
                sample_interval = '33ms'
                df = df.resample(sample_interval).mean()
                df['TimeDelta'] = (df['Time']-df['Time'][0])
                return df

        else:
            df = pd.DataFrame() # empty DF just so something is returned
            return df
      
    
    
        
    def get_rides(self, ride_ids=[]):
        """
        returns dataframes of smartfin rides
        
        keyword args:
            - ride_id (string): returns single dataframe of ride_id
            - ride_ids (string array): an array of the ride_ids we want to get. Default is all rides
            
        
        returns:
            - dictionary of ride dataframes in the format {ride_id: dataframe}
        """
        returns = {}
        
        ids = self.generate_id_list(ride_ids)

        # fill returns with dataframes of ids
        for ride_id in ids:
            returns[ride_id] = self.rides[ride_id]
            
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
        
        # get timeframes of all rides in ids list
        for ride_id in ids:
            returns[ride_id] = self.get_timeframe(self.rides[ride_id])
            
        return returns
    
    
    
    def get_timeframe(self, df):
        
        # get the times of the first and last reading
        df = df.reset_index()
        df = df.set_index('UTC')
        start_time = pd.to_datetime(df.index[0]).strftime('%d/%m/%Y %H:%M:%S')
        end_time = pd.to_datetime(df.index[-1]).strftime('%d/%m/%Y %H:%M:%S')
        return [start_time, end_time]
    
    
    
    
    def get_CDIP_heights(self, station, ride_ids=[]):
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
    def label_data( self, ride_id, footage_file = '../Labelled_Footage/Footage.txt', labelling_method = 'simple', sync_threshold = 20000 ):
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
        
        df = self.rides[ride_id]
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


    
    def chunk_data(self, labelled_df, column):
        """
        Splits continuous segments of labelled data into a list of chunks of data

        keyword arguments:
            - labelled_df (dataframe): dataframe to chunk data from
            - column (string): data measurement to chunk

        returns:
            - chunks (list): list of all data chunks
            - chunk_times (list): list of times that correspond with each data point in chunks
            - chunk_start_indices (list): list of indices of each new chunk
            - chunk_end_indices (list): list of indices of every chunk end
            - chunk_count (int): count of how many chunks are in chunks
        """
        chunks = []
        chunk_times = []
        chunk_end_indices = []
        chunk_start_indices = []
        chunk_seen = False
        index = 0
        chunk_count = 0

        for row in labelled_df.iterrows():

            # if surfing stays 0 
            if (row[1][column] == 0 and not chunk_seen):
                chunk_seen = False
                continue

            # if surfing is 1
            elif (row[1][column] == 1):
                if (not chunk_seen): 
                    chunk_seen = True
                    chunk_count += 1
                    chunk_start_indices.append(index)

                index += 1
                chunks.append(row[1]['IMU A2'])
                chunk_times.append(row[1]['Time'])

            # if surfing returns from 1 to 0
            elif (row[1][column] == 0 and chunk_seen):

                chunk_seen = False
                chunk_end_indices.append(index - 1)

        chunk_times = [time / 1000 for time in chunk_times]

        return chunks, chunk_times, chunk_start_indices, chunk_end_indices, chunk_count
       


    # helper methods

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
    