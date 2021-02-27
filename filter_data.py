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

import pandas

def filterMessage(title, original_size, new_size):
    print(title)
    print('Filtered out data count: ' + str(original_size - new_size))
    print('Filtered out data percentage: ' + str(100.0 - (new_size / original_size * 100.0)))
    print('New data count: ' + str(new_size))

def keepEpochs(data_table, epochs_to_keep):
    original_size = len(data_table.index)
    for index, row in data_table.iterrows():
        if int(row['epoch']) not in epochs_to_keep:
            data_table.drop(index, inplace=True)

    new_size = len(data_table.index)
    filterMessage('Keep data of specified epochs.', original_size, new_size)

def fitlerFirstTwoTrials(data_table):
    original_size = len(data_table.index)
    for index, row in data_table.iterrows():
        if int(row['trial']) <= 2:
            data_table.drop(index, inplace=True)

    new_size = len(data_table.index)

    filterMessage('Filtered first and second trials.', original_size, new_size)

def fitlerRepetition(data_table):
    original_size = len(data_table.index)
    for index, row in data_table.iterrows():
        if bool(row['repetition']):
            data_table.drop(index, inplace=True)

    new_size = len(data_table.index)

    filterMessage('Filtered repetitions.', original_size, new_size)

def filterBlinkGap(data_table):
    original_size = len(data_table.index)
    for index, row in data_table.iterrows():
        if int(row['missing_pupil_data_maxgap']) > 3: # > 75 ms
            data_table.drop(index, inplace=True)

    new_size = len(data_table.index)

    filterMessage('Filter big gaps.', original_size, new_size)

def filterTooMuchMissingData(data_table):
    original_size = len(data_table.index)
    for index, row in data_table.iterrows():
        if int(row['missing_pupil_data_count']) > 11: # > 22 %
            data_table.drop(index, inplace=True)

    new_size = len(data_table.index)

    filterMessage('Filter too much missing data.', original_size, new_size)

def filterExtremeTimeWindow(data_table):
    original_size = len(data_table.index)
    for index, row in data_table.iterrows():
        if int(row['pupil_data_time_window']) < 1220000 or int(row['pupil_data_time_window']) > 1260000:
            data_table.drop(index, inplace=True)

    new_size = len(data_table.index)

    filterMessage('Filter extreme time window.', original_size, new_size)

def filterExtremeRTData(data_table):
    original_size = len(data_table.index)
    for index, row in data_table.iterrows():
        RT = float(row['RT (ms)'].replace(',','.'))
        if RT < 164.0 or RT > 551.0:
            data_table.drop(index, inplace=True)

    new_size = len(data_table.index)

    filterMessage('Filter extreme RT.', original_size, new_size)

def filterData(input_file, output_file, epochs_to_keep):
    data_table = pandas.read_csv(input_file, sep='\t')

    keepEpochs(data_table, epochs_to_keep)
    fitlerFirstTwoTrials(data_table)
    fitlerRepetition(data_table)
    filterBlinkGap(data_table)
    filterTooMuchMissingData(data_table)
    filterExtremeTimeWindow(data_table)
    filterExtremeRTData(data_table)

    data_table.to_csv(output_file, sep='\t', index=False)
    return len(data_table)
