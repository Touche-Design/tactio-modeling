import json
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

import os

position_label = ['all']
file_path = 'line_detection'
files_present = []
nodes = []
for root, dirs, files in os.walk(file_path):
    if len(dirs) > 0:
        nodes.extend(dirs)
    
    if len(files) > 0:
        files_present.extend(files)

#Filters only node files and directories
nodes = [x for x in nodes if x.startswith('node')]
files_present = [x for x in files_present if x.startswith('node')]
node_id = 'node18'
full_data = []
processed_data = []
# Data organization
for node in nodes:
    node_files = []
    for file in files_present:
        file_name_split = file.split("_")
        if(node == file_name_split[0]):
            node_files.append(file)

    for position in position_label:
        position_data = {}
        postions_files_present = [x for x in node_files if x.endswith(position)]
        for node_file in postions_files_present:
            file = open(file_path+"/"+node+"/"+node_file,'r')
            data = json.load(file)
            file.close()
            node_number = node[4:]
            full_data = data[node_number]
# Data processing
# Per node
node_number_id = '18'

fig,(ax1, ax2) = plt.subplots(1,2)

index = 0

def grab_processed_frame():
    frame = processed_data[index]
    return frame

def grab_original_frame():
    frame = current_data[index]
    return frame

def update(i):
    global index
    im1.set_data(grab_original_frame())
    im2.set_data(grab_processed_frame())
    index+=1




current_data = np.array(full_data)

current_data = current_data*(255.0/np.amax(current_data))
processed_data = current_data.astype(np.uint8)

for frame_index in range(np.shape(processed_data)[0]):
    frame = processed_data[frame_index]
    ret,thresh1 = cv2.threshold(frame,1,255,cv2.THRESH_TOZERO)
    laplacian = cv2.Laplacian(thresh1,cv2.CV_64F)
    processed_data[frame_index] = laplacian

im1 = ax1.imshow(grab_original_frame())
im2 = ax2.imshow(grab_processed_frame())

ani = FuncAnimation(plt.gcf(), update, interval=5)
plt.show()
