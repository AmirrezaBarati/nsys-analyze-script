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
#Usage: python3 memcpy_DtoH_bw.py <sqlite file>

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
import sqlite3
from matplotlib.ticker import MultipleLocator
####################################################
def extract_host_to_device_transfers(database_file):
    try:
        # Connect to the SQLite database
        connection = sqlite3.connect(database_file)
        cursor = connection.cursor()

        # Execute SQL query to fetch host-to-device transfers and their sizes
        cursor.execute("SELECT start, end, bytes FROM CUPTI_ACTIVITY_KIND_MEMCPY WHERE copyKind = 2")

        # Fetch all the rows
        transfers = cursor.fetchall()
        num_arr = 10
        array_lists = [[] for _ in range(num_arr)]
        for data in transfers:
            if (data[2] <= (4*1024)):
                byte_tmp = data[2] * 953.674
                time = data[1] - data[0]
                array_lists[0].append(byte_tmp / time)
            elif (data[2] <= (8*1024)):
                byte_tmp = data[2] * 953.674
                time = data[1] - data[0]
                array_lists[1].append(byte_tmp / time)
            elif (data[2] <= (16*1024)):
                byte_tmp = data[2] * 953.674
                time = data[1] - data[0]
                array_lists[2].append(byte_tmp / time)
            elif (data[2] <= (32*1024)):
                byte_tmp = data[2] * 953.674
                time = data[1] - data[0]
                array_lists[3].append(byte_tmp / time)
            elif (data[2] <= (64*1024)):
                byte_tmp = data[2] * 953.674
                time = data[1] - data[0]
                array_lists[4].append(byte_tmp / time)
            elif (data[2] <= (128*1024)):
                byte_tmp = data[2] * 953.674
                time = data[1] - data[0]
                array_lists[5].append(byte_tmp / time)
            elif (data[2] <= (256*1024)):
                byte_tmp = data[2] * 953.674
                time = data[1] - data[0]
                array_lists[6].append(byte_tmp / time)
            elif (data[2] <= (512*1024)):
                byte_tmp = data[2] * 953.674
                time = data[1] - data[0]
                array_lists[7].append(byte_tmp / time)
            elif (data[2] <= (1024*1024)):
                byte_tmp = data[2] * 953.674
                time = data[1] - data[0]
                array_lists[8].append(byte_tmp / time)
            else:
                byte_tmp = data[2] * 953.674
                time = data[1] - data[0]
                array_lists[9].append(byte_tmp / time)


        for item in array_lists:
            if (len(item) == 0):
                item.append(0)

        
        labels = ["4KB","8KB","16KB","32KB","64KB","128KB","256KB","512KB","1MB","1MB+"]
        x_values = np.arange(1,len(array_lists)+1)
        fig, ax = plt.subplots(1, figsize=(10, 10))
        parts = ax.violinplot(array_lists, showmeans=True, showmedians=True)
        # Customizing violin parts
        for pc in parts['bodies']:
            pc.set_facecolor('skyblue')
            pc.set_edgecolor('black')
            pc.set_alpha(0.7)

        # Customizing median line
        parts['cmedians'].set_color('blue')
        parts['cmedians'].set_linewidth(2)
        # Customizing whiskers and caps
        parts['cmins'].set_color('red')
        parts['cmins'].set_linestyle('--')
        parts['cmaxes'].set_color('green')
        parts['cmaxes'].set_linestyle('--')
        # Customizing caps
        parts['cbars'].set_color('black')

        ax.xaxis.set_ticks(x_values)
        ax.xaxis.set_ticklabels(labels)
        ax.tick_params(axis='x', rotation=45)
        max_value = max(max(sublist) for sublist in array_lists)
        min_value = min(min(sublist) for sublist in array_lists)
        y_step_size = (max_value - min_value) / 10
        ax.yaxis.set_major_locator(MultipleLocator(y_step_size))
        ax.grid(axis='y', linestyle='--', linewidth=0.5, color='gray', alpha=0.5)
        ax.set_xlabel("Transfer size range (B)")
        ax.set_ylabel("Bandwidth (MB/s)")
        fig.tight_layout()
        fig.subplots_adjust(top=0.95)
        fig.savefig('hist_DtoH_bw.pgf', bbox_inches='tight')
        fig.savefig('hist_DtoH_bw.png', bbox_inches='tight')

    except sqlite3.Error as error:
        print("Error reading data from SQLite table:", error)

    finally:
        # Close the database connection
        if connection:
            connection.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python program_name.py <database_file>")
        sys.exit(1)

    database_file = sys.argv[1]
    extract_host_to_device_transfers(database_file)

