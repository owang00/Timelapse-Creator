#!/usr/bin/python
import os, os.path, sys
import math, subprocess

from EagleEye import *

een = EagleEye()

# Login credentials
USERNAME = "owang+hq@een.com"
PASSWORD = "wRKMCLCCm6Hxns5"

if USERNAME == "" or PASSWORD == "":
    print("Update script with your credentials")
    sys.exit()

# which camera are we accessing
CAMERA_ESN = sys.argv[1]
if CAMERA_ESN == "":
    print("Update script with the camera's ESN")
    sys.exit()

# what time range are we looking for
START_TIME = sys.argv[3]
END_TIME =   sys.argv[4]

if START_TIME == "" or END_TIME == "":
    print("Update script with a start and end time")
    sys.exit()

# total length of the video in seconds
VIDEO_LENGTH = int (sys.argv[2])


een.login(username=USERNAME, password=PASSWORD) 

this_camera = een.find_by_esn(CAMERA_ESN) 

this_camera.get_preview_list(instance=een, start_timestamp=START_TIME, end_timestamp=END_TIME, asset_class="pre") 

# Figure out how to get to the desired video length assuming input at 10 FPS.
# Get the total number of images devides by the desired video length in seconds.
# The result is how man images we need to skip in order to represent the time period.
number_of_previews = len(this_camera.previews)
# print("Number of Previews:", number_of_previews)
# print("VIDEO_LENGTH", VIDEO_LENGTH)
steps = number_of_previews / VIDEO_LENGTH


# print(f"Total images: {number_of_previews} \n" )
# print(f"Length of video: {VIDEO_LENGTH} \n" )
# print(f"Steps: {steps} \n" )

# check if there are less images that needed for video_length
input_fps = 10

if steps <= 1:
    # less than target fps, lower fps
    scale_factor = VIDEO_LENGTH / number_of_previews
    print(f"Scale Factor: {scale_factor}" )
    
    fps_steps = math.ceil(input_fps / scale_factor)
    print(f"FPS steps: {fps_steps}" )
    
    input_fps = fps_steps
    steps = math.ceil( steps )

else:
    steps = math.floor( steps )


# Only download the images that are going to be used.
for pre in sorted(this_camera.previews)[0::steps]:
    if os.path.isfile(f"/tmp/{this_camera.camera_id}-{pre}.jpg") == False:
        print(" Reached here 2 ")
        local_filename = f"/tmp/{this_camera.camera_id}-{pre}.jpg"
        img = this_camera.download_image(instance=een, timestamp=pre, asset_class="pre")
        print(local_filename)
        if img:
            print(" Reached here 3 ")
            try:
                open(local_filename, 'wb').write(img)
            except Exception as err:
                print("Caught an exception: ", err)
        else: 
            print("Reached here 4")
            print(f"{local_filename} failed")
    else:
        # file has already been downloaded
        print( f"File already exists, skipping: tmp/{this_camera.camera_id}-{pre}.jpg" )


# Let's go ahead and call ffmpeg to make the images into a movie
# Assumes that you've got ffmpeg installed or are using the included Docker container

print( f"Total images: {number_of_previews}" )
print( f"Length of video: {VIDEO_LENGTH}" )
print( f"Steps: {steps}" )
print( f"input_fps: {input_fps}" )

# Moves all the files into a folder for FFMPEG
# try:
#     os.system('find /tmp/systemd-private-0e7e02ff5c8e4a4ea749ce436adec0b5-apache2.service-PsTF3U/tmp -type f -print0 | xargs -0 mv -t /home/oliver/var/www/html/Project1')
# except Exception as err:
#     print("It didn't move :(", err)

subprocess.run(["ffmpeg", "-framerate", str(input_fps), "-pattern_type", "glob", "-i", f"/tmp/{CAMERA_ESN}-*.jpg", "-y", "-r", "30", "-pix_fmt", "yuv420p", f"/home/oliver/var/www/html/Project1/tmp/video.mp4"])