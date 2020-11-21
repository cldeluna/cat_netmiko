#!/usr/bin/python -tt
# Project: cat_netmiko
# Filename: ping_check
# claudia
# PyCharm

from __future__ import absolute_import, division, print_function

__author__ = "Claudia de Luna (claudia@indigowire.net)"
__version__ = ": 1.0 $"
__date__ = "11/21/20"
__copyright__ = "Copyright (c) 2018 Claudia"
__license__ = "Python"

import argparse
import datetime
import os
import utils



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

    json_files_to_process = utils.get_file_list(path, ".json", debug=True)

    not_pingable_dict = {}
    for file in json_files_to_process:

        # Looad devices in JSON file
        devs = utils.read_json(file, debug=False)

        temp_failed_ping_list = []
        print(f"\n\nPing Verification for {file}")
        for dev in devs:
            ping_result = utils.ping_device(dev, debug=False)
            print(f"\t {dev} ping result is {ping_result}")
            if not ping_result:
                temp_failed_ping_list.append(dev)


        not_pingable_dict.update({file: temp_failed_ping_list})

    print(f"\n\n====== SUMMARY of Failed Pings ========")
    for k,v in not_pingable_dict.items():
        print(f"Device File: {k}")
        for d in v:
            print(f"\t{d}")




# Standard call to the main() function.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Script Description",
                                     epilog="Usage: ' python ping_check' ")
    parser.add_argument('filename_or_dir', help='filename or directory of files to parse')
    parser.add_argument('-e', '--extension', action='store', default=False, help='Valid file extension in format '
                                                                                 '".xxx" or comma delimited '
                                                                                 '".txt, .fil" Default values if '
                                                                                 'option not give are .txt and .log')

    arguments = parser.parse_args()
    main()
