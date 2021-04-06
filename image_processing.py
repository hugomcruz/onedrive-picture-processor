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

import exifread
import io
import json
import logging
from PIL import Image

def pretty_print(obj):
    #Pretty print
    json_formatted_str = json.dumps(obj, indent=2)
    print(json_formatted_str)

def process_image(filename):
    # Open image file for reading (binary mode)
    file_name_lower = filename.lower()
    
    tag_list = dict()

    original_time = ""
    original_time_offset = ""
    


    if(file_name_lower.endswith(".heic") or file_name_lower.endswith(".jpg")):

        f = open(filename, 'rb')
        
        # Return Exif tags
        tags = exifread.process_file(f)

        f.close()
     
        #print("Latitude:", tags["GPS GPSLongitude"])
        latitude = get_key_value("GPS GPSLatitude", tags)
        longitude = get_key_value("GPS GPSLongitude", tags)
        original_time = get_key_value("EXIF DateTimeOriginal", tags)
        original_milliseconds = get_key_value("EXIF SubSecTimeOriginal", tags)

        original_time_offset = get_key_value("EXIF OffsetTimeOriginal", tags)
        logging.debug("Latitude     : %s",latitude)
        logging.debug("Longitude:   : %s", longitude)
        logging.debug("Original time: %s", original_time)
        logging.debug("Original time millis: %s", original_milliseconds)
        
        logging.debug("Time Offset  : %s",original_time_offset)

    
    elif(file_name_lower.endswith(".png")):
        
        try:
            image = Image.open(filename)
            image.verify()
            result = image._getexif()
            
            #print(result)
            #original_time = result[36867]
            #original_milliseconds = result[37521]
            
            original_time = get_key_value(36867,result)
            original_milliseconds = get_key_value(37521,result)

        except:
            logging.debug("Original Time: NO DATA")
            original_time = ""
            original_milliseconds = ""
            original_time_offset = ""

    

    result = {  "originaltime": str(original_time), 
                "offset": str(original_time_offset),
                "originalsubsecond": str(original_milliseconds)
                  }

    return result




def get_exif(filename):
    image = Image.open(filename)
    image.verify()
    return image._getexif()



def get_key_value(key, tags):
    try:
        value = tags[key]
        return value
    except KeyError:
        return ""






#result = process_image("/Users/hcruz/Downloads/2015-09-06 21.14.19.mov")
#pretty_print(result)