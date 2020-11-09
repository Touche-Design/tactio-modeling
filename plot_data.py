import json
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import os


file_path = 'cal_data'
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

full_data = {}
# Data organization
for node in nodes:
    node_data = {}
    node_files = []
    for file in files_present:
        file_name_split = file.split("_")
        if(node == file_name_split[0]):
            node_files.append(file)
    
    for node_file in node_files:
        file = open(file_path+"/"+node+"/"+node_file,'r')
        data = json.load(file)
        file.close()
        focusData = data["0"] #TODO Make the node address
        weight = node_file.split("_")[1][:-1]
        node_data[int(weight)] = focusData
    
    full_data[node] = node_data

# Data processing

full_weight_values = {}
full_avg_sensor_values = {}
full_max_sensor_values = {}
# Per node
for node_name in full_data:
    print(node_name)
    weight_values = []
    avg_sensor_values = []
    max_sensor_values = []
    for weight in full_data[node_name]:
        current_data = full_data[node_name][weight]
        averaged_data = np.average(np.average(current_data,axis=0))
        max_data = np.max(current_data)
        weight_values.append(weight)
        avg_sensor_values.append(averaged_data)
        max_sensor_values.append(max_data)


    # Adds to global quantities
    full_weight_values[node_name] = weight_values
    full_avg_sensor_values[node_name] = avg_sensor_values
    full_max_sensor_values[node_name] = max_sensor_values

    # fig, (ax0, ax1, ax2) = plt.subplots(nrows=3)
    # fig.suptitle(node_name + " Data Collection", fontsize=16)

    # ax0.plot(weight_values,avg_sensor_values, "ro")
    # ax0.set_title('Average Sensor Value vs Weight')
    # ax0.set_ylabel('Sensor Value (mV)')
    # ax0.set_xlabel('Weight (g)')
    
    # ax1.plot(weight_values,max_sensor_values, "ro")
    # ax1.set_title('Max Sensor Value vs Weight')
    # ax1.set_ylabel('Sensor Value (mV)')
    # ax1.set_xlabel('Weight (g)')
    
    # ax2.loglog(weight_values,avg_sensor_values, "ro")
    # ax2.set_title('Log Log Max Sensor Value vs Weight')
    # ax2.set_ylabel('log(Sensor Value) (mV)')
    # ax2.set_xlabel('log(Weight) (g)')
    
    # #Fix vertical spacing
    # plt.subplots_adjust(hspace=1)
    # plt.show()

# All nodes
fig, (ax0, ax1, ax2) = plt.subplots(nrows=3)
fig.suptitle(" Total Data Collection", fontsize=16)
print(full_weight_values)
for node_name in nodes:
    ax0.scatter(full_weight_values[str(node_name)],full_avg_sensor_values[str(node_name)], marker='o', label=str(node_name))
    ax0.set_ylabel('Sensor Value (mV)')
    ax0.set_xlabel('Weight (g)')
    ax0.set_title('Average Sensor Value vs Weight')

    ax1.scatter(full_weight_values[str(node_name)],full_max_sensor_values[str(node_name)], marker='o', label=str(node_name))
    ax1.set_title('Max Sensor Value vs Weight')
    ax1.set_ylabel('Sensor Value (mV)')
    ax1.set_xlabel('Weight (g)')

    ax2.scatter(full_weight_values[str(node_name)],full_avg_sensor_values[str(node_name)], marker='o', label=str(node_name))
    ax2.set_title('Log Log Max Sensor Value vs Weight')
    ax2.set_ylabel('log(Sensor Value) (mV)')
    ax2.set_xlabel('log(Weight) (g)')
    ax2.set_yscale('log')
    ax2.set_xscale('log')

plt.legend(loc='upper left')
plt.subplots_adjust(hspace=0.75)
plt.show()


