#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
import numpy as np
import warnings
import datetime
import time
import os

warnings.filterwarnings('ignore')
pd.options.display.max_rows = 9999
pd.options.display.max_columns = 9999


# In[2]:


# Take the file names that has the data from last 1 month

now = datetime.datetime.now().date()
one_month_before = now - datetime.timedelta(days=30)
file_in_interest_list = []
for file_name in os.listdir("D:/H/DataSci/SSO_User_analiz/data_07042020/sample_transaction_log"):
    date_object = datetime.datetime.strptime(file_name.split(".")[0], '%Y-%m-%d').date()
    if date_object > one_month_before:
        file_in_interest_list.append(file_name)
        
# Selected files are combined into a Data Frame

df_merged = pd.DataFrame()
for file in file_in_interest_list:
    df_file = pd.read_csv("data_07042020/sample_transaction_log/{}".format(file))
    df_merged = df_merged.append(df_file)


# In[3]:


df_merged.tail()


# In[4]:


# The following variables will be used to detect the script users.

df = df_merged
min_time_delta_to_be_a_script = 24 # Hours, 
min_percent_of_labeled_records_to_be_a_script = 80 # %, 


# In[5]:


# Filter is applies to get "command_time","user_name","command","host","client_ip" columns

df.command_time = pd.to_datetime(df.command_time)
df_to_group = df[["command_time","user_name","command","host","client_ip"]]
df = df.sort_values(by="command_time")
df.head()


# In[6]:


# The records that have same user,command,host and client within 1 month are extracted.

grouped_df = df_to_group.groupby(["user_name","command","host","client_ip"]).count().query('command_time > 3').reset_index()
grouped_df.columns = ["user_name","command","host","client_ip","command_count"]
grouped_df.head()


# In[8]:


# Check how many records that exists

grouped_df.count()


# In[7]:


# The users that start with TC, TE, EXT and NG are filtered.

grouped_df = grouped_df[grouped_df.user_name.str.contains("te|tc|ng|ext",case=False)]


# In[8]:


grouped_df.user_name.unique()


# In[9]:


# For all records that have more than 3 lines are iterated in order to determine if they access to the system periodically and
# whether if they match with the scripting rules.

is_script_list = []
for df_index in grouped_df.index.to_list():
    user_name = grouped_df.loc[[df_index]].user_name.to_list()[0]
    command = grouped_df.loc[[df_index]].command.to_list()[0]
    host = grouped_df.loc[[df_index]].host.to_list()[0]
    client_ip = grouped_df.loc[[df_index]].client_ip.to_list()[0]

    # Time difference is calculated for all users that have access more than three times.
    command = command.replace("'","_")
    command = command.replace('"',"_")
    df_date_user = df_to_group.query("user_name == '{}' and command == '{}' and host =='{}' and client_ip =='{}'".format(user_name,command,host,client_ip))
    df_date_user["time_delta"] = df_date_user['command_time'].diff().dt.total_seconds().fillna(0)

    # In order to eliminate the situations like couldnt access the server or halting the script, .85 quantile is taken so as to
    # eliminate also this outliers.
    df_date_user = df_date_user.drop(df_date_user[df_date_user["time_delta"] > df_date_user.time_delta.quantile([.77]).values[0]].index,axis=0)

    # Since it is a timediff, the first row will be 0. This are eliminated.
    df_date_user = df_date_user.query('time_delta != 0.0')
    
    # Command diff values are vizualized.
    df_date_user.index = df_date_user.command_time
    #fig, axes = plt.subplots()

    # For the time delta values Unsupervised clustering is done with DBCSAN.
    array_1d = df_date_user.time_delta.astype(int).to_numpy().reshape(-1,1)
    EPS = df_date_user.time_delta.max() / 229
    if EPS > 0.0:
        db = DBSCAN(eps = EPS).fit(array_1d)

        #  In order to detect the scripts the following conditions are used:
        #  1- There must be time difference between the records at leaest min_time_delta_to_be_a_script in order to be a script,
        #  2- The labeled record percentage must be greater than min_percent_of_labeled_records_to_be_a_script,
        #  3- The command entrances that belong to a script before more than 3 sample, but the for the last 3 entrance dont
        # have the property to be a script, must be eliminated.
        
        date_condition_to_be_a_script = datetime.timedelta(hours = min_time_delta_to_be_a_script) < (df_date_user.command_time.max() - df_date_user.command_time.min())
        df_date_user["labels"] = db.labels_    
        percent_of_labeled_records = 100 * (df_date_user.query('labels != -1').count()[0] / df_date_user.count()[0])
        if df_date_user.count()[0] > 3:
            last_3_sample_is_script = not ((df_date_user.labels.to_list()[-1] == -1) and (df_date_user.labels.to_list()[-2] == -1) and (df_date_user.labels.to_list()[-3] == -1))
        else:
            last_3_sample_is_script = False
        detected_as_script = date_condition_to_be_a_script and (percent_of_labeled_records > min_percent_of_labeled_records_to_be_a_script) and last_3_sample_is_script
        is_script_list.append(detected_as_script)
        #df_date_user.time_delta.plot(ax=axes,style=".",title="Record Index: {}\nLabels: {}\nUser Name: {}\nCommand: {}\nIs_script: {}".format(df_index,db.labels_,user_name,command,detected_as_script))
        if df_index % 500 == 0:
            print("{} , INDEX : {}".format(datetime.datetime.now(),df_index))
    else:
        is_script_list.append(False)
        
grouped_df["is_script"] = is_script_list


# In[10]:


grouped_df.head()


# In[11]:


# All users that are running scripts are found.
grouped_df.query('is_script == True').user_name.unique()


# In[13]:


# Extract the connection time graph of script users.

for df_index in df_script_user_list.index.to_list():
    user_name = grouped_df.loc[[df_index]].user_name.to_list()[0]
    command = grouped_df.loc[[df_index]].command.to_list()[0]
    host = grouped_df.loc[[df_index]].host.to_list()[0]
    client_ip = grouped_df.loc[[df_index]].client_ip.to_list()[0]

    # Time difference is calculated for all users that have access more than three times.
    command = command.replace("'","_")
    command = command.replace('"',"_")
    df_date_user = df_to_group.query("user_name == '{}' and command == '{}' and host =='{}' and client_ip =='{}'".format(user_name,command,host,client_ip))
    df_date_user["time_delta"] = df_date_user['command_time'].diff().dt.total_seconds().fillna(0)

    # In order to eliminate the situations like couldnt access the server or halting the script, .85 quantile is taken so as to
    # eliminate also this outliers.
    df_date_user = df_date_user.drop(df_date_user[df_date_user["time_delta"] > df_date_user.time_delta.quantile([.77]).values[0]].index,axis=0)
    df_date_user = df_date_user.query('time_delta != 0.0')
    
    # Command diff values are vizualized.
    df_date_user.index = df_date_user.command_time
    fig, axes = plt.subplots()

    # For the time delta values Unsupervised clustering is done with DBCSAN.
    array_1d = df_date_user.time_delta.astype(int).to_numpy().reshape(-1,1)
    EPS = df_date_user.time_delta.max() / 229
    if EPS > 0.0:
        db = DBSCAN(eps = EPS).fit(array_1d)

        #  In order to detect the scripts the following conditions are used:
        #  1- There must be time difference between the records at leaest min_time_delta_to_be_a_script in order to be a script,
        #  2- The labeled record percentage must be greater than min_percent_of_labeled_records_to_be_a_script,
        date_condition_to_be_a_script = datetime.timedelta(hours = min_time_delta_to_be_a_script) < (df_date_user.command_time.max() - df_date_user.command_time.min())
        df_date_user["labels"] = db.labels_    
        percent_of_labeled_records = 100 * (df_date_user.query('labels != -1').count()[0] / df_date_user.count()[0])
        last_3_sample_is_script = not ((df_date_user.labels.to_list()[-1] == -1) and (df_date_user.labels.to_list()[-2] == -1) and (df_date_user.labels.to_list()[-3] == -1))
        detected_as_script = date_condition_to_be_a_script and (percent_of_labeled_records > min_percent_of_labeled_records_to_be_a_script) and last_3_sample_is_script
        is_script_list.append(detected_as_script)
        df_date_user.time_delta.plot(ax=axes,style=".",title="Record Index: {}\nLabels: {}\nUser Name: {}\nCommand: {}\nIs_script: {}".format(df_index,db.labels_,user_name,command,detected_as_script))
        if df_index % 500 == 0:
            print("{} , INDEX : {}".format(datetime.datetime.now(),df_index))
    else:
        is_script_list.append(False)
        


# In[18]:


df_script_user_list.to_csv("df_script_user_list_tcell.csv")


# In[3]:


df = pd.read_csv("df_script_user_list_tcell.csv")


# In[10]:


# Convert all script records to json format.

import json

df_json = df.to_json(orient = "records")

"""‘split’ : dict like {‘index’ -> [index], ‘columns’ -> [columns], ‘data’ -> [values]}
‘records’ : list like [{column -> value}, … , {column -> value}]
‘index’ : dict like {index -> {column -> value}}
‘columns’ : dict like {column -> {index -> value}}
‘values’ : just the values array
‘table’ : dict like {‘schema’: {schema}, ‘data’: {data}}"""

# Write JSON to a file
with open('script_user_json.txt', 'w') as outfile:
    json.dump(df_json, outfile)
    
# Read JSON from file:
with open('script_user_json.txt') as json_file:
    df_json = json.load(json_file)


# In[9]:


df_json

