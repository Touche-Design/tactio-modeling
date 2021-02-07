import json
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import os

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

# Data processing

full_weight_values = {}
full_avg_sensor_values = {}
full_max_sensor_values = {}
# Per node
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
            current_data_time_avg = np.average(current_data,axis=0)

            # Samples the center 4 elements 
            time_avg_center_sample = np.zeros((2,2))
            time_avg_center_sample[0][0] = current_data_time_avg[1][1]
            time_avg_center_sample[0][1] = current_data_time_avg[1][2]
            time_avg_center_sample[1][0] = current_data_time_avg[2][1]
            time_avg_center_sample[1][1] = current_data_time_avg[2][2]
    

            averaged_data = np.average(time_avg_center_sample)
            max_data = np.max(current_data)
            weight_values.append(weight)
            avg_sensor_values.append(averaged_data)
            max_sensor_values.append(max_data)
            sample_data = np.array(current_data)


            #print(np.var(sample_data[:,1,1]))
            #std_sensor_values.append(np.var(sample_data[:,1,1]))
            #print(std_sensor_values.append(np.var(sample_data[:,1,1])))


        # Adds to global quantities
        full_weight_values_node[position] = weight_values
        full_avg_sensor_values_node[position] = avg_sensor_values
        full_max_sensor_values_node[position] = max_sensor_values

    center_all_pos_avg_sensor_values_node = {}
    for position in position_label:
        for weight in full_data[node_name][position]:
            print(weight)
            print(full_avg_sensor_values_node[position])
            center_all_pos_avg_sensor_values_node[weight] += full_avg_sensor_values_node[position][weight]
    print(center_all_pos_avg_sensor_values_node)



    full_weight_values[node_name] = full_weight_values_node
    full_avg_sensor_values[node_name] = full_avg_sensor_values_node
    full_max_sensor_values[node_name] = full_max_sensor_values_node

    fig, (ax0, ax1, ax2) = plt.subplots(nrows=3)
    fig.suptitle(node_name + " Data Collection", fontsize=16)
     
    ax0.plot(weight_values,avg_sensor_values, "ro")
    ax0.set_title('Average Sensor Value vs Weight')
    ax0.set_ylabel('Sensor Value (mV)')
    ax0.set_xlabel('Weight (g)')
     
    ax1.plot(weight_values,max_sensor_values, "ro")
    ax1.set_title('Max Sensor Value vs Weight')
    ax1.set_ylabel('Sensor Value (mV)')
    ax1.set_xlabel('Weight (g)')
     
    ax2.loglog(weight_values,avg_sensor_values, "ro")
    ax2.set_title('Log Log Max Sensor Value vs Weight')
    ax2.set_ylabel('log(Sensor Value) (mV)')
    ax2.set_xlabel('log(Weight) (g)')
     
    #Fix vertical spacing
    plt.subplots_adjust(hspace=1)
    plt.show()


#print(np.var(full_std_sensor_values['node20'][np.where(full_std_sensor_values['node20']>0)]))
#print(np.var(full_std_sensor_values['node20res'][np.where(full_std_sensor_values['node20res']>0)]))
#plt.hist(full_std_sensor_values['node20'][np.where(full_std_sensor_values['node20']>0)], bins='auto',label='node20')
#plt.show()
#plt.hist(full_std_sensor_values['node20res'][np.where(full_std_sensor_values['node20res']>0)], bins='auto',label='node20res')
#plt.legend(loc='upper left')
#plt.show()

# All nodes
fig, (ax0, ax1, ax2) = plt.subplots(nrows=3)
ax0.set_ylabel('Sensor Value (mV)')
ax0.set_xlabel('Weight (g)')
ax0.set_title('Average Sensor Value vs Weight')
ax1.set_title('Max Sensor Value vs Weight')
ax1.set_ylabel('Sensor Value (mV)')
ax1.set_xlabel('Weight (g)')
ax2.set_title('Log Log Max Sensor Value vs Weight')
ax2.set_ylabel('log(Sensor Value) (mV)')
ax2.set_xlabel('log(Weight) (g)')
ax2.set_yscale('log')
ax2.set_xscale('log')

fig.suptitle(" Total Data Collection", fontsize=16)
for node_name in nodes:
    node_label = str(node_name)
    for position in position_label:
        ax0.scatter(full_weight_values[str(node_name)][position],full_avg_sensor_values[str(node_name)][position], marker='o', label=node_label)
        ax1.scatter(full_weight_values[str(node_name)][position],full_max_sensor_values[str(node_name)][position], marker='o', label=node_label)
        ax2.scatter(full_weight_values[str(node_name)][position],full_avg_sensor_values[str(node_name)][position], marker='o', label=node_label)


plt.legend(loc='upper left')
plt.subplots_adjust(hspace=0.75)
plt.show()


