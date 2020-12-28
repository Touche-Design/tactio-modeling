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

full_pressure_values = {}
full_avg_sensor_values = {}
full_regression_param = {}
full_cond_press_regression_param = {}
fig1, (ax0, ax1, ax2) = plt.subplots(ncols=3)
#fig2, (ax2, ax3) = plt.subplots(ncols=2,sharey=True)
ax0.set_title("Conductance vs. Applied Pressure")
ax0.set_xlabel("Applied Pressure (kPa)")
ax0.set_ylabel("Conductance (S)")
ax2.set_title("Total Residual")

#ax2.set_title("Conductance vs. Applied Pressure")
ax1.set_xlabel("Applied Pressure (kPa)")
#ax2.set_ylabel("Conductance (S)")
ax1.set_title("Regression")
ax2.set_xlabel("Applied Pressure (kPa)")
#ax3.set_ylabel("Conductance (S)")

for node_name in full_data:
    pressure_values = []
    avg_sensor_values = []
    max_sensor_values = []
    std_sensor_values = []
    full_pressure_values_node = {}
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
            
            # 0.125 in -> 0.003175 m
            # looking at 4 points so area is 4x
            area = 0.003175**2 * 4
            # weight in grams
            force = (weight/1000)*9.81

            #In KPa
            pressure = force / area / 1000

            averaged_data = np.average(time_avg_center_sample)
            pressure_values.append(pressure)
            avg_sensor_values.append(averaged_data)
            sample_data = np.array(current_data)

            #print(np.var(sample_data[:,1,1]))
            #std_sensor_values.append(np.var(sample_data[:,1,1]))
            #print(std_sensor_values.append(np.var(sample_data[:,1,1])))

        # Adds to global quantities
        full_pressure_values_node[position] = pressure_values
        full_pressure_values[node_name] = np.array(pressure_values)
        full_avg_sensor_values_node[position] = avg_sensor_values
        full_max_sensor_values_node[position] = max_sensor_values
    
    ax0.plot(pressure_values, avg_sensor_values, '.', label = node_name)
    #ax2.plot(pressure_values, avg_sensor_values, '.', label = node_name)
    pressure_values = np.array(pressure_values)
    slope, intercept, r_value, p_value, std_err = linregress(pressure_values, avg_sensor_values)
    full_regression_param[node_name] = (slope, intercept)
    ax2.plot(pressure_values, pressure_values * slope + intercept - avg_sensor_values, '.', label = node_name)

    slope_2, intercept_2, r_value_2, p_value_2, std_err_2 = linregress(avg_sensor_values,pressure_values)

    full_cond_press_regression_param[node_name] = (slope_2, intercept_2)

#ax2.set_prop_cycle(None)
max_offset = 0
min_offset = 999
max_slope_regression = 0
min_slope_regression = 999
average_slope_holder = 0
average_offset_holder = 0

for node_name in full_regression_param:
    current_slope = full_regression_param[node_name][0] 
    current_offset = full_regression_param[node_name][1]
    ax1.plot(full_pressure_values[node_name], full_pressure_values[node_name] * current_slope + current_offset,'-', label = node_name + " regression")

    average_slope_holder = average_slope_holder+ current_slope
    average_offset_holder = average_offset_holder+current_offset

    if current_slope > max_slope_regression:
        max_slope_regression = current_slope
    
    if current_slope < min_slope_regression:
        min_slope_regression = current_slope

    if current_offset > max_offset:
        max_offset = current_offset
    
    if current_offset < min_offset:
        min_offset = current_offset

ax0.legend()
ax2.legend()

average_slope_holder = average_slope_holder/len(nodes)
average_offset_holder = average_offset_holder/len(nodes)

pressure_values = np.arange(start=0, stop=250, step=1)
max_regression = pressure_values*max_slope_regression + max_offset
min_regression = pressure_values*min_slope_regression + min_offset
ave_regression = pressure_values*average_slope_holder + average_offset_holder
ax1.plot(pressure_values, max_regression,'--',color='black',alpha=0.5)
ax1.plot(pressure_values, min_regression,'--',color='black',alpha=0.5)
ax1.fill_between(pressure_values, max_regression, min_regression,color='black',alpha=0.1)
ax1.plot(pressure_values,ave_regression,'-.',color='black',label='average regression')
ax1.legend()
print(full_cond_press_regression_param)
plt.show()