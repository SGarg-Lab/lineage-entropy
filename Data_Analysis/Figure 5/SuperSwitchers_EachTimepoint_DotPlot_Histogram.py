"""
This file produces a stacked histogram that shows the distribution of motility in all timepoints combined
"""

import pickle
import math
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

top_right_coord = (1, 1)
top_left_coord = (0, 1)
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
                       'total_transition_amount': 0, 'transition_amount': []}

    barcode_size = [sum(row[1:4]), sum(row[5:8]), sum(row[21:24]), sum(row[33:36]), sum(row[37:40])]

    for timepoint in timepoints:
        timepoint_all_present = all(barcode_size)
        timepoint_total = sum([barcode_dict[timepoint + '_' + state] for state in states])
        if timepoint_total > 10:
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
            barcode_summary['transition_amount'].append(vector_size(vector[0], vector[1]))
        all_transition_size_list.append(barcode_summary['total_transition_amount'])
        for size in barcode_summary['size']:
            all_size_set.add(round(size, 3))
        all_barcode_list.append(barcode_summary)
all_barcode_list.sort(reverse=True, key=lambda barcode: barcode['total_transition_amount'])

barcode_number = len(all_barcode_list)


def scatter_plot(all_barcode_list):
    # each lineage has a unique color
    rainbow = cm.get_cmap('rainbow', barcode_number)
    rainbow_list = rainbow(range(barcode_number))[::-1]

    # iterate through each transition
    for transition in range(4):
        fig = plt.figure()
        ax = plt.axes()

        ax.set_ylabel('Log Average Lineage Size')
        ax.set_xlabel('Total Amount of Transition')

        # plot scatter plots
        for index, barcode in enumerate(all_barcode_list):
            average_size = sum(barcode['size'][1:]) / len(barcode['size'][1:])
            plt.scatter(barcode['transition_amount'][transition], np.log10(average_size), color=rainbow_list[index], marker='.')

        plt.title('Day {} to {}'.format(transition*6, (transition+1)*6))
        fig.tight_layout()
        fig.savefig("SuperSwitchers_EachTimepoint_DotPlot_T{}.svg".format(transition), bbox_inches='tight', format='svg', dpi=720)


def histogram(all_barcode_list):
    # each lineage gets unique color
    rainbow = cm.get_cmap('rainbow_r', barcode_number)
    rainbow_list = rainbow(range(barcode_number))[::-1]

    # iterate through each transition
    for transition in range(4):
        fig = plt.figure()
        ax = plt.axes()
        ax.set_xlim(0, 1.5)
        if transition == 0:
            ax.set_ylabel('Number of Distinct Lineages')
            ax.set_xlabel('Total Amount of Transition')

        n, bins, patches = plt.hist([barcode['transition_amount'][transition] for barcode in all_barcode_list], 30, color='black')
        plt.ylim(0, 800)

        bin_centers = 0.5 * (bins[:-1] + bins[1:])

        # scale values to interval [0,1]
        col = bin_centers - min(bin_centers)
        col /= max(col)

        number_barcodes = 0
        index = 0

        for c, p in zip(col, patches):
            plt.setp(p, 'facecolor', rainbow_list[int(number_barcodes)])
            plt.setp(p, edgecolor='black')
            if number_barcodes + n[i] < len(all_barcode_list):
                number_barcodes += n[i]
                index += 1
            else:
                pass

        fig.tight_layout()
        fig.savefig("SuperSwitchers_EachTimepoint_Histogram_T{}.svg".format(transition), bbox_inches='tight', format='svg', dpi=720)

histogram(all_barcode_list)
scatter_plot(all_barcode_list)