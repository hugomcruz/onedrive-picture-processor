'''
------------------------------------------------------------------------------
 Copyright (c) 2021 Hugo Cruz - hugo.m.cruz@gmail.com
 
 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:
 
 The above copyright notice and this permission notice shall be included in
 all copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 THE SOFTWARE.
------------------------------------------------------------------------------
'''

import sys
import os
import time
import json
import datetime
import logging

from onedrive import onedrive_simple_sdk
from image_processing import process_image
from datetime import timezone
from video_processing import video_creation_datetime


############## Classes - Data Objects ####################
class PhotoInfo:
    filename = ""
    month = ""
    year = ""
    status = ""

############ Functions ################

def get_extension(filename):
    basename = os.path.basename(filename)  # os independent
    ext = basename.split('.')[-1]
    return ext.lower()

def read_configuration():
    with open('config.json') as json_file:
        data = json.load(json_file)
        return data


def read_credentials(filename):
    with open(filename) as json_file:
        data = json.load(json_file)
        return data

           


#################################################################################################################################
#################################################################################################################################
#################################################################################################################################
#################################################################################################################################





## Recursive function to transvese the folder structure
def list_onedrive_folder(onedrive_origin_client, source_path, config):
    logging.info("process_onedrive_camera_roll(): Starting to process the onedrive files.")
    
    result = onedrive_origin_client.listfiles(source_path)

    if(result["status"]):

        item_list = result["itemlist"]
        
        for item in item_list:
            if(item["type"] == "folder"):
                logging.info("process_onedrive_camera_roll(): Processing folder: %s", item["name"])
                new_path = source_path + "/" +  item["name"]
                list_onedrive_folder(onedrive_origin_client, new_path, config)

            elif(item["type"] == "file"):
                print(source_path + "/" + item["name"])
    
    else:
        logging.error("Error listing files: %s", result["message"])




######### MAIN PART ##########
logging.basicConfig(format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s', level=logging.ERROR)


logging.info("Listing all files in the directory structure")

### Variables for global processing
destination_credentials_file = ""
destination_path = ""



## Read configuration file
config = read_configuration()

origins = config["origins"]



#### Cycle through all the origins and process the files
for origin in origins:
    profile_name = origin["profile_name"]
    origin_credentials_file = origin["credentials"]
    source_path = origin["source_path"]
    profile_destination_folder = origin["destination_folder"]

    origin_credentials = read_credentials(origin_credentials_file)

    ## Connecting to the origin
    origin_client = onedrive_simple_sdk(origin_credentials["clientID"], origin_credentials["clientSecret"], origin_credentials["refreshToken"])
    logging.info("Connected to origin client profile: %s", profile_name)
  
    list_onedrive_folder(origin_client, source_path, config)


logging.info("Completed listing all files.")





