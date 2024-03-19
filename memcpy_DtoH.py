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
#Usage: python3 memcpy_DtoH.py <sqlite file>

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
###################################################
def extract_host_to_device_transfers(database_file):
    try:
        # Connect to the SQLite database
        connection = sqlite3.connect(database_file)
        cursor = connection.cursor()

        # Execute SQL query to fetch host-to-device transfers and their sizes
        cursor.execute("SELECT bytes FROM CUPTI_ACTIVITY_KIND_MEMCPY WHERE copyKind = 2")

        # Fetch all the rows
        transfers = cursor.fetchall()

        # Extract transfer sizes
        transfer_sizes = [transfer[0] for transfer in transfers]

        labels = ["4KB","8KB","16KB","32KB","64KB","128KB","256KB","512KB","1MB","1MB+"]
        bin_array = np.zeros(10)
        for num in transfer_sizes:
            if (num <= 4096):
                bin_array[0] += 1
            elif (num <= 8192):
                bin_array[1] += 1
            elif (num <= 16384):
                bin_array[2] += 1
            elif (num <= 32768):
                bin_array[3] += 1
            elif (num <= 65536):
                bin_array[4] += 1
            elif (num <= 131072):
                bin_array[5] += 1
            elif (num <= 262144):
                bin_array[6] += 1
            elif (num <= 524288):
                bin_array[7] += 1
            elif (num <= 1048576):
                bin_array[8] += 1
            else:
                bin_array[9] += 1


        fig, ax = plt.subplots(1, figsize=(10, 10))
        ax.bar(range(1, 11), bin_array, width=1, edgecolor='black')
        x_values = np.arange(1,len(bin_array)+1)
        ax.xaxis.set_ticks(x_values)
        ax.xaxis.set_ticklabels(labels)
        ax.tick_params(axis='x', rotation=45)
        max_items_in_bin = np.max(bin_array)
        min_items_in_bin = np.min(bin_array)
        y_step_size = (max_items_in_bin - min_items_in_bin) / 10
        ax.yaxis.set_major_locator(MultipleLocator(y_step_size))
        ax.grid(axis='y', linestyle='--', linewidth=0.5, color='gray', alpha=0.5)
        ax.set_xlabel("Transfer Size Range")
        ax.set_ylabel("Frequency")
        fig.tight_layout()
        fig.subplots_adjust(top=0.95)
        fig.savefig('hist_DtoH.pgf', bbox_inches='tight')
        fig.savefig('hist_DtoH.png', bbox_inches='tight')

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

