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
import copy
import numpy

def getAllData(input_dir, column_name, filter = None):
    all_data = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:

            input_file = os.path.join(input_dir, file)
            input_data_table = pandas.read_csv(input_file, sep='\t')
            if filter:
                filter(input_data_table)
            all_data.extend(input_data_table[column_name])
        break

    return all_data

# Fill in the missing data using linear interpolation.
# Always use the two closest data point for interpolation.
# We always use real samples for interpolation, we don't use
# interpolated data to interpolate other missing data.
def doLinearInterpolation(data):
    data = data.strip('][').split(', ')
    new_data = copy.deepcopy(data)
    for i in range(len(data)):
        if str(data[i]) == 'nan':
            first_point = i
            second_point = i
            for j in range(1, len(data)):
                if i - j >= 0 and str(data[i - j]) != 'nan':
                    if first_point == i:
                        first_point = i - j
                    else:
                        second_point = i - j
                        break
                if i + j <= len(data) - 1 and str(data[i + j]) != 'nan':
                    if first_point == i:
                        first_point = i + j
                    else:
                        second_point = i + j
                        break
            assert(first_point != i)
            assert(second_point != i)

            one_two_distance = abs(first_point - second_point)
            one_two_diff = abs(float(data[second_point]) - float(data[first_point]))
            step = one_two_diff / one_two_distance
            if first_point < second_point:
                if i < first_point:
                    new_data[i] = float(data[first_point]) - abs(first_point - i) * step
                else:
                    assert(i > first_point)
                    new_data[i] = float(data[first_point]) + abs(first_point - i) * step
            else:
                assert(first_point > second_point)
                if i < second_point:
                    new_data[i] = float(data[second_point]) - abs(second_point - i) * step
                else:
                    assert(i > second_point)
                    new_data[i] = float(data[second_point]) + abs(second_point - i) * step
        new_data[i] = float(new_data[i])
    return new_data

#smoothing with moving avarage
def smoothing(data):
    new_data = copy.deepcopy(data)
    kernel_size = 5
    kernel_half = 2
    for i in range(kernel_half, len(data) - kernel_half):
        assert(i - kernel_half >= 0)
        assert(i + kernel_half < len(data))
        new_data[i] = numpy.average(data[i - kernel_half:i + kernel_half + 1])

    #handle special cases
    size = len(data)
    new_data[0] = numpy.average(data[0:3])
    new_data[1] = numpy.average(data[0:4])
    new_data[-1] = numpy.average(data[-3:])
    new_data[-2] = numpy.average(data[-4:])
    return new_data

def convertPupilData(pupil_data_column):
    new_column = []
    all_pupil_size = []
    for i in range(len(pupil_data_column)):
        pupil_data = doLinearInterpolation(pupil_data_column[i])
        pupil_data = smoothing(pupil_data)
        for j in range(len(pupil_data)):
            all_pupil_size.append(pupil_data[j])
        new_column.append(copy.deepcopy(pupil_data))

    # standardize (x - average) / standard deviation
    average = numpy.average(all_pupil_size)
    std = numpy.std(all_pupil_size)

    assert(len(new_column) == len(pupil_data_column))
    for i in range(len(new_column)):
        pupil_data = new_column[i]
        for j in range(len(pupil_data)):
            pupil_data[j] = (pupil_data[j] - average) / std

    return new_column

def calcAllPupilData(input_dir):
    all_data = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:

            input_file = os.path.join(input_dir, file)
            input_data_table = pandas.read_csv(input_file, sep='\t')
            subject_pupil_data = convertPupilData(input_data_table['pupil_data'])
            all_data.extend(subject_pupil_data)
        break

    return all_data

# Extract pupil data from data files and categorize it
# based on triplet type (high - low).
def extractPupilDataHL(input_dir, output_file):
    pupil_column = calcAllPupilData(input_dir)

    HL_column = getAllData(input_dir, 'triplet_type_hl')
    category_column = []
    high_count = 0
    for i in range(len(HL_column)):
        if str(HL_column[i]) == 'high':
            category_column.append(1)
            high_count += 1
        else:
            assert(str(HL_column[i]) == 'low')
            category_column.append(0)

    print('Hight count ' + str(high_count))
    print('Low count ' + str(len(HL_column) - high_count))

    pupil_data = pandas.DataFrame()
    pupil_data['pupil_data'] = pupil_column
    pupil_data['category'] = category_column
    pupil_data.to_csv(output_file, sep='\t', index=False)

# Extract pupil data from data files and categorize it
# based on epoch, which is an indicator of where we
# are in the learning process (before - after).
def extractPupilDataBA(input_dir, output_file):
    pupil_column = calcAllPupilData(input_dir)

    epoch_column = getAllData(input_dir, 'epoch')
    category_column = []
    before_count = 0
    for i in range(len(epoch_column)):
        if str(epoch_column[i]) == '1':
            category_column.append(0)
            before_count += 1
        else:
            assert(str(epoch_column[i]) == '5')
            category_column.append(1)

    print('Before count ' + str(before_count))
    print('After count ' + str(len(epoch_column) - before_count))

    pupil_data = pandas.DataFrame()
    pupil_data['pupil_data'] = pupil_column
    pupil_data['category'] = category_column
    pupil_data.to_csv(output_file, sep='\t', index=False)
