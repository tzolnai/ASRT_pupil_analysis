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

def computeRepetitionColumn(data_table):
    repetition_column = []
    stimulus_column = data_table["stimulus"]

    for i in range(len(stimulus_column)):
        if i > 0 and stimulus_column[i] == stimulus_column[i - 1]:
            repetition_column.append(True)
        else:
            repetition_column.append(False)

    return repetition_column

def computeMissingData(data_table):
    missing_data_column = []
    pupil_data_column = data_table["pupil_data"]

    for i in range(len(pupil_data_column)):
        missing_data_count = 0
        pupil_data = pupil_data_column[i].strip('][').split(', ')
        for j in range(len(pupil_data)):
            if str(pupil_data[j]) == 'nan':
                missing_data_count += 1

        missing_data_column.append(missing_data_count)

    return missing_data_column

def computeMissingDataStreak(data_table):
    missing_data_streak_column = []
    pupil_data_column = data_table["pupil_data"]

    for i in range(len(pupil_data_column)):
        max_streak = 0
        missing_data_streak_count = 0
        pupil_data = pupil_data_column[i].strip('][').split(', ')
        for j in range(len(pupil_data)):
            if str(pupil_data[j]) == 'nan':
                missing_data_streak_count += 1
            else:
                missing_data_streak_count = 0

            if max_streak < missing_data_streak_count:
                max_streak = missing_data_streak_count
        missing_data_streak_column.append(max_streak)

    return missing_data_streak_column

def extendTrialData(input_file, output_file):
    data_table = pandas.read_csv(input_file, sep='\t')

    # previous trial has the stimulus at the same position -> repetition.
    repetition_data = computeRepetitionColumn(data_table)
    assert(len(repetition_data) == len(data_table.index))
    data_table["repetition"] = repetition_data

    # count all missing data in a trial's pupil data array.
    missing_data = computeMissingData(data_table)
    assert(len(missing_data) == len(data_table.index))
    data_table["missing_pupil_data_count"] = missing_data

    # compute the biggest missing data gap in a trial's pupil data array.
    missing_data_streak = computeMissingDataStreak(data_table)
    assert(len(missing_data_streak) == len(data_table.index))
    data_table["missing_pupil_data_maxgap"] = missing_data_streak

    data_table.to_csv(output_file, sep='\t', index=False)
