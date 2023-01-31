'''
------------------------------------------------------------------------------
 Copyright (c) 2021 - 2023 Hugo Cruz - hugo.m.cruz@gmail.com
 
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
import hashlib

from onedrive import onedrive_simple_sdk
from image_processing import process_image
from datetime import timezone
from video_processing import video_creation_datetime
from urllib.request import urlopen


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

def read_configuration(base_url):
    response = urlopen(base_url + "/config.json")
    data = json.load(response)
    return data


def read_credentials(base_url, filename):
    response = urlopen(base_url + "/" + filename)
    data = json.load(response)
    return data



#
# Compare file in Onedrive with local file using HASH256 and SIZE
#
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

        # Hash calculation in chuncks, as large files will exceed memory limits in small instances.
        with open(local_file, "rb") as f:
            file_hash = hashlib.sha256()
            while chunk := f.read(8192):
                file_hash.update(chunk)
            local_file_hash = file_hash.hexdigest().upper()

        stat = os.stat(local_file)
        local_file_size = stat.st_size
    except FileNotFoundError as ex:
        return {
            "status": False,
            "message": "Local file not found."
        }
    except:
        logging.error("compare_files() %s", sys.exc_info()[0])
        return {
            "status": False,
            "message": sys.exc_info()[0]
        }

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



#
# Parse the filname to determine the pattern type
# This function is only used when the file metadata does not contain a date/time
#
def parse_filename_pattern(filename):
    basename = os.path.splitext(filename)[0]
    filename_components_onedrive = basename.split("_")
    filename_components_dropbox = basename.split(" ")

    ## Most likely a One Dive file
    if(len(filename_components_onedrive) == 3):

        logging.debug("Onedrive - Filename components: %s", filename_components_onedrive)

        try:
            datetime.datetime.strptime(filename_components_onedrive[0], "%Y%m%d")
            datetime.datetime.strptime(filename_components_onedrive[1], "%H%M%S%f")
        
            part_1 = filename_components_onedrive[0]
            part_2 = filename_components_onedrive[1]
            part_3 = filename_components_onedrive[2]


            if(part_3 == "iOS"):
                result = {  "status": True,
                            "error":"",
                            "datestr": part_1,
                            "timestr": part_2
                }
                return result
            else:
                result = {  "status": False,
                        "error": "Format does contain 'iOS'"
                }
        
            return result

        except ValueError:
            result = {  "status": False,
                        "error": "Onedrive: Date components format on filename are invalid"
            }
            return result

    ## Dropbox File Pattern Analysis
    elif(len(filename_components_dropbox) == 2):
        # Dropbox pattern processing here
        logging.debug("Dropbox - Filename components: %s", filename_components_dropbox)

        try:
            dt_obj = datetime.datetime.strptime(basename[0:19], "%Y-%m-%d %H.%M.%S")
            
            #Convert to string

        
            part_1 = dt_obj.strftime("%Y%m%d")
            part_2 = dt_obj.strftime("%H%M%S")

            result = { "status": True,
                        "error":"",
                        "datestr": part_1,
                        "timestr": part_2,
                        "year": part_1[0:4],
                        "month": part_2[4:6]
                        }
            return result
            
        except ValueError:
            result = {  "status": False,
                        "error": "Onedrive: Date components format on filename are invalid"
            }
            return result

    else:
        # File format is invalid both for Dropbox and Onedrive upload formats
        result = {  "status": False,
                    "error": "File format pattern is invalid."
        }
        return result


def new_file_details(original_filename, original_time, offset, subsecond):
    
    date_str = ""
    no_offset_sufix = ""

    # Use 000 as default subsecond when information is not available
    if(subsecond == "" or subsecond == None):
        subsecond = "000"

    if(original_time == ""):
        # The image does not have information on the time. 
        # Let's parse the filname pattern
        components = parse_filename_pattern(original_filename)

        logging.debug("new_file_details(): Components result: %s", components["error"])
        if(components["status"] == True):
            
            year = components["datestr"][0:4]
            month = components["datestr"][4:6]
            
            filename = "p_" + components["datestr"] + "_" + components["timestr"][0:6] + "_" + subsecond + "_lt"
            file_extension = get_extension(original_filename)

            photo_info = PhotoInfo()
            photo_info.filename = filename + "." + file_extension
            photo_info.month = month
            photo_info.year = year
            photo_info.status = "file-naming"

            return photo_info


        else:
            photo_info = PhotoInfo()
            photo_info.filename = original_filename
            photo_info.month = None
            photo_info.year = None
            photo_info.status = "original-name"

    else: 

        if(offset == ""):
            date_str = original_time + "+00:00"
            no_offset_sufix = "_lt"
        else:
            date_str = original_time + offset
        
        
    
        date_time_obj = datetime.datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S%z')
        #pst = pytz.timezone('UTC')
        #date_time_obj = pst.localize(date_time_obj)


        filename = ""
        # Convert timestamps with Offset to UTC
        if(date_time_obj.tzinfo != timezone.utc):
            utc_time = date_time_obj.astimezone(timezone.utc)
            #print("----------------  REPLACING TO UCT -----------------")
            filename = utc_time.strftime("p_%Y%m%d_%H%M%S")
        else:
            filename = date_time_obj.strftime("p_%Y%m%d_%H%M%S")

        photo_info = PhotoInfo()
        photo_info.filename = filename
        photo_info.month = date_time_obj.strftime("%m")
        photo_info.year = date_time_obj.strftime("%Y")
        photo_info.status = "exif-name"

        file_extension = get_extension(original_filename)
        photo_info.filename = filename  + "_" + subsecond + no_offset_sufix + "." + file_extension
    

    return photo_info


def process_image_file(onedrive_origin_client, source_file, onedrive_destination_client, destination_path, config, sequence=0):
    logging.debug("process_image_file(): Image file: %s", source_file)

    ## Data from configuration
    path_screenshot = config["constants"]["screenshot_folder_name"]
    path_image = config["constants"]["images_folder_name"]
    path_video = config["constants"]["videos_folder_name"]
    

    filename = os.path.basename(source_file)
    filename_lower = filename.lower()

    ## Trigger the file download
    onedrive_origin_client.download(source_file,"/tmp")

    image_data = process_image(filename)
  
    processed_data = new_file_details(filename, image_data["originaltime"], image_data["offset"],image_data["originalsubsecond"])
    #print("FILENAME: ", processed_data.filename)
    #print("MONTH: ", processed_data.month)
    #print("YEAR: ", processed_data.year)

    logging.debug("process_image_file(): New filename: %s",processed_data.filename )


    file_year = processed_data.year
    file_month = processed_data.month


    ## When function is called recursively, to generate another name
    # This needs to be improved to avoid the download
    if(sequence > 0 ):
        filename_no_ext = os.path.splitext(processed_data.filename)[0]
        file_ext = get_extension(processed_data.filename)
        processed_data.filename = filename_no_ext + "_" + str(sequence) + "." + file_ext


    ### Rename the file here before uploading
    os.rename(filename, processed_data.filename)


    ### Determine upload path 
    #Upload to another folder
    upload_folder = ""
    if(filename_lower.endswith(".png")):
        upload_folder = destination_path + "/" + path_screenshot
    elif(processed_data.status == "file-naming" or processed_data.status == "original-name"):
        upload_folder = destination_path + "/" + path_screenshot
    else:
        upload_folder = destination_path + "/" + path_image



    if(file_year == None):
        file_year = "0000"

    if(file_month == None):
        file_month = "00"


    full_upload_path = upload_folder + "/" + file_year + "/" + file_month

    logging.debug("process_image_file(): Full upload path: %s", full_upload_path)
    
    result = onedrive_destination_client.upload(processed_data.filename, full_upload_path)
    
    if(result["status"]):
        onedrive_origin_client.delete(source_file)
        logging.debug("process_image_file(): File uploaded successfuly: %s", processed_data.filename)

    elif(result["message"] == "File already exists. Solve conflict by changing upload policy from 'fail' to other."):
        #Check if local file is repeated
        result = compare_files(onedrive_destination_client, full_upload_path + "/" + processed_data.filename, processed_data.filename)
        
        if([result["comparison"]]):
            #File is repeated
            logging.info("process_image_file(): File is repeated. Delete from the source. Maintain existing in target.")
            onedrive_origin_client.delete(source_file)

        else:
            ## Process again to append sequence to the file name
            process_image_file(onedrive_origin_client, source_file, onedrive_destination_client, destination_path, config, sequence + 1)
    else:
        logging.error("process_image_file(): Error on the upload. Original file to remain in place. %s", result["message"])
    
    os.remove(processed_data.filename)


    
#################################################################################################################################
#################################################################################################################################
#################################################################################################################################
#################################################################################################################################

def video_filename(filename):
    date_obj = video_creation_datetime(filename)

    new_filename = filename

    if(date_obj == None):
        return None

    else:
        file_extension = get_extension(filename)
        file_basename = date_obj.strftime("v_%Y%m%d_%H%M%S")
        filename = file_basename + "." + file_extension
        return filename




def process_video_file(onedrive_origin_client, source_file, onedrive_destination_client, destination_path, config):
    logging.debug("process_video_file(): Video file:", source_file)

    ## Data from configuration
    path_video = config["constants"]["videos_folder_name"]
    

    filename = os.path.basename(source_file)
    filename_lower = filename.lower()

    ## Trigger the file download
    ### TODO - Error in the download might not be processed... CHECK THIS
    onedrive_origin_client.download(source_file,"/tmp")

    new_filename = video_filename(filename)
    logging.debug("process_video_file(): New filename: %s", new_filename)

    # Initialize variables
    file_year = "0000"
    file_month = "00"

    if(new_filename == None):
        components = parse_filename_pattern(filename)
        
        if(components["status"] == True):
            file_year = components["datestr"][0:4]
            file_month = components["datestr"][4:6]
            extension = get_extension(filename)
            new_filename = "v_" + components["datestr"] + "_" + components["timestr"][0:6] + "." + extension
        else:
            file_year = "0000"
            file_month = "00"
            new_filename = filename

    else:
        file_year = new_filename[2:6]
        file_month = new_filename[6:8]

    os.rename(filename, new_filename)

    full_upload_path = destination_path + "/" + path_video + "/" + file_year + "/" + file_month

    result = onedrive_destination_client.upload(new_filename, full_upload_path)
 

    if(result["status"]):
        onedrive_origin_client.delete(source_file)
        logging.debug("process_video_file(): File uploaded successfuly: %s", new_filename)

    elif(result["message"] == "File already exists. Solve conflict by changing upload policy from 'fail' to other."):
        #Check if local file is repeated
        result = compare_files(onedrive_destination_client, full_upload_path + "/" + new_filename, new_filename)
        
        if([result["comparison"]]):
            #File is repeated
            logging.info("process_video_file(): File is repeated. Delete from the source. Maintain existing in target.")
   
            onedrive_origin_client.delete(source_file)

    else:
        logging.error("process_video_file(): Error on the upload. Original file to remain in place. %s", result["message"])
    
    os.remove(new_filename)
                    


#################################################################################################################################
#################################################################################################################################
#################################################################################################################################
#################################################################################################################################


#### Process Onde Drive Camera Roll

def process_file(onedrive_origin_client, source_file, onedrive_destination_client, destination_path, config):

    
    timeBefore = time.time()
    filename = os.path.basename(source_file)
    filename_lower = filename.lower()

    logging.info("process_file(): Processing file: %s", filename)

    if(filename_lower.endswith(".heic") or filename_lower.endswith(".png") or filename_lower.endswith(".jpg")):
        process_image_file(onedrive_origin_client, source_file, onedrive_destination_client, destination_path, config)

    elif(filename_lower.endswith(".mp4") or filename_lower.endswith(".mov")):
        process_video_file(onedrive_origin_client, source_file, onedrive_destination_client, destination_path, config)

    else:
        logging.warning("process_file(): Unknown file type: %s", filename)
    




## Recursive function to transvese the folder structure
def process_onedrive_folder(onedrive_origin_client, source_path, onedrive_destination_client, destination_path, config):
    logging.info("process_onedrive_camera_roll(): Starting to process the onedrive files.")
    
    result = onedrive_origin_client.listfiles(source_path)

    if(result["status"]):

        item_list = result["itemlist"]
        
        for item in item_list:
            if(item["type"] == "folder"):
                logging.info("process_onedrive_camera_roll(): Processing folder: %s", item["name"])
                new_path = source_path + "/" +  item["name"]
                process_onedrive_folder(onedrive_origin_client, new_path, onedrive_destination_client, destination_path, config)
                
                ## Folder processing is complete here. And it should be empty. 
                # TODO - Check number of itemts in the folder
                folder_list = onedrive_origin_client.listfiles(new_path)

                if(len(folder_list["itemlist"]) ==0):
                    logging.info("process_onedrive_folder(): The folder is empty. It can be deleted now.")
                    
                    del_result = onedrive_origin_client.delete(new_path)

                    if(del_result["status"] == False):
                        logging.error("process_onedrive_folder(): Error deleting folder: %s", result["message"])

                else:
                    logging.info("process_onedrive_folder(): The folder not empty and can't be removed.")
                    

            elif(item["type"] == "file"):
                process_file(onedrive_origin_client, source_path + "/" + item["name"], onedrive_destination_client, destination_path, config)

    
    else:
        logging.error("Error listing files: %s", result["message"])




######### MAIN FUNCTION ##########
def mainProcessor():
    logging.basicConfig(format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s', level=logging.INFO)


    logging.info("Started processing the Onedrive files...")
    
    
    ### Obtain the base config URL
    base_url = os.environ.get('BASE_CONFIG_URL')
    

    ### Variables for global processing
    destination_credentials_file = ""
    destination_path = ""



    ## Read configuration file
    config = read_configuration(base_url)

    destination_credentials_file = config["destination"]["credentials"]
    destination_path = config["destination"]["path"]
    destination_credentials = read_credentials(base_url, destination_credentials_file)

    origins = config["origins"]

    # Connect to the destination
    destination_client = onedrive_simple_sdk(destination_credentials["clientID"], destination_credentials["clientSecret"], destination_credentials["refreshToken"])
    logging.info("Connected to destination client.")

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
    
        process_onedrive_folder(origin_client, source_path, destination_client, destination_path + profile_destination_folder, config)


    logging.info("Completed processing the Onedrive files.")


##### MAIN PART ######
mainProcessor()


