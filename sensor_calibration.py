import json
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from scipy.stats import linregress
import os
from NumpyArrayEncoder import NumpyArrayEncoder
import json

#######################################################################################################################################
#Data Acquisition from Directories

position_label = 'all'
file_path = {'model':'cal_data','test':'cal_test'}
files_present = {'model':[],'test':[]}
nodes = {'model':[],'test':[]}

#Finds files in data and test directories
for data_type in file_path:
    for root, dirs, files in os.walk(file_path[data_type]):
        if len(dirs) > 0:
            nodes[data_type].extend(dirs)
    
        if len(files) > 0:
            files_present[data_type].extend(files)

    #Filters only 'node' and 'all' files and directories
    nodes[data_type] = [x for x in nodes[data_type] if x.startswith('node')]
    files_present[data_type] = [x for x in files_present[data_type] if (x.startswith('node') & x.endswith(position_label))]

full_data = {}
# Data organization
for data_type in ['model','test']:
    full_data[data_type] = {}
    for node in nodes[data_type]:
        node_files = []
        for file in files_present[data_type]:
            file_name_split = file.split("_")
            if(node == file_name_split[0]):
                node_files.append(file)

        node_data = {}
        for node_file in node_files:
            file = open(file_path[data_type]+"/"+node+"/"+node_file,'r')
            data = json.load(file)
            file.close()
            node_number = node[4:]
            focusData = data[node_number]
            weight = node_file.split("_")[1]
            position = node_file.split("_")[2]
            node_data[int(weight)] = focusData

        full_data[data_type][node] = node_data

#######################################################################################################################################
#Sampling and Scaling

voltage = 3300
r2 = 390
full_pressure_values = {}
full_avg_sensor_values = {}
scaled_data = {'model':{},'test':{}}
for data_type in ['model','test']:
    for node_name in full_data[data_type]:
        scaled_data[data_type][node_name] = {'weight':[],'avg_sense_vals':[]}
        pressure_values = []
        avg_sensor_values = []
        full_pressure_values_node = {}
        full_avg_sensor_values_node = {}
        center_position_avg_sensor_values_node = {}
        full_regression_param_node = {}
        for weight in full_data[data_type][node_name]:
            current_data = full_data[data_type][node_name]
            current_data = np.array(current_data[weight])
            current_conductance = current_data/(r2*voltage  - r2 * current_data)
            current_conductance_time_avg = np.average(current_conductance,axis=0)
            averaged_data = np.average(current_conductance_time_avg)
            scaled_data[data_type][node_name]['weight'].append(weight)
            scaled_data[data_type][node_name]['avg_sense_vals'].append(averaged_data)
        
        scaled_data[data_type][node_name]['weight'] = np.array(scaled_data[data_type][node_name]['weight'])
        scaled_data[data_type][node_name]['avg_sense_vals'] = np.array(scaled_data[data_type][node_name]['avg_sense_vals'])

#######################################################################################################################################
#Model Building and Plotting

fig1, (ax0, ax1) = plt.subplots(ncols=2)
fig2, (ax2, ax3) = plt.subplots(ncols=2)

ax0.set_title("Conductance vs. Applied Weight")
ax0.set_xlabel("Weight (g)")
ax0.set_ylabel("Conductance (S)")
ax1.set_title("Total Residual")
ax1.set_xlabel("Weight (g)")
ax1.set_ylabel("Conductance (S)")

ax2.set_title("Conductance vs. Applied Weight")
ax2.set_xlabel("Weight (g)")
ax2.set_ylabel("Conductance (S)")
ax3.set_title("Linear Regression")
ax3.set_xlabel("Weight (g)")
ax3.set_ylabel("Conductance (S)")

full_regression_param = {}
for node_name in scaled_data['model']:
    weight = scaled_data['model'][node_name]['weight']
    avg_sense_vals = scaled_data['model'][node_name]['avg_sense_vals']

    # linear data scatter plots
    ax0.plot(weight, avg_sense_vals, '.', label = node_name)
    ax2.plot(weight, avg_sense_vals, '.', label = node_name)
                    
    # linear regression
    slope, intercept, r_value, p_value, std_err = linregress(weight, avg_sense_vals)
    full_regression_param_node = (slope, intercept)
    # residuals
    ax1.plot(weight, weight * slope + intercept - avg_sense_vals, '.', label = node_name)

    # Adds to global quantities
    full_regression_param[node_name] = full_regression_param_node

ax2.set_prop_cycle(None)
max_offset = 0
min_offset = 999
max_slope_regression = 0
min_slope_regression = 999
slope_sum = 0
offset_sum = 0

for node_name in full_regression_param:
    current_slope = full_regression_param[node_name][0] 
    current_offset = full_regression_param[node_name][1]
    weight = scaled_data['model'][node_name]['weight']
    ax3.plot(weight, weight * current_slope + current_offset,'.', label = node_name + " regression")

    slope_sum = slope_sum + current_slope
    offset_sum = offset_sum + offset_sum

    if current_slope > max_slope_regression:
        max_slope_regression = current_slope
    
    if current_slope < min_slope_regression:
        min_slope_regression = current_slope

    if current_offset > max_offset:
        max_offset = current_offset
    
    if current_offset < min_offset:
        min_offset = current_offset

average_slope = slope_sum/len(nodes['model'])
average_offset = offset_sum/len(nodes['model'])

pressure_values = np.arange(start=0, stop=4000, step=1)
max_regression = pressure_values*max_slope_regression + max_offset
min_regression = pressure_values*min_slope_regression + min_offset
ave_regression = pressure_values*average_slope + average_offset
#print("avg slope:",average_slope)
#print("avg offset:",average_offset)
ax3.plot(pressure_values, max_regression,'--',color='black',alpha=0.5)
ax3.plot(pressure_values, min_regression,'--',color='black',alpha=0.5)
ax3.fill_between(pressure_values, max_regression, min_regression,color='black',alpha=0.1)
ax3.plot(pressure_values,ave_regression,'-.',color='black',label='average regression')
ax2.legend()
ax3.legend()

#######################################################################################################################################
#Linear regression of test data + correction model

full_regression_param = {}
for node_name in scaled_data['test']:
    weight = scaled_data['test'][node_name]['weight']
    avg_sense_vals = scaled_data['test'][node_name]['avg_sense_vals']
                    
    # linear regression
    slope, intercept, r_value, p_value, std_err = linregress(weight, avg_sense_vals)
    full_regression_param_node = (slope, intercept)

    # Adds to global quantities
    full_regression_param[node_name] = full_regression_param_node

#######################################################################################################################################
#outputs file of corrected regression parameters for nodes based on test data

export_param = {}
for node_name in full_regression_param:
    slope = average_slope/full_regression_param[node_name][0]
    intercept = average_offset - full_regression_param[node_name][1]*average_slope/full_regression_param[node_name][0]
    export_param[node_name]= (slope,intercept)
save_name = "regression_params.json"
with open(save_name, "w") as outfile:  
    json.dump(export_param, outfile, cls=NumpyArrayEncoder)

#######################################################################################################################################
#plots average line and original vs shifted data per node

fig3, ax = plt.subplots(ncols=len(export_param))

i = 0
for node_name in export_param:
    weights = scaled_data['test'][node_name]['weight']
    original_data = scaled_data['test'][node_name]['avg_sense_vals']
    ax[i].plot(weights,original_data,'.',label=node_name+' data')

    slope = export_param[node_name][0]
    intercept = export_param[node_name][1]
    shifted_data =  original_data * slope + intercept

    ax[i].plot(weights,shifted_data,'.',label=node_name+' shifted data')

    ax[i].plot(pressure_values,ave_regression,'-.',color='black',alpha=0.3,label='average regression')
    ax[i].legend()

    ax[i].set_title("Conductance vs. Applied Weight")
    ax[i].set_xlabel("Weight (g)")
    ax[i].set_ylabel("Conductance (S)")
    i = i+1

plt.show()