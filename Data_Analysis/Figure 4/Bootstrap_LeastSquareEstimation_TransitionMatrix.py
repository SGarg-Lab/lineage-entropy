"""
This file use bootstrapping to find transition matrix using LeastSqaureEstimation
"""

import pickle
import math
import random
import csv
import numpy as np
from numpy.linalg import pinv
from scipy import stats

__author__ = 'Tee Udomlumleart'
__maintainer__ = 'Tee Udomlumleart'
__email__ = ['teeu@mit.edu', 'salilg@mit.edu']
__status__ = 'Production'


def euclidean_distance(coor_1, coor_2):
    return math.sqrt(sum((i - j) ** 2 for i, j in zip(coor_1, coor_2)))


def vector_size(x_displacement, y_displacement):
    return math.sqrt(x_displacement ** 2 + y_displacement ** 2)


# normalize reads
total_cell_number = 10 ** 8

state_1_ratio = 0.90
state_2_ratio = 0.05
state_3_ratio = 0.05

state_1_number = state_1_ratio * total_cell_number
state_2_number = state_2_ratio * total_cell_number
state_3_number = state_3_ratio * total_cell_number

normalizing_factor = [total_cell_number, state_1_number, state_2_number, state_3_number] * 10

table = pickle.load(open('191012_finished_table.pickle', 'rb'))

sum_table = table.sum(axis=0)
normalized_table = table.div(sum_table)
true_number_table = (normalized_table * normalizing_factor).round()

states = ['s1', 's2', 's3']
states_coords = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]

timepoints = ['d0', 'd6', 'd12', 'd18', 'd24']

all_size_set = set()
all_barcode_list = []
all_transition_size_list = []

top_right_coord = (10, 10)
top_left_coord = (0, 10)
bottom_left_coord = (0, 0)

triangle_vertices = np.array([top_right_coord, top_left_coord, bottom_left_coord])

for barcode, row in true_number_table.iterrows():
    barcode_dict = {}

    barcode_dict['d0_all'], barcode_dict['d0_s1'], barcode_dict['d0_s2'], barcode_dict['d0_s3'] = row[0:4]
    barcode_dict['d6_all'], barcode_dict['d6_s1'], barcode_dict['d6_s2'], barcode_dict['d6_s3'] = row[4:8]
    barcode_dict['d12_all'], barcode_dict['d12_s1'], barcode_dict['d12_s2'], barcode_dict['d12_s3'] = row[20:24]
    barcode_dict['d18_all'], barcode_dict['d18_s1'], barcode_dict['d18_s2'], barcode_dict['d18_s3'] = row[32:36]
    barcode_dict['d24_all'], barcode_dict['d24_s1'], barcode_dict['d24_s2'], barcode_dict['d24_s3'] = row[36:40]

    barcode_summary = {'ternary_coord': [], 'cartesian_coord': [], 'vector': [], 'size': [], 'assigned_state': [],
                       'timepoint_size': [], 'total_transition_amount': 0}

    barcode_size = [sum(row[1:4]), sum(row[5:8]), sum(row[21:24]), sum(row[33:36]), sum(row[37:40])]

    for timepoint in timepoints:
        timepoint_all_present = all(barcode_size)
        timepoint_total = sum([barcode_dict[timepoint + '_' + state] for state in states])
        if timepoint_total:
            ternary_coord = []
            timepoint_size = []
            dist = []
            for state in states:
                ternary_coord.append(barcode_dict[timepoint + '_' + state] / timepoint_total)
                timepoint_size.append(barcode_dict[timepoint + '_' + state])
            barcode_summary['ternary_coord'].append(ternary_coord)
            barcode_summary['timepoint_size'].append(timepoint_size)

            cartesian_coord = np.dot(np.array(ternary_coord), triangle_vertices)
            barcode_summary['cartesian_coord'].append(list(cartesian_coord))

            for state_coord in triangle_vertices:
                dist.append(euclidean_distance(cartesian_coord, state_coord))
            barcode_summary['assigned_state'].append(dist.index(min(dist)))

            barcode_summary['size'].append(timepoint_total)

    if len(barcode_summary['cartesian_coord']) == 5:
        for i in range(4):
            vector = (barcode_summary['cartesian_coord'][i + 1][0] - barcode_summary['cartesian_coord'][i][0],
                      barcode_summary['cartesian_coord'][i + 1][1] - barcode_summary['cartesian_coord'][i][1])
            barcode_summary['vector'].append(vector)
            barcode_summary['total_transition_amount'] += vector_size(vector[0], vector[1])
        all_transition_size_list.append(barcode_summary['total_transition_amount'])
        for size in barcode_summary['size']:
            all_size_set.add(round(size, 3))
        all_barcode_list.append(barcode_summary)
all_barcode_list.sort(reverse=True, key=lambda barcode: barcode['total_transition_amount'])

# make a list that contains 9 lists inside
matrix_data_list = [np.empty(0) for i in range(9)]  # store each entry of matrix in a list
bootstrap_sample_number = round(0.8*len(all_barcode_list))  # sample 80% of the total lineages
log_count = 0  # keep track of bootstrap iterations


def least_square_estimation_all_timepoint(all_barcode_list):
    # perform least square estimation to estimate the transition matrix
    T_0 = np.empty((len(all_barcode_list) * 4, 3))
    T_1 = np.empty((len(all_barcode_list) * 4, 3))
    length = 0
    for timepoint in range(4):
        for barcode in all_barcode_list:
            ternary_coord = barcode['ternary_coord']
            T_0[length] = np.array(ternary_coord[timepoint])
            T_1[length] = np.array(ternary_coord[timepoint + 1])
            length += 1
    T_0_t = np.transpose(T_0)
    P = np.matmul(pinv(np.matmul(T_0_t, T_0)), np.matmul(T_0_t, T_1))
    return P


with open('Bootstrap_LSE.csv', mode='w') as csv_file:
    # open a file and csv writer function
    csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    # bootstrap iterate 10^5 times
    for bootstrap_sample_iteration in range(100000):
        # sample 80% of all lineages
        bootstrap_sample = random.choices(all_barcode_list, k=bootstrap_sample_number)
        # calculate transition matrix from those 80% of all lineages
        LSE_result = least_square_estimation_all_timepoint(bootstrap_sample)
        # record each entry in a list in matrix_data_list
        for ir, row in enumerate(LSE_result):
            for ic, entry in enumerate(LSE_result[ir]):
                matrix_data_list[3*ir+ic] = np.append(matrix_data_list[3*ir+ic], entry)
        # every 10**i iterations, record the data
        if bootstrap_sample_iteration % (10 ** log_count) == 0:
            csv_writer.writerow(['Number of bootstrap samples = {}'.format(10**log_count)])
            csv_writer.writerow(['Index', 'Mean', '2.5th Percentile', '97.5th Percentile', 'SEM'])
            log_count += 1
            for index, entry in enumerate(matrix_data_list):
                csv_writer.writerow([str(index), str(entry.mean()), str(np.percentile(entry, 2.5)),
                                     str(np.percentile(entry, 97.5)), str(stats.sem(entry, axis=None, ddof=0))])
            csv_writer.writerow([])

pickle.dump(matrix_data_list, open('Bootstrap_LSE.pickle', 'wb'), protocol=pickle.HIGHEST_PROTOCOL)


