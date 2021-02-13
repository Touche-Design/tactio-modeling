import json
import numpy as np
from scipy.signal import sosfilt, lfilter
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

import os

position_label = ['all']
file_path = 'bump'
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
node_id = 'node11'
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
node_number_id = '12'

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
    if(index < np.shape(processed_data)[0]):
        im1.set_data(grab_original_frame())
        im2.set_data(grab_processed_frame())
        index+=1
    else:
        return




current_data = np.array(full_data)

current_data = current_data*(255.0/np.amax(current_data))
#processed_data = current_data.astype(np.uint8)
processed_data = current_data

filter_coeff_SOS = np.array([
    [1, -2, 1, 1, -0.108988232441268,  0.811038079887577    ],
    [1, -2, 1, 1, -0.0919861826501431,0.528518041547985  ],
    [1, -2, 1, 1, -0.0802884776169996,0.334139356915846  ],
    [1, -2, 1, 1, -0.0721618020570055,0.199099834094223  ],
    [1, -2, 1, 1, -0.0665873204363481,0.106469664171206  ],
    [1, -2, 1, 1, -0.0629533999745092,0.0460854539839319 ],
    [1, -2, 1, 1, -0.0608993596534685,0.0119538311866368 ],
    [1, -1, 0, 1, -0.0301172823212969,0]])

#processed_data = sosfilt(filter_coeff_SOS, current_data, axis=0)

press_strength_thresh = 1.4

zero_data =current_data[0,...]
zero_data = np.repeat(zero_data[np.newaxis, :, :],np.shape(processed_data)[0], axis=0)
processed_data = np.where(processed_data - zero_data <= 0, 0.00001, processed_data - zero_data)

processed_data = np.log(np.power(processed_data, 2))
processed_data = np.where(processed_data > press_strength_thresh, 1.0, 0)

press_time = 4 # samples
press_time_thresh = 1/press_time
processed_data = lfilter(np.ones((press_time,)), 1, processed_data, axis=0)
processed_data = np.where(processed_data > press_time_thresh, 1.0, 0)


im1 = ax1.imshow(grab_original_frame())
im2 = ax2.imshow(grab_processed_frame(), cmap = 'gray', vmin = 0, vmax = 1)
ani = FuncAnimation(plt.gcf(), update, interval=50)

#ani.save('animation.mp4', fps=20)

#ax1.plot(current_data[:, 1, 1])
#ax2.plot(processed_data[:, 1, 1])

#print(np.shape(current_data))
#print(np.shape(processed_data))
plt.show()
