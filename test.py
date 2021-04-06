


import sys
sys.path.append('/Users/hcruz/Documents/development/python/onedrive_simple_sdk/src')
sys.path.append('/root/dev/onedrive_simple_sdk/src')
sys.path.append('/home/ec2-user/onedrive_simple_sdk/src')

 

import os
import time
import json
import datetime
import logging
import hashlib

from onedrive import onedrive_simple_sdk
from image_processing import process_image
from datetime import timezone
from video_processing import video_creation_datetime


def read_configuration():
    with open('config.json') as json_file:
        data = json.load(json_file)
        return data


def read_credentials(filename):
    with open(filename) as json_file:
        data = json.load(json_file)
        return data



def compare_files(onedrive_client, onedrive_path, local_file):
 ## Connecting to the origin
   
    result = onedrive_client.filedetails(onedrive_path)

    if(result["status"] == False):
        return {
            "status": False,
            "message": result["message"]
        }

    od_file_hash = result["sha256hash"].upper()
    od_file_size = result["size"]
    
    
    try:
        with open(local_file,"rb") as f:
            bytes = f.read() # read entire file as bytes
            local_file_hash = hashlib.sha256(bytes).hexdigest().upper()

        stat = os.stat(local_file)
        local_file_size = stat.st_size
    except FileNotFoundError as ex:
        return {
            "status": False,
            "message": "Local file not found."
        }
    except ex2:
        return {
            "status": False,
            "message": ex2
        }



    print("Local file hash:", local_file_hash)
    print("Onedrive hash  :",od_file_hash )
    
    print("Local file size:", local_file_size)
    print("Onedrive size  :",od_file_size)


    ### Compare the Files

    hash_comparison = False
    size_comparison = False

    ## Hash comparison
    if(local_file_hash == od_file_hash):
        hash_comparison = True
    
    if(local_file_size == od_file_size):
        size_comparison = True


    if(hash_comparison and size_comparison):
        return {
            "status": True,
            "comparison": True,
            "message": "Files are equal"
        }
    else:
        return {
            "status": True,
            "comparison": False,
            "message": "Files are different"
        }




   

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
    client = onedrive_simple_sdk(origin_credentials["clientID"], origin_credentials["clientSecret"], origin_credentials["refreshToken"])
    
    result = compare_files(client, "/nas-children/ana-xuan-files/school/smart-kids/smarttkids-ana-2018-11.pdf", "/Users/hcruz/Downloads/smarttkids-ana-2018-11.pdf")

    print(result)


