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
import logging
import sys



def main():

    # Timestamp the start of the run so that a total run time can be calcuated at the end
    start_time = datetime.datetime.now()

    #Date stamp for log file
    datestamp = datetime.date.today()

    file_timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    # https://www.kite.com/python/answers/how-to-print-logging-messages-to-both-stdout-and-to-a-file-in-python
    output_loger = logging.getLogger()
    output_loger.setLevel(logging.DEBUG)

    output_log_fn = f"Log_{arguments.filename_or_dir}_{file_timestamp}.txt"
    output_file_handler = logging.FileHandler(output_log_fn)
    stdout_handler = logging.StreamHandler(sys.stdout)

    output_loger.addHandler(output_file_handler)
    output_loger.addHandler(stdout_handler)

    output_loger.debug(f"\nPing Run for Directory {arguments.filename_or_dir} on {file_timestamp}\n")
    output_loger.debug(f"\nPing Run Message: {arguments.message}\n")

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

        startt = datetime.datetime.now()

        # Looad devices in JSON file
        devs = utils.read_json(file, debug=False)

        temp_failed_ping_list = []
        output_loger.debug(f"\n\nPing Verification for {file}")
        # print(f"\n\nPing Verification for {file}")
        # Ping Test Timestamp
        output_loger.debug(f"\tPings started at {datetime.datetime.now()}\n")
        # print(f"Pings started at {datetime.datetime.now()}\n")
        for dev in devs:
            ping_result = utils.ping_device(dev, debug=False)
            output_loger.debug(f"\t{dev} ping result is {ping_result}")
            # print(f"\t{dev} ping result is {ping_result}")
            if not ping_result:
                temp_failed_ping_list.append(dev)

        not_pingable_dict.update({file: temp_failed_ping_list})

        # Ping Test Timestamp
        output_loger.debug(f"\n\tPings completed at {datetime.datetime.now()}")
        # print(f"\n\tPings completed at {datetime.datetime.now()}")
        # Script Execution Time
        output_loger.debug(f"\tPing Execution Time for {file}: {datetime.datetime.now() - startt}\n")
        # print(f"\tPing Execution Time for {file}: {datetime.datetime.now() - start}\n")

    output_loger.debug(f"\n\n====== SUMMARY of Failed Pings ========")
    # print(f"\n\n====== SUMMARY of Failed Pings ========")
    for k,v in not_pingable_dict.items():
        output_loger.debug(f"\nDevice File: {k}")
        # print(f"\nDevice File: {k}")
        if len(v) == 0:
            output_loger.debug(f"\tAll devices ping!")
            # print(f"\tAll devices ping!")
        else:
            for d in v:
                output_loger.debug(f"\t{d} failed to respond to pings!")
                # print(f"\t{d} failed to respond to pings!")

    output_loger.debug(f"\nScript Execution Time: {datetime.datetime.now() - start_time}\n")



# Standard call to the main() function.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Script Description",
                                     epilog="Usage: ' python ping_check' ")
    parser.add_argument('filename_or_dir', help='filename or directory of files to parse')
    parser.add_argument('-e', '--extension', action='store', default=False, help='Valid file extension in format '
                                                                                 '".xxx" or comma delimited '
                                                                                 '".txt, .fil" Default values if '
                                                                                 'option not give are .txt and .log')
    parser.add_argument('-m', '--message', action='store', default=f"Ping Run on {datetime.datetime.now()}",
                        help='Optional Descriptive message for ping run')
    arguments = parser.parse_args()
    main()
