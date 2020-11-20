#!/usr/bin/python -tt
# Project: cat_netmiko
# Filename: x_multi_json
# claudia
# PyCharm

from __future__ import absolute_import, division, print_function

__author__ = "Claudia de Luna (claudia@indigowire.net)"
__version__ = ": 1.0 $"
__date__ = "11/20/20"
__copyright__ = "Copyright (c) 2018 Claudia"
__license__ = "Python"

import argparse
import utils
import datetime
import re
import os
import sys


def get_file_list(pth, ext='', debug=True):

    # Initialize list of all valid files
    file_list = []

    valid_file_extenstion = []
    if ext:
        valid_file_extenstion.append(ext)
    else:
        valid_file_extenstion.append(".txt")
        valid_file_extenstion.append(".log")

    if os.path.exists(pth):
        # Check to see if the argument is a directory
        if os.path.isdir(pth):
            print("Processing Directory: " + pth + " for all files with the following extensions: " + str(valid_file_extenstion))
            file_list, total_files = utils.read_files_in_dir(pth, valid_file_extenstion)
            print("\t Total files in directory: " + str(len(total_files)))
            print("\t Valid files in directory: " + str(len(file_list)))

        else:
            print("Processing File: " + pth)
            file_list.append(pth)

    else:
        print("Problem with path or filename! {}".format(pth))
        sys.exit("Aborting Program Execution due to bad file or directory argument.")

    return file_list


def main():

    # Timestamp the start of the run so that a total run time can be calcuated at the end
    start_time = datetime.datetime.now()


    # Keep a list of any files that did not have any output information
    no_output = []

    utils.load_environment(debug=False)

    # Get the current working directory to store the zip files
    curr_dir = os.getcwd()

    # Mandatory argument passed to script - either a filename or a directory of files to process
    path = arguments.filename_or_dir

    json_files_to_process = get_file_list(path, ".json", debug=True)



    for file in json_files_to_process:

        # Looad devices in JSON file
        devs = utils.read_json(file, debug=False)

        # Derive Subdirectory to save to
        subdir = utils.get_filename_wo_extension(file, debug=False)

        utils.get_and_zip_output(devs, subdir, debug=False)



# Standard call to the main() function.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Script Description",
                                     epilog="Usage: ' python x_multi_json' ")

    parser.add_argument('filename_or_dir', help='filename or directory of files to parse')
    parser.add_argument('-e', '--extension', action='store', default=False, help='Valid file extension in format '
                                                                                 '".xxx" or comma delimited '
                                                                                 '".txt, .fil" Default values if '
                                                                                 'option not give are .txt and .log')
    arguments = parser.parse_args()
    main()
