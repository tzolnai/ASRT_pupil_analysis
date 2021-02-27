# !/usr/bin/env python
# -*- coding: utf-8 -*-

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import pandas
import numpy

# Example result (mild outliers)
# Outlier bounds for pupil data time window size.
# low_bound: 1221720.5
# high_bound: 1261470.5
# all data count 111452
# extreme low data count 2165
# extreme high data count 2250
# Outlier bounds for missing pupil data count.
# low_bound: -5.0
# high_bound: 11.0
# all data count 111452
# extreme low data count 0
# extreme high data count 6018
# Outlier bounds for RT.
# low_bound: 164.320875
# high_bound: 551.4098749999999
# all data count 83606
# extreme low data count 2808
# extreme high data count 7834

def getAllData(input_dir, column_name, filter = None):
    all_data = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:

            input_file = os.path.join(input_dir, file)
            input_data_table = pandas.read_csv(input_file, sep='\t')
            if filter:
                filter(input_data_table)
            all_data.extend(input_data_table[column_name][2:]) # filter out first two practice trials.
        break

    return all_data

#https://psychology.wikia.org/wiki/Outlier
def calcBounds(data, title):
    Q1 = numpy.percentile(data, 25)
    Q3 = numpy.percentile(data, 75)
    IQR = Q3 - Q1
    low_bound = Q1 - 1.5 * IQR
    high_bound = Q3 + 1.5 * IQR

    print(title)
    print('low_bound: ' + str(low_bound))
    print('high_bound: ' + str(high_bound))
    print('all data count ' + str(len(data)))
    print('extreme low data count ' + str((data < low_bound).sum()))
    print('extreme high data count ' + str((data > high_bound).sum()))

# Create an output file of all used data so we can plot it on a box diagram.
def writeOutAllData(data, output_file, column_name):
    output = pandas.DataFrame({column_name : data})
    output.to_csv(output_file, sep='\t', index=False)

# Check the actual size of the time window of pupil data array.
def timeWindowBounds(input_dir, output_dir):
    all_pupil_time_data = getAllData(input_dir, 'pupil_data_time_window')
    calcBounds(all_pupil_time_data, 'Outlier bounds for pupil data time window size.')

    output_file = os.path.join(output_dir, 'time_window_data.txt')
    writeOutAllData(all_pupil_time_data, output_file, 'pupil_data_time_window')

# How many missing data inside the pupil array is accepted.
def missingPupilDataBounds(input_dir, output_dir):
    missing_data = getAllData(input_dir, 'missing_pupil_data_count')
    calcBounds(missing_data, 'Outlier bounds for missing pupil data count.')

    output_file = os.path.join(output_dir, 'missing_pupil_data.txt')
    writeOutAllData(missing_data, output_file, 'missing_pupil_data_count')

# We filter-out repetition for RT bounds calculation
# because they are assummed to be extreme low values.
def fitlerRepetition(data_table):
    for index, row in data_table.iterrows():
        if bool(row['repetition']):
            data_table.drop(index, inplace=True)

# We filter-out extreme reaction times too, so the pupil time window
# is kind of homogeneous wrt. the events during the trial.
def RTBounds(input_dir, output_dir):
    RT_data = getAllData(input_dir, 'RT (ms)', fitlerRepetition)
    number_RT_data = [float(i.replace(',','.')) for i in RT_data]
    calcBounds(number_RT_data, 'Outlier bounds for RT.')

    output_file = os.path.join(output_dir, 'RT_data.txt')
    writeOutAllData(RT_data, output_file, 'RT (ms)')

def calcOutlierBounds(input_dir, output_dir):
    timeWindowBounds(input_dir, output_dir)
    missingPupilDataBounds(input_dir, output_dir)
    RTBounds(input_dir, output_dir)
