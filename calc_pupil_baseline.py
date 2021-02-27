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
import sys
import pandas
import math
import numpy

def convertToFloat(data):
    return float(str(data).replace(",", "."))

def calcPupilBaselines(input_file):
    input_data_table = pandas.read_csv(input_file, sep='\t')

    trial_column = input_data_table["trial"]
    epoch_column = input_data_table["epoch"]
    left_pupil_validity_column = input_data_table['left_pupil_validity']
    right_pupil_validity_column = input_data_table['right_pupil_validity']
    left_pupil_diameter_column = input_data_table['left_pupil_diameter']
    right_pupil_diameter_column = input_data_table['right_pupil_diameter']

    epoch_pupil_baselines = []
    epoch_pupil_std = []
    pupil_data = []
    current_epoch = epoch_column[0]
    for i in range(len(trial_column) + 1):
        if i == len(trial_column) or epoch_column[i] != current_epoch:
            epoch_pupil_baselines.append(numpy.median(pupil_data))
            epoch_pupil_std.append(numpy.std(pupil_data))
            pupil_data = []
            if i < len(trial_column):
                current_epoch = epoch_column[i]
            else:
                break

        if int(trial_column[i]) > 2: # ignore first two trials
            left_pupil_size = convertToFloat(left_pupil_diameter_column[i])
            right_pupil_size = convertToFloat(right_pupil_diameter_column[i])
            if left_pupil_validity_column[i] and left_pupil_size > 0:
                pupil_data.append(left_pupil_size)
            if right_pupil_validity_column[i] and right_pupil_size > 0:
                pupil_data.append(right_pupil_size)

    assert(len(epoch_pupil_baselines) == 8)
    assert(len(epoch_pupil_std) == 8)
    return epoch_pupil_baselines, epoch_pupil_std

def generatePupilBaseline(input_dir, baseline_output_file, std_output_file):
    pupil_baselines = []
    pupil_sdts = []
    subjects = []
    filtered_subjects = [14, 17, 37, 39, # a lot of extreme RT -> bad ET accuracy
                        27, 47] # bad learning measure
    for root, dirs, files in os.walk(input_dir):
        for subject_dir in dirs:
            if subject_dir.startswith('.'):
                continue
            
            if int(subject_dir) in filtered_subjects:
                continue

            subjects.append(subject_dir)
            raw_data_path = os.path.join(root, subject_dir, 'subject_' + subject_dir + '__log.txt')
            basline, std = calcPupilBaselines(raw_data_path)
            pupil_baselines.append(basline)
            pupil_sdts.append(std)

        break

    pupil_baseline_data = pandas.DataFrame({'subject' : subjects})
    for i in range(8):
        epoch_baseline_column = []
        for j in range(len(pupil_baselines)):
            epoch_baseline_column.append(pupil_baselines[j][i])
        pupil_baseline_data['epoch_' + str(i + 1) + '_median_pupil'] = epoch_baseline_column
    pupil_baseline_data.to_csv(baseline_output_file, sep='\t', index=False)

    pupil_std_data = pandas.DataFrame({'subject' : subjects})
    for i in range(8):
        epoch_std_column = []
        for j in range(len(pupil_sdts)):
            epoch_std_column.append(pupil_sdts[j][i])
        pupil_std_data['epoch_' + str(i + 1) + 'pupil_std'] = epoch_std_column
    pupil_std_data.to_csv(std_output_file, sep='\t', index=False)
