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

def generateOutput(raw_file_name, new_file_name, RT_data, pupil_data, pupil_time_data):
    # use the input data headers
    input_data = pandas.read_csv(raw_file_name, sep='\t')
    output_data = pandas.DataFrame(columns=input_data.columns)

    # remove some useless fields
    output_data = output_data.drop(columns=['RSI_time', 'trial_phase', 'left_gaze_data_X_ADCS', 'left_gaze_data_Y_ADCS',
                      'right_gaze_data_X_ADCS', 'right_gaze_data_Y_ADCS', 'left_gaze_data_X_PCMCS',
                      'left_gaze_data_Y_PCMCS', 'right_gaze_data_X_PCMCS', 'right_gaze_data_Y_PCMCS',
                      'left_eye_distance', 'right_eye_distance', 'left_gaze_validity', 'right_gaze_validity',
                      'left_pupil_diameter', 'right_pupil_diameter', 'left_pupil_validity', 'right_pupil_validity',
                      'gaze_data_time_stamp', 'stimulus_1_position_X_PCMCS', 'stimulus_1_position_Y_PCMCS',
                      'stimulus_2_position_X_PCMCS', 'stimulus_2_position_Y_PCMCS', 'stimulus_3_position_X_PCMCS',
                      'stimulus_3_position_Y_PCMCS', 'stimulus_4_position_X_PCMCS', 'stimulus_4_position_Y_PCMCS', 'quit_log', 'Unnamed: 48'])

    output_index = 0
    last_trial = "0"
    for index, row in input_data.iterrows():
        # we ignore 0 indexed blocks, which are calibration validation blocks.
        if str(row['block']) == "0":
            continue

        # insert one row of each trial data
        if row['trial'] != last_trial:
            last_trial = row['trial']
            output_data.loc[output_index] = row
            output_index += 1

    # reaction time of the trial
    assert(len(output_data.index) == len(RT_data))
    output_data['RT (ms)'] = RT_data

    # array of pupil sizes
    assert(len(output_data.index) == len(pupil_data))
    output_data['pupil_data'] = pupil_data

    # actual time window size of pupil data
    assert(len(output_data.index) == len(pupil_time_data))
    output_data['pupil_data_time_window'] = pupil_time_data

    output_data.to_csv(new_file_name, sep='\t', index=False)

def convertToFloat(data):
    return float(str(data).replace(",", "."))

def calcRTColumn(raw_file_name):
    input_data = pandas.read_csv(raw_file_name, sep='\t')

    last_trial = "1"
    start_time = 0
    end_time = 0
    start_time_found = False
    end_time_found = False
    RT_data = []
    previous_row = -1

    for index, row in input_data.iterrows():
        # we are at the end of the trial (actually at the first row of the next trial)
        if last_trial != str(row['trial']) or index == len(input_data.index) - 1:
            # we ignore 0 indexed blocks, which are calibration validation blocks.
            if isinstance(previous_row, pandas.Series) and str(previous_row['block']) != "0":
                # We calculate the elapsed time during the stimulus was on the screen.
                if start_time_found and end_time_found:
                    RT_data.append(str((end_time - start_time) / 1000.0).replace(".", ","))
                # if there is not endtime, then it means the software was fast enough to step
                # on to the next trial instantly after the stimulus was hidden.
                elif start_time_found:
                    end_time = int(previous_row['gaze_data_time_stamp'])
                    RT_data.append(str((end_time - start_time) / 1000.0).replace(".", ","))
                else:
                    RT_data.append("0")

            last_trial = str(row['trial'])
            start_time_found = False
            end_time_found = False

        # stimulus appears on the screen -> start time
        if row['trial_phase'] == "stimulus_on_screen" and not start_time_found:
            start_time = int(row['gaze_data_time_stamp'])
            start_time_found = True

        # stimulus disappear from the screen -> end time
        if row['trial_phase']== "after_reaction" and not end_time_found:
            end_time = int(previous_row['gaze_data_time_stamp'])
            end_time_found = True

        previous_row = row

    return RT_data

def calcPupilColumn(raw_file_name):
    input_data = pandas.read_csv(raw_file_name, sep='\t')

    trial_column = input_data['trial']
    block_column = input_data['block']
    left_pupil_validity_column = input_data['left_pupil_validity']
    right_pupil_validity_column = input_data['right_pupil_validity']
    left_pupil_diameter_column = input_data['left_pupil_diameter']
    right_pupil_diameter_column = input_data['right_pupil_diameter']
    time_stamp_column = input_data['gaze_data_time_stamp']

    last_trial = "0"
    pupil_data = []
    pupil_time_data = []

    # get a 1250 ms time series for this trial (120 Hz -> 1250 ms = 150 samples)
    trial_sample_count = 150

    for i in range(len(trial_column)):
        # we ignore 0 indexed blocks, which are calibration validation blocks.
        if str(block_column[i]) == '0':
            continue

        # we are at the beginning of the next trial
        if last_trial != str(trial_column[i]):
            last_trial = str(trial_column[i])

            j = i
            trial_pupil_data = []
            while len(trial_pupil_data) < trial_sample_count and j < len(trial_column):
                left_pupil_valid = left_pupil_validity_column[j]
                right_pupil_valid = right_pupil_validity_column[j]
                left_pupil_size = convertToFloat(left_pupil_diameter_column[j])
                right_pupil_size = convertToFloat(right_pupil_diameter_column[j])

                # use the valid data only
                if left_pupil_valid and right_pupil_valid:
                    new_data = (left_pupil_size + right_pupil_size) / 2.0
                elif left_pupil_valid:
                    new_data = left_pupil_size
                elif right_pupil_valid:
                    new_data = right_pupil_size
                else:
                    new_data = float('nan')
                j += 1
                trial_pupil_data.append(new_data)

            # we can calculate the actual duration of 150 samples -> can be used for filtering extreme data.
            time_window = int(time_stamp_column[j - 1]) - int(time_stamp_column[i])

            if (len(trial_pupil_data) != trial_sample_count or # we reached the end of the file
			   (j < len(trial_column) and block_column[i] != block_column[j])): # we reached the end of the block
                pupil_data.append([])
                pupil_time_data.append(0)
                continue

            # drop useless data, we have 40 Hz actual frequency for pupil size
            # so we need every third item, but first need to find which indexes to use
            valid_data_index = -1
            for j in range(len(trial_pupil_data)):
                if not math.isnan(trial_pupil_data[j]) and trial_pupil_data[j] > 0.0:
                    valid_data_index = j
                    break

            # no valid data inside this time window
            if valid_data_index == -1:
                pupil_data.append([])
                pupil_time_data.append(0)
                continue

            trial_actual_pupil_data = []
            first_data = valid_data_index % 3
            for j in range(valid_data_index % 3, len(trial_pupil_data), 3):
                trial_actual_pupil_data.append(trial_pupil_data[j])

            assert(len(trial_actual_pupil_data) == int(trial_sample_count / 3))
            pupil_data.append(trial_actual_pupil_data)
            pupil_time_data.append(time_window)

    return pupil_data, pupil_time_data

def generateTrialData(raw_file_name, new_file_name):
    RT_data = calcRTColumn(raw_file_name)
    pupil_data, pupil_time_data = calcPupilColumn(raw_file_name)
    generateOutput(raw_file_name, new_file_name, RT_data, pupil_data, pupil_time_data)