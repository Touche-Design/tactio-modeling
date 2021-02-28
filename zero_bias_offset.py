import json
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from scipy.stats import linregress
import os


#position_label = ['bl', 'br', 'tl','tr']
position_label = ['all']
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

fig1, (ax0, ax1) = plt.subplots(ncols=2)
fig2, (ax2, ax3) = plt.subplots(ncols=2)

ax0.set_title("Voltage vs. Applied Weight")
ax0.set_xlabel("Weight (g)")
ax0.set_ylabel("Voltage (mV)")
ax1.set_title("Total Residual")

ax2.set_title("Conductance vs. Applied Weight")
ax2.set_xlabel("Weight (g)")
ax2.set_ylabel("Conductance (S)")
ax3.set_title("Linear Regression")
ax3.set_xlabel("Weight (g)")
ax3.set_ylabel("Conductance (S)")

full_pressure_values = {}
full_avg_sensor_values = {}
full_regression_param = {}
single_node = 'node6'
#full_cond_press_regression_param = {}
for node_name in full_data:
    if node_name == node_name:
        pressure_values = []
        avg_sensor_values = []
        std_sensor_values = []
        full_pressure_values_node = {}
        full_avg_sensor_values_node = {}
        center_position_avg_sensor_values_node = {}
        full_regression_param_node = {}
        lamdas_position = {}
        for position in position_label:
            for weight in full_data[node_name][position]:
                current_data = full_data[node_name][position]
                current_data = np.array(current_data[weight])
                current_voltage = current_data
                current_voltage_time_avg = np.average(current_voltage,axis=0)

                averaged_data = np.average(current_voltage_time_avg)
                #pressure_values.append(pressure)
                pressure_values.append(weight)
                avg_sensor_values.append(averaged_data)
                sample_data = np.array(current_data)

            pressure_values_np = np.array(pressure_values)
            avg_sensor_values_np = np.array(avg_sensor_values)

            # linear data scatter plots
            ax0.plot(pressure_values, avg_sensor_values_np, '.', label = node_name)
            ax2.plot(pressure_values, avg_sensor_values_np, '.', label = node_name)

            # regression line plots
            # linear regression
            slope, intercept, r_value, p_value, std_err = linregress(pressure_values_np, avg_sensor_values_np)
            full_regression_param_node[position] = (slope, intercept)
            ax1.plot(pressure_values_np, pressure_values_np * slope + intercept - avg_sensor_values_np, '.', label = node_name)

            # Adds to global quantities
            full_pressure_values_node[position] = pressure_values_np
            full_avg_sensor_values_node[position] = avg_sensor_values_np

            #slope_2, intercept_2, r_value_2, p_value_2, std_err_2 = linregress(avg_sensor_values_np,pressure_values_np)
            #full_cond_press_regression_param[node_name] = (slope_2, intercept_2)

        # Adds to global quantities
        full_avg_sensor_values[node_name] = full_avg_sensor_values_node
        full_pressure_values[node_name] = full_pressure_values_node
        full_regression_param[node_name] = full_regression_param_node


print(full_avg_sensor_values)
ratio = []
node_value_min = []
node_value_max = []
for node in full_avg_sensor_values:

    ratio.append(np.min(full_avg_sensor_values[node]['all'])/np.max(full_avg_sensor_values[node]['all']))

print(100*np.average(ratio))
