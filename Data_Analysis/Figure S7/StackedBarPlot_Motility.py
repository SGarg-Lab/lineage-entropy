"""
StackedBarPlot_Motility.py analyzes the proportion of lineage with different sizes across different motility group
"""
import pickle
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

__author__ = 'Tee Udomlumleart'
__maintainer__ = 'Tee Udomlumleart'
__email__ = ['teeu@mit.edu', 'salilg@mit.edu']
__status__ = 'Production'


def euclidean_distance(coor_1, coor_2):
    return math.sqrt(sum((i - j) ** 2 for i, j in zip(coor_1, coor_2)))


def vector_size(x_displacement, y_displacement):
    return math.sqrt(x_displacement ** 2 + y_displacement ** 2)

# normalizing the reads
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

top_right_coord = (1, 1)
top_left_coord = (0, 1)
bottom_left_coord = (0, 0)

triangle_vertices = np.array([top_right_coord, top_left_coord, bottom_left_coord])

j = 0
for barcode, row in true_number_table.iterrows():
    barcode_dict = {}

    barcode_dict['d0_all'], barcode_dict['d0_s1'], barcode_dict['d0_s2'], barcode_dict['d0_s3'] = row[0:4]
    barcode_dict['d6_all'], barcode_dict['d6_s1'], barcode_dict['d6_s2'], barcode_dict['d6_s3'] = row[4:8]
    barcode_dict['d12_all'], barcode_dict['d12_s1'], barcode_dict['d12_s2'], barcode_dict['d12_s3'] = row[20:24]
    barcode_dict['d18_all'], barcode_dict['d18_s1'], barcode_dict['d18_s2'], barcode_dict['d18_s3'] = row[32:36]
    barcode_dict['d24_all'], barcode_dict['d24_s1'], barcode_dict['d24_s2'], barcode_dict['d24_s3'] = row[36:40]

    barcode_summary = {'ternary_coord': [], 'cartesian_coord': [], 'vector': [], 'size': [], 'assigned_state': [],
                       'total_transition_amount': 0}

    barcode_size = [sum(row[1:4]), sum(row[5:8]), sum(row[21:24]), sum(row[33:36]), sum(row[37:40])]

    for timepoint in timepoints:
        timepoint_all_present = all(barcode_size)
        timepoint_total = sum([barcode_dict[timepoint + '_' + state] for state in states])
        if timepoint_total:
            ternary_coord = []
            dist = []
            for state in states:
                ternary_coord.append(barcode_dict[timepoint + '_' + state] / timepoint_total)
            barcode_summary['ternary_coord'].append(ternary_coord)

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
        cells = true_number_table.iloc[j, :]
        barcode_summary['s1_cells'] = (cells[1] + cells[5] + cells[21] + cells[33] + cells[37]) / 5
        barcode_summary['s2_cells'] = (cells[2] + cells[6] + cells[22] + cells[34] + cells[38]) / 5
        barcode_summary['s3_cells'] = (cells[3] + cells[7] + cells[23] + cells[35] + cells[39]) / 5
        all_barcode_list.append(barcode_summary)

    j += 1

all_barcode_list.sort(reverse=True, key=lambda barcode: barcode['total_transition_amount'])

states = ['s1', 's2', 's3']
for state in states:  # iterate through different state
    motility_group = [
        all_barcode_list[round(j * 20 / 100 * len(all_barcode_list)):round((j + 1) * 20 / 100 * len(all_barcode_list))]
        for j in range(5)]  # split lineages into different groups based on their motility (total transition)
    motility_size_group = [[] for i in range(5)]

    # only select the number of cells in the state you are interested in
    for index, group in enumerate(motility_group):
        for barcode in group:
            motility_size_group[index].append(barcode['{}_cells'.format(state)])

    # define bins for the stacked bar plot
    bins = [5 * (10 ** i) for i in range(0, 6, 1)]

    # making the histogram
    histogram_group = [np.histogram(group, bins)[0] for group in motility_size_group]
    total_lineage = [0 for i in range(5)]
    for group in histogram_group:
        for i, size in enumerate(group):
            total_lineage[i] += size

    histogram_group_df = pd.DataFrame(histogram_group)
    total = histogram_group_df.sum(axis=0)
    histogram_percentage_df = histogram_group_df / histogram_group_df.sum(axis=0)

    # define the color
    rainbow = cm.get_cmap('rainbow_r', 5)
    rainbow_list = rainbow(range(5))

    bar_width = 0.85
    names = [i for i in range(0, 5)]
    x = [i for i in range(len(names))]

    # make the stacked bar plot
    for i in range(5):
        if i == 0:
            plt.bar(x, histogram_percentage_df.iloc[i, :], color=rainbow_list[i], width=bar_width)
        else:
            plt.bar(x, histogram_percentage_df.iloc[i, :], bottom=histogram_percentage_df.iloc[0:i, :].sum(axis=0),
                    color=rainbow_list[i], width=bar_width)

    plt.ylim(0, 1)
    plt.xticks(x, names)
    plt.title('Average {} Population Size'.format(state))
    plt.xlabel('Log Average Population Size')
    plt.ylabel('Proportion of Cells')

    # plt.savefig("StackedBarPlot_Motility_{}.svg".format(state), bbox_inches=0, format='svg', dpi=720)
    # plt.close()