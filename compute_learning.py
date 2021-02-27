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
import statistics

def calcBlockMedianRTs(input_file):
    input_data_table = pandas.read_csv(input_file, sep='\t')

    RT_column = input_data_table["RT (ms)"]
    repetition_column = input_data_table["repetition"]
    block_column = input_data_table["block"]
    trial_column = input_data_table["trial"]
    trial_type_column = input_data_table["triplet_type_hl"]

    assert(len(RT_column) == len(repetition_column))
    assert(len(RT_column) == len(block_column))
    assert(len(RT_column) == len(trial_column))
    assert(len(RT_column) == len(trial_type_column))

    current_block = block_column[0]
    high_RT_list = []
    low_RT_list = []
    high_median_array = []
    low_median_array = []
    for i in range(len(RT_column) + 1):
        # end of the block -> calc median for low and high trials
        if i == len(RT_column) or current_block != block_column[i]:
            if len(high_RT_list) > 0:
                high_median_array.append(statistics.median(high_RT_list))
                high_RT_list = []
            else:
                # the first 5 block has no high-low labelled trials
                assert(int(current_block) <= 5)
                high_median_array.append(-1.0)

            if len(low_RT_list) > 0:
                low_median_array.append(statistics.median(low_RT_list))
                low_RT_list = []
            else:
                # the first 5 block has no high-low labelled trials
                assert(int(current_block) <= 5)
                low_median_array.append(-1.0)

            if i == len(RT_column):
                break

            current_block = block_column[i]

        # we ignore the first two trials and also repetition
        if trial_column[i] > 2 and repetition_column[i] == False:
            if trial_type_column[i] == 'high':
                high_RT_list.append(float(RT_column[i].replace(",", ".")))
            elif trial_type_column[i] == 'low':
                low_RT_list.append(float(RT_column[i].replace(",", ".")))

    # 8 epoch * 5 block
    assert(len(low_median_array) == 40)
    assert(len(high_median_array) == 40)
    return low_median_array, high_median_array

# we use the frequency of those blocks where median of high-frequency triplets were
# smaller then the low frequency triplets.
def calcLearningMeasure(low_medians, high_medians):
    lowBigger = 0
    for i in range(5, 30):
        if low_medians[i] > high_medians[i]:
            lowBigger += 1

    return str(lowBigger).replace('.',',')

def computeLearningMeasure(input_dir, output_file):
    learning_measure = []
    subjects = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:

            input_file = os.path.join(input_dir, file)
            subject = int(file.split('_')[1])
            subjects.append(subject)

            low_medians, high_medians = calcBlockMedianRTs(input_file)
            learning_measure.append(calcLearningMeasure(low_medians, high_medians))
        break

    sign_test_data = pandas.DataFrame({'subject' : subjects, 'learning_measure': learning_measure})
    sign_test_data.to_csv(output_file, sep='\t', index=False)
