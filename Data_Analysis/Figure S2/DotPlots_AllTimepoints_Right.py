"""
DotPlots_AllTimepoint_Right.py generates a dot plot that shows the proportion of cells in different states across all
timepoints and all lineages
"""

import pickle
import math
import numpy as np
import matplotlib
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

# Normalize the data
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
all_vector_size_set = set()
all_barcode_list = []

top_right_coord = (10, 10)
top_left_coord = (0, 10)
bottom_left_coord = (0, 0)

triangle_vertices = np.array([top_right_coord, top_left_coord, bottom_left_coord])

# iterate through each lineage
for barcode, row in true_number_table.iterrows():
    barcode_dict = {}

    barcode_dict['d0_all'], barcode_dict['d0_s1'], barcode_dict['d0_s2'], barcode_dict['d0_s3'] = row[0:4]
    barcode_dict['d6_all'], barcode_dict['d6_s1'], barcode_dict['d6_s2'], barcode_dict['d6_s3'] = row[4:8]
    barcode_dict['d12_all'], barcode_dict['d12_s1'], barcode_dict['d12_s2'], barcode_dict['d12_s3'] = row[20:24]
    barcode_dict['d18_all'], barcode_dict['d18_s1'], barcode_dict['d18_s2'], barcode_dict['d18_s3'] = row[32:36]
    barcode_dict['d24_all'], barcode_dict['d24_s1'], barcode_dict['d24_s2'], barcode_dict['d24_s3'] = row[36:40]

    barcode_summary = {'ternary_coord': [], 'cartesian_coord': [], 'vector': [], 'size': [], 'assigned_state': [],
                       'vector_size': [], 'cell_number': [], 'observed_bulk_size': [], 'total_size': 0}

    # lineage size for each timepoint is defined by S1 cells + S2 cells + S3 cells
    barcode_size = [sum(row[1:4]), sum(row[5:8]), sum(row[21:24]), sum(row[33:36]), sum(row[37:40])]

    for timepoint in timepoints:
        timepoint_all_present = all(barcode_size)
        timepoint_total = sum([barcode_dict[timepoint + '_' + state] for state in states])
        if timepoint_total:
            ternary_coord = []
            cell_number = []
            dist = []
            for state in states:
                ternary_coord.append(barcode_dict[timepoint + '_' + state] / timepoint_total)
                cell_number.append(barcode_dict[timepoint + '_' + state])

            # cell number contains number of cells in different states
            barcode_summary['cell_number'].append(cell_number)
            # ternary coordinate shows the proportion of cells in three states
            barcode_summary['ternary_coord'].append(ternary_coord)

            # turn ternary coordinate to cartesian coordinate to make downstream anaalysis easier
            cartesian_coord = np.dot(np.array(ternary_coord), triangle_vertices)
            barcode_summary['cartesian_coord'].append(list(cartesian_coord))

            # assign states to this lineage by the plurality vote (highest proportion)
            for state_coord in triangle_vertices:
                dist.append(euclidean_distance(cartesian_coord, state_coord))
            barcode_summary['assigned_state'].append(dist.index(min(dist)))

            barcode_summary['size'].append(timepoint_total)
            barcode_summary['observed_bulk_size'].append(barcode_dict[timepoint + '_all'])

    # if this lineage has reads in all timepoints
    if len(barcode_summary['cartesian_coord']) == 5:
        for i in range(4):
            # define vector by finding euclidean distance between two points
            barcode_summary['vector'].append((barcode_summary['cartesian_coord'][i + 1][0] -
                                              barcode_summary['cartesian_coord'][i][0],
                                              barcode_summary['cartesian_coord'][i + 1][1] -
                                              barcode_summary['cartesian_coord'][i][1]))
            barcode_summary['vector_size'].append(
                vector_size(barcode_summary['vector'][i][0], barcode_summary['vector'][i][1]))
        for size in barcode_summary['size']:
            all_size_set.add(round(size, 3))
            barcode_summary['total_size'] += size
        for size_ in barcode_summary['vector_size']:
            all_vector_size_set.add(round(size_, 3))
        all_barcode_list.append(barcode_summary)

def scatter_plot_right_all(all_barcode_list):
    fig, ax = plt.subplots()
    x_all = []
    y_all = []
    c_all = []
    color_scalarMap = matplotlib.cm.ScalarMappable(norm=matplotlib.colors.LogNorm(vmin=1, vmax=max(all_size_set)),
                                                   cmap='YlOrRd')
    # sort the lineage based on their size (ascending: small -> large)
    all_barcode_list.sort(key=lambda barcode: barcode['size'][-1])
    for barcode in all_barcode_list:
        cartesian_coord = barcode['cartesian_coord']
        size = barcode['size']
        for i in range(4):
            x_all.append(cartesian_coord[i][0])  # record x-coord
            y_all.append(cartesian_coord[i][1])  # record y-coord
            c_all.append(color_scalarMap.to_rgba(round(size[i], 3)))  # use colormap to define the size of this lineage

    ax.scatter(x_all, y_all, c=c_all, marker='.')
    ax.set_title('All Timepoints')
    ax.text(11, 9.85, 'State 1')
    ax.text(-2, 9.85, 'State 2')
    ax.text(-2, -0.15, 'State 3')
    ax.axis('off')

    plt.savefig("DotPlots_AllTimepoints_Right.svg", bbox_inches='tight', format='svg', dpi=720)

scatter_plot_right_all(all_barcode_list)