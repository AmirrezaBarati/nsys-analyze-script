#This script extracts a few metrics about the GPU applications.
#Copyright (C) 2024 Amirreza Barati Sedeh

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
 
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <https://www.gnu.org/licenses/>.
#########################################################################
#Usage: python3 kernel_metrics.py <sqlite file>

#Note: It may take from a few minutes to multiple hours for the script
# to finish producing the figures based on the <sqlite file> size
#########################################################################
import os
import sys 
import matplotlib
matplotlib.use("pgf")
matplotlib.rcParams.update({
    "pgf.texsystem": "pdflatex",
    'font.family': 'serif',
    'font.size': 14, 
    'text.usetex': True,
    'pgf.rcfonts': False,
})
import matplotlib.pyplot as plt 
import numpy as np
import re
import math
import heapq
import sqlite3
from matplotlib.ticker import MultipleLocator
######################################################################
def calculate_median(lst):
    return np.median(lst)
######################################################################
def remove_outliers(data):
    # Calculate the first and third quartiles
    Q1 = np.percentile(data, 25) 
    Q3 = np.percentile(data, 75) 

    # Calculate the interquartile range (IQR)
    IQR = Q3 - Q1

    # Define the lower and upper bounds for outliers
    lower_bound = Q1 - 1.5 * IQR 
    upper_bound = Q3 + 1.5 * IQR 

    # Remove outliers
    clean_data = [x for x in data if (x >= lower_bound) and (x <= upper_bound)]

    return clean_data
######################################################################
def extract_metrics(database_file):
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()
    ############################################################
    sql_query_kernel_list = """ 
    SELECT DISTINCT
        StringIds.value,
        cuda_gpu.gridX,
        cuda_gpu.gridY,
        cuda_gpu.gridZ,
        cuda_gpu.blockX,
        cuda_gpu.blockY,
        cuda_gpu.blockZ
    FROM StringIds 
    JOIN CUPTI_ACTIVITY_KIND_KERNEL AS cuda_gpu ON cuda_gpu.shortName = StringIds.id
    JOIN CUPTI_ACTIVITY_KIND_RUNTIME ON CUPTI_ACTIVITY_KIND_RUNTIME.correlationId = cuda_gpu.correlationId
    """
    ############################################################
    sql_query_ket = """
    SELECT KERNEL.end - KERNEL.start AS klo
    FROM CUPTI_ACTIVITY_KIND_RUNTIME AS RUNTIME
    JOIN CUPTI_ACTIVITY_KIND_KERNEL AS KERNEL
    ON RUNTIME.correlationId = KERNEL.correlationId
    JOIN StringIds AS StringIds
    ON KERNEL.shortName = StringIds.id
    WHERE StringIds.value = ?
    AND KERNEL.gridX = ?
    AND KERNEL.gridY = ?
    AND KERNEL.gridZ = ?
    AND KERNEL.blockX = ?
    AND KERNEL.blockY = ?
    AND KERNEL.blockZ = ?
    """
    ############################################################
    sql_query_klo = """ 
    SELECT RUNTIME.end - RUNTIME.start AS klo
    FROM CUPTI_ACTIVITY_KIND_RUNTIME AS RUNTIME
    JOIN CUPTI_ACTIVITY_KIND_KERNEL AS KERNEL
    ON RUNTIME.correlationId = KERNEL.correlationId
    JOIN StringIds AS StringIds
    ON KERNEL.shortName = StringIds.id
    WHERE StringIds.value = ?
    AND KERNEL.gridX = ?
    AND KERNEL.gridY = ?
    AND KERNEL.gridZ = ?
    AND KERNEL.blockX = ?
    AND KERNEL.blockY = ?
    AND KERNEL.blockZ = ?
    """
    ############################################################
    sql_query_slack = """ 
    SELECT KERNEL.start - RUNTIME.end AS time_difference
    FROM CUPTI_ACTIVITY_KIND_RUNTIME AS RUNTIME
    JOIN CUPTI_ACTIVITY_KIND_KERNEL AS KERNEL
    ON RUNTIME.correlationId = KERNEL.correlationId
    JOIN StringIds AS StringIds
    ON KERNEL.shortName = StringIds.id
    WHERE StringIds.value = ?
    AND KERNEL.gridX = ?
    AND KERNEL.gridY = ?
    AND KERNEL.gridZ = ?
    AND KERNEL.blockX = ?
    AND KERNEL.blockY = ?
    AND KERNEL.blockZ = ?
    """
################################################################################
    labels = []
    ket_tmp = []
    klo_tmp = []
    slack_tmp = []
    ket = []
    klo = []
    slack = []
    ket_list = []
    klo_list = []
    slack_list = []
    kernels_list = []
    dominant_list = []
################################################################################
    cursor.execute(sql_query_kernel_list)
    results = cursor.fetchall()
    for item in results:
        kernels_list.append(item)
        label_tmp = item[0]+','+str(item[1])+','+str(item[2])+','+str(item[3])+','+str(item[4])+','+str(item[5])+','+str(item[6])
        labels.append(label_tmp[0:min(9,len(label_tmp))])
################################################################################
    for kernel_name in kernels_list:
        cursor.execute(sql_query_ket, (kernel_name[0],kernel_name[1],kernel_name[2],kernel_name[3],kernel_name[4],kernel_name[5],kernel_name[6]))
        ket_tmp = cursor.fetchall()
        ket = []
        for ind in ket_tmp:
            if (ind[0] > 0):
                ket.append(ind[0] / 1000)
        if (len(ket) == 0):
            ket.append(0)

        ket_list.append(math.log10(calculate_median(ket)))
        dominant_list.append(len(ket) * calculate_median(ket))
        #################################################
        cursor.execute(sql_query_klo, (kernel_name[0],kernel_name[1],kernel_name[2],kernel_name[3],kernel_name[4],kernel_name[5],kernel_name[6]))
        klo_tmp = cursor.fetchall()
        klo = []
        for ind in klo_tmp:
            if (ind[0] > 0): 
                klo.append(ind[0] / 1000)
        if (len(klo) == 0): 
            klo.append(0)

        klo_list.append(math.log10(calculate_median(remove_outliers(klo))))
        #################################################
        cursor.execute(sql_query_slack, (kernel_name[0],kernel_name[1],kernel_name[2],kernel_name[3],kernel_name[4],kernel_name[5],kernel_name[6]))
        slack_tmp = cursor.fetchall()
        slack = []
        for ind in slack_tmp:
            if (ind[0] > 0):
                slack.append(ind[0] / 1000)
        if (len(slack) == 0):
            slack.append(0)

        if len(slack) == 1 and slack[0] == 0:
            slack_list.append(0)
        else:
            slack_list.append(math.log10(calculate_median(remove_outliers(slack))))
##########################################################################
    num_dominating_kernels = 50
    if (len(ket_list) > num_dominating_kernels):
        largest_indices = heapq.nlargest(num_dominating_kernels, range(len(dominant_list)), key=lambda i: dominant_list[i])
        ket_list_bar = [ket_list[i] for i in largest_indices]
        klo_list_bar = [klo_list[i] for i in largest_indices]
        slack_list_bar = [slack_list[i] for i in largest_indices]
        labels_bar = [labels[i] for i in largest_indices]
    else:
        ket_list_bar = ket_list
        klo_list_bar = klo_list
        slack_list_bar = slack_list
        labels_bar = labels
###########################################################################
    fig, ax = plt.subplots(1, figsize=(18, 12))
    ax.bar(range(1, len(ket_list_bar)+1), ket_list_bar, width=1, edgecolor='black')
    x_values = np.arange(1,len(ket_list_bar)+1)
    ax.xaxis.set_ticks(x_values)
    ax.xaxis.set_ticklabels(labels_bar)
    ax.tick_params(axis='x', rotation=90)
    max_items_in_bin = np.max(ket_list_bar)
    min_items_in_bin = np.min(ket_list_bar)
    y_step_size = (max_items_in_bin - min_items_in_bin) / 10
    ax.yaxis.set_major_locator(MultipleLocator(y_step_size))
    ax.grid(axis='y', linestyle='--', linewidth=0.5, color='gray', alpha=0.5)
    ax.set_xlabel("Kernel Name")
    ax.set_ylabel("Kernel Duration (us) - Log Base 10")
    fig.tight_layout()
    fig.subplots_adjust(top=0.95)
    fig.savefig('metric_ket_bar.pgf', bbox_inches='tight')
    fig.savefig('metric_ket_bar.png', bbox_inches='tight')
    ########################################################
    fig, ax = plt.subplots(1, figsize=(18, 12))
    ax.bar(range(1, len(klo_list_bar)+1), klo_list_bar, width=1, edgecolor='black')
    x_values = np.arange(1,len(klo_list_bar)+1)
    ax.xaxis.set_ticks(x_values)
    ax.xaxis.set_ticklabels(labels_bar)
    ax.tick_params(axis='x', rotation=90)
    max_items_in_bin = np.max(klo_list_bar)
    min_items_in_bin = np.min(klo_list_bar)
    y_step_size = (max_items_in_bin - min_items_in_bin) / 10
    ax.yaxis.set_major_locator(MultipleLocator(y_step_size))
    ax.grid(axis='y', linestyle='--', linewidth=0.5, color='gray', alpha=0.5)
    ax.set_xlabel("Kernel Name")
    ax.set_ylabel("Kernel Launch Overhead (us) - Log Base 10")
    fig.tight_layout()
    fig.subplots_adjust(top=0.95)
    fig.savefig('metric_klo_bar.pgf', bbox_inches='tight')
    fig.savefig('metric_klo_bar.png', bbox_inches='tight')
    ########################################################
    fig, ax = plt.subplots(1, figsize=(18, 12))
    ax.bar(range(1, len(slack_list_bar)+1), slack_list_bar, width=1, edgecolor='black')
    x_values = np.arange(1,len(slack_list_bar)+1)
    ax.xaxis.set_ticks(x_values)
    ax.xaxis.set_ticklabels(labels_bar)
    ax.tick_params(axis='x', rotation=90)
    max_items_in_bin = np.max(slack_list_bar)
    min_items_in_bin = np.min(slack_list_bar)
    y_step_size = (max_items_in_bin - min_items_in_bin) / 10
    ax.yaxis.set_major_locator(MultipleLocator(y_step_size))
    ax.grid(axis='y', linestyle='--', linewidth=0.5, color='gray', alpha=0.5)
    ax.set_xlabel("Kernel Name")
    ax.set_ylabel("Slack (us) - Log Base 10")
    fig.tight_layout()
    fig.subplots_adjust(top=0.95)
    fig.savefig('metric_slack_bar.pgf', bbox_inches='tight')
    fig.savefig('metric_slack_bar.png', bbox_inches='tight')
    ########################################################
    ratio = []
    for item in range(len(ket_list_bar)):
        ratio.append((10 ** ket_list_bar[item]) / (10 ** klo_list_bar[item]))

    for item in range(len(ratio)):
        ratio[item] = math.log10(ratio[item])

    fig, ax = plt.subplots(1, figsize=(18, 12))
    ax.bar(range(1, len(ratio)+1), ratio, width=1, edgecolor='black')
    x_values = np.arange(1,len(ratio)+1)
    ax.xaxis.set_ticks(x_values)
    ax.xaxis.set_ticklabels(labels_bar)
    ax.tick_params(axis='x', rotation=90)
    max_items_in_bin = np.max(ratio)
    min_items_in_bin = np.min(ratio)
    y_step_size = (max_items_in_bin - min_items_in_bin) / 10
    ax.yaxis.set_major_locator(MultipleLocator(y_step_size))
    ax.grid(axis='y', linestyle='--', linewidth=0.5, color='gray', alpha=0.5)
    ax.set_xlabel("Kernel Name")
    ax.set_ylabel("Ratio of Duration to Launch - log base 10")
    fig.tight_layout()
    fig.subplots_adjust(top=0.95)
    fig.savefig('metric_ratio.pgf', bbox_inches='tight')
    fig.savefig('metric_ratio.png', bbox_inches='tight')
###########################################################################
if __name__ == "__main__":
    # Check if the correct number of arguments are provided
    if len(sys.argv) != 2:
        print("Usage: python program_name.py database_file.db")
        sys.exit(1)

    # Get the SQLite file from command line argument
    database_file = sys.argv[1]

    # Calculate time differences
    extract_metrics(database_file)

