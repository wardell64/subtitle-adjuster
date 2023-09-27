"""
Subtitle adjustment script
"""
import getopt
import os
import shutil
import sys
from datetime import datetime as dt
from datetime import timedelta as td
from enum import Enum


class ShiftType(Enum):
    """
    Shift Types
    """
    AUTO = 1
    LEFT = 2
    RIGHT = 3


def main(argv):
    """
    Stuff
    :param argv:
    :return:
    """
    input_file = ''
    shift_direction = None
    seconds = 0
    milliseconds = 0
    stretch_factor = 1.0

    opts, args = getopt.getopt(argv, "hi:d:s:m:f:", ["input=", "direction", "right", "seconds=", "milliseconds=", "factor="])  # pylint: disable=unused-variable
    for opt, arg in opts:
        if opt == '-h':
            print('subtitle.py -i <input_file> -type  -seconds <seconds> -milliseconds <milliseconds> -factor <float>')
            sys.exit()
        elif opt in ("-i", "--input"):
            input_file = arg
        elif opt in ("-d", "--direction"):
            shift_direction = determine_shift_direction(arg)
        elif opt in ("-s", "--seconds"):
            seconds = int(arg)
        elif opt in ("-m", "--milliseconds"):
            milliseconds = int(arg)
        elif opt in ("-f", "--factor"):
            stretch_factor = float(arg)

    if not os.path.isfile(input_file):
        print(f"File does not exist: {input_file}")
        sys.exit()

    # if shift_direction is not None:
    #     print(f"Malformed direction {shift_direction.name}")
    #     sys.exit()

    process_inputs(input_file, milliseconds, seconds, shift_direction, stretch_factor)


def determine_shift_direction(arg):
    """

    :param arg:
    :return:
    """
    if arg.lower() in ['left', 'l']:
        return ShiftType.LEFT
    if arg.lower() in ['right', 'r']:
        return ShiftType.RIGHT
    if arg.lower() in ['auto', 'a']:
        return ShiftType.AUTO
    print(f"Could not parse direction {arg}")
    sys.exit()


def process_inputs(input_file, milliseconds, seconds, shift_direction, stretch_factor):
    """
    
    :param input_file: 
    :param milliseconds: 
    :param seconds: 
    :param shift_direction: 
    :param stretch_factor: 
    :return: 
    """
    print("=== Arguments ===")
    print(f'Input file: {input_file}')
    if shift_direction is not None:
        print(f'Input Shift Direction: {shift_direction}')
        print(f'Input Time {seconds}:{milliseconds}')
        shift_amount = td(seconds=seconds, milliseconds=milliseconds)
    if stretch_factor is not None:
        print(f'Input Stretch Factor {stretch_factor}')
    file_path = os.path.abspath(input_file)
    folder_path = os.path.dirname(file_path)
    # filename = os.path.basename(file_path)
    backup_file_path = file_path.replace(r'M:', r'M:\Backup')
    backup_folder_path = folder_path.replace(r'M:', r'M:\Backup')
    print("\r")
    print("=== Operation Values ===")
    if shift_direction is not None:
        print(f'Direction: {shift_direction}')
    if shift_amount is not None:
        print(f'Shift Amount {shift_amount}')
    if stretch_factor is not None:
        print(f'Stretch Factor {stretch_factor}')
    print("\r")
    print("=== File Paths ===")
    print(f'Input file path : {file_path}')
    print(f'Input folder path : {folder_path}')
    print(f'Backup file path : {backup_file_path}')
    print(f'Backup folder path : {backup_folder_path}')
    print("\r")
    print("=== Script Output ===")
    if os.path.isfile(backup_file_path):
        print(f"Found a backup at {backup_file_path}")
        print("Using backup as input")
    else:
        print(f"Create backup at {backup_file_path}")
        if not os.path.isdir(backup_folder_path):
            print(f"Create folder at {backup_folder_path}")
            os.makedirs(backup_folder_path)
        shutil.copy2(file_path, backup_file_path)
    subs_factor_stretch(backup_file_path, file_path, stretch_factor, shift_direction, shift_amount)


def subs_factor_stretch(input_path, output_path, stretch_factor=None, shift_direction=None, shift_amount=None):
    """
    Opens and adjusts subtitles
    :param input_path:
    :param output_path:
    :param stretch_factor:
    :param shift_direction:
    :param shift_amount:
    :return:
    """
    with open(input_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()  # read all lines as a list
    with open(output_path, 'w', encoding='utf-8') as file:  # open new file
        for line in lines:  # iterate over lines
            if '-->' in line:
                # if line contains -->, split it
                subs_line = line.split('-->')
                for sub_index, sub in enumerate(subs_line):  # pylint: disable=unused-variable
                    # shift
                    time_string = subs_line[sub_index].strip()
                    time_string = time_string.replace(',', '.')  # replacing coma with dot
                    # converting to datetime object
                    time_dt = dt.strptime(time_string, '%H:%M:%S.%f')

                    if shift_direction is not None:
                        if shift_direction == ShiftType.AUTO:
                            shift_amount = time_dt - dt(1900, 1, 1)
                            print(f'New Shift Amount {shift_amount}')
                            shift_direction = ShiftType.LEFT
                        if shift_direction == ShiftType.RIGHT:
                            time_dt = time_dt + shift_amount
                        elif shift_direction == ShiftType.LEFT:
                            time_dt = time_dt - shift_amount
                    if stretch_factor is not None:
                        time_dt = time_dt - dt(1900, 1, 1)  # converting to seconds
                        time_dt *= stretch_factor  # adjusting the time
                        time_dt = dt(1900, 1, 1) + time_dt  # converting back to datetime object

                    # apply stretch function to each sub
                    subs_line[sub_index] = time_dt.strftime('%H:%M:%S,%f')[:-3]  # convert to string
                    # join the list of 2 subs
                    line = f'{subs_line[0]} --> {subs_line[1]}\n'
            file.write(line)  # write the line to the new file


if __name__ == "__main__":
    main(sys.argv[1:])
