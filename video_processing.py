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
#sys.path.append('/Users/hcruz/Documents/development/python/ffprobe_hugo')
#sys.path.append('/home/ec2-user/ffprobe_hugo')
#sys.path.append('/root/dev/ffprobe_hugo')


from ffprobe import FFProbe
import datetime

#
# Use FFprobe to determine the video creation date-time
#
def video_creation_datetime(filepath):
    metadata=FFProbe(filepath)

    if("creation_time" not in metadata.metadata.keys()):
        return None

    try:

        dt_obj = datetime.datetime.strptime(metadata.metadata['creation_time'], "%Y-%m-%dT%H:%M:%S.%f%z")
        return dt_obj

    except ValueError as ex:
        logging.error ("video_creation_datetime(): %s", ex)
        return None


#result = video_creation_datetime("/Users/hcruz/Downloads/2015-09-20 16.17.35.mov")
#print(result)
        

#result2 = video_creation_datetime("/Users/hcruz/Downloads/2015-09-06 21.14.19.mov")
#print(result2)