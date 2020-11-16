import json
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from scipy.stats import linregress
import os



position_label = ['bl', 'br', 'tl','tr']
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

    for position in position_label:
        position_data = {}
        postions_files_present = [x for x in node_files if x.endswith(position)]
        for node_file in postions_files_present:
            file = open(file_path+"/"+node+"/"+node_file,'r')
            data = json.load(file)
            file.close()
            node_number = node[4:]
            focusData = data[node_number]
            weight = node_file.split("_")[1]
            position = node_file.split("_")[2]
            position_data[int(weight)] = focusData
        node_data[position] = position_data
    
    full_data[node] = node_data


voltage = 3300
r2 = 390

full_weight_values = {}
full_avg_sensor_values = {}
full_regression_param = {}

for node_name in full_data:
    weight_values = []
    avg_sensor_values = []
    max_sensor_values = []
    std_sensor_values = []
    full_weight_values_node = {}
    full_avg_sensor_values_node = {}
    center_position_avg_sensor_values_node = {}
    full_max_sensor_values_node = {}
    for position in position_label:
        for weight in full_data[node_name][position]:

            current_data = full_data[node_name][position]
            current_data = np.array(current_data[weight])
            current_conductance = current_data/(r2*voltage  - r2 * current_data)
            current_conductance_time_avg = np.average(current_conductance,axis=0)

            # Samples the center 4 elements 
            time_avg_center_sample = np.zeros((2,2))
            time_avg_center_sample[0][0] = current_conductance_time_avg[1][1]
            time_avg_center_sample[0][1] = current_conductance_time_avg[1][2]
            time_avg_center_sample[1][0] = current_conductance_time_avg[2][1]
            time_avg_center_sample[1][1] = current_conductance_time_avg[2][2]

            averaged_data = np.average(time_avg_center_sample)
            weight_values.append(weight)
            avg_sensor_values.append(averaged_data)
            sample_data = np.array(current_data)

            #print(np.var(sample_data[:,1,1]))
            #std_sensor_values.append(np.var(sample_data[:,1,1]))
            #print(std_sensor_values.append(np.var(sample_data[:,1,1])))


        # Adds to global quantities
        full_weight_values_node[position] = weight_values
        full_avg_sensor_values_node[position] = avg_sensor_values
        full_max_sensor_values_node[position] = max_sensor_values

    full_weight_values[node_name] = full_weight_values_node
    full_avg_sensor_values_node[position] = avg_sensor_values

    plt.subplot(1,2,1)
    plt.plot(weight_values, avg_sensor_values, '.', label = node_name)
    weight_values = np.array(weight_values)
    slope, intercept, r_value, p_value, std_err = linregress(weight_values, avg_sensor_values)

    full_regression_param[node_name] = (slope, intercept)

    plt.plot(weight_values, weight_values * slope + intercept,'-', label = node_name + " regression")
    plt.title(node_name + "Regression")
    plt.xlabel("Applied Weight (g)")
    plt.ylabel("Conductance (S)")
    plt.legend()
    plt.subplot(1,2,2)
    plt.plot(weight_values, weight_values * slope + intercept - avg_sensor_values, '.', label = node_name)
    plt.legend()
    plt.title(node_name + " Residual")
print(full_regression_param)
plt.show()