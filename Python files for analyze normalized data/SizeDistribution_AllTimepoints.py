import pickle
import pandas as pd
import matplotlib
import numpy as np
import matplotlib.pyplot as plt

matplotlib.rcParams['font.sans-serif'] = "Helvetica"
matplotlib.rcParams['font.family'] = "sans-serif"

total_cell_number = 10**8

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

all_barcode_number_list = []
for barcode, row in true_number_table.iterrows():
    d0_all, d0_s1, d0_s2, d0_s3 = row[0:4]
    d6_all, d6_s1, d6_s2, d6_s3 = row[4:8]
    d9_all, d9_s1, d9_s2, d9_s3 = row[16:20]
    d12_all, d12_s1, d12_s2, d12_s3 = row[20:24]
    d18_all, d18_s1, d18_s2, d18_s3 = row[32:36]
    d24_all, d24_s1, d24_s2, d24_s3 = row[36:40]
    average_size = sum([sum(row[1:4]), sum(row[5:8]), sum(row[21:24]), sum(row[33:36]), sum(row[37:40])])/5
    all_barcode_number_list.append(average_size)

fig, ax = plt.subplots(1, 1, sharex=True, sharey=True, figsize=[8, 6])
bins = 10 ** (np.arange(0, 7, 0.1))

ax.hist(all_barcode_number_list, bins=bins)
ax.set_xscale('log')

fig.suptitle('Distribution of Average Lineage Size Across All Timepoints', size='x-large', y=0.95)
fig.text(0.5, 0.04, '$\log_{10}$ Average Lineage Size', ha='center', va='center', size='x-large')
fig.text(0.06, 0.5, 'Number of Lineages', ha='center', va='center', rotation='vertical', size='x-large')
plt.savefig('SizeDistribution_AllTimepoint.svg', bbox_inches='tight', format='svg', dpi=720)