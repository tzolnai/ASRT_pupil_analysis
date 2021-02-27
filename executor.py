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

import shutil
import os
import sys
import time

import calc_trial_data as ctd
import extend_trial_data as etd
import compute_learning as cl
import compute_extreme_RT as cert
import filter_data as fd
import outlier_calculator as oc
import extract_pupil_data as epa
import calc_pupil_baseline as cpb

def setupOutputDir(dir_path):
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
        time.sleep(.001)

    os.makedirs(dir_path)
    if not os.path.isdir(dir_path):
        print("Could not make the output folder: " + dir_path)
        exit(1)

def compute_trial_data(input_dir, output_dir):
    setupOutputDir(output_dir)

    for root, dirs, files in os.walk(input_dir):
        for subject_dir in dirs:
            if subject_dir.startswith('.'):
                continue

            raw_data_path = os.path.join(root, subject_dir, 'subject_' + subject_dir + '__log.txt')
            trial_data_path = os.path.join(output_dir, 'subject_' + subject_dir + '__trial_log.txt')
            ctd.generateTrialData(raw_data_path, trial_data_path)

        break

def extend_trial_data(input_dir, output_dir):
    setupOutputDir(output_dir)

    for root, dirs, files in os.walk(input_dir):
        for file in files:

            input_file = os.path.join(input_dir, file)
            output_file = os.path.join(output_dir, os.path.splitext(file)[0] + '_extended.txt')
            etd.extendTrialData(input_file, output_file)

        break

def filter_data_high_low(input_dir, output_dir):
    setupOutputDir(output_dir)

    filtered_subjects = [14, 17, 37, 39, # a lot of extreme RT -> bad ET accuracy
                        27, 47] # bad learning measure

    all_data_count = 0

    for root, dirs, files in os.walk(input_dir):
        for file in files:

            input_file = os.path.join(input_dir, file)
            subject = int(file.split('_')[1])
            if subject not in filtered_subjects:
                output_file = os.path.join(output_dir, os.path.splitext(file)[0] + '_filtered.txt')
                all_data_count += fd.filterData(input_file, output_file, [4, 5])
        break

    print('Final data count after filtering: ' + str(all_data_count))

def filter_data_before_after(input_dir, output_dir):
    setupOutputDir(output_dir)

    filtered_subjects = [14, 17, 37, 39, # a lot of extreme RT -> bad ET accuracy
                        27, 47] # bad learning measure

    all_data_count = 0

    for root, dirs, files in os.walk(input_dir):
        for file in files:

            input_file = os.path.join(input_dir, file)
            subject = int(file.split('_')[1])
            if subject not in filtered_subjects:
                output_file = os.path.join(output_dir, os.path.splitext(file)[0] + '_filtered.txt')
                all_data_count += fd.filterData(input_file, output_file, [1, 5])
        break

    print('Final data count after filtering: ' + str(all_data_count))

def compute_learning_measure(input_dir, output_dir):
    setupOutputDir(output_dir)

    output_file = os.path.join(output_dir, 'RT_learning_measures.txt')
    cl.computeLearningMeasure(input_dir, output_file)

def compute_extreme_RT(input_dir, output_dir):
    setupOutputDir(output_dir)

    output_file = os.path.join(output_dir, 'extreme_RT_avarages.txt')
    cert.computeExtremeRTAverages(input_dir, output_file)

def compute_outliers(input_dir, output_dir):
    setupOutputDir(output_dir)

    oc.calcOutlierBounds(input_dir, output_dir)

def compute_pupil_data_HL(input_dir, output_dir):
    setupOutputDir(output_dir)

    output_file = os.path.join(output_dir, 'pupil_data_HL.txt')
    epa.extractPupilDataHL(input_dir, output_file)

def compute_pupil_data_BA(input_dir, output_dir):
    setupOutputDir(output_dir)

    output_file = os.path.join(output_dir, 'pupil_data_BA.txt')
    epa.extractPupilDataBA(input_dir, output_file)


def compute_pupil_baseline(input_dir, output_dir):
    setupOutputDir(output_dir)

    baseline_output_file = os.path.join(output_dir, 'pupil_baselines.txt')
    std_output_file = os.path.join(output_dir, 'pupil_stds.txt')
    cpb.generatePupilBaseline(input_dir, baseline_output_file, std_output_file)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("You need to specify an input folder for data files.")
        exit(1)

    if not os.path.isdir(sys.argv[1]):
        print("The passed first parameter should be a valid directory path: " + sys.argv[1])
        exit(1)

    script_dir = os.path.dirname(os.path.realpath(__file__))
    RT_data_dir = os.path.join(script_dir, 'data', 'trial_data')

    compute_trial_data(sys.argv[1], RT_data_dir)

    extended_trial_data_dir = os.path.join(script_dir, 'data', 'trial_data_extended')

    extend_trial_data(RT_data_dir, extended_trial_data_dir)

    learning_data_dir = os.path.join(script_dir, 'data', 'learning_data')

    compute_learning_measure(extended_trial_data_dir, learning_data_dir)

    extreme_RT_dir = os.path.join(script_dir, 'data', 'extreme_RT_data')

    compute_extreme_RT(extended_trial_data_dir, extreme_RT_dir)

    outlier_dir = os.path.join(script_dir, 'data', 'outlier_data')
    compute_outliers(extended_trial_data_dir, outlier_dir)

    filter_data_HL_dir = os.path.join(script_dir, 'data', 'filtered_data_HL')
    filter_data_high_low(extended_trial_data_dir, filter_data_HL_dir)

    filter_data_BA_dir = os.path.join(script_dir, 'data', 'filtered_data_BA')
    filter_data_before_after(extended_trial_data_dir, filter_data_BA_dir)

    pupil_data_HL_dir = os.path.join(script_dir, 'data', 'pupil_data_HL')
    compute_pupil_data_HL(filter_data_HL_dir, pupil_data_HL_dir)

    pupil_data_BA_dir = os.path.join(script_dir, 'data', 'pupil_data_BA')
    compute_pupil_data_BA(filter_data_BA_dir, pupil_data_BA_dir)
    
    pupil_baseline_dir = os.path.join(script_dir, 'data', 'pupil_baseline')
    compute_pupil_baseline(sys.argv[1], pupil_baseline_dir)
