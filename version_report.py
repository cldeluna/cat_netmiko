#!/usr/bin/python -tt
# Project: cat_netmiko
# Filename: version_report
# claudia
# PyCharm

from __future__ import absolute_import, division, print_function

__author__ = "Claudia de Luna (claudia@indigowire.net)"
__version__ = ": 1.0 $"
__date__ = "12/23/20"
__copyright__ = "Copyright (c) 2018 Claudia"
__license__ = "Python"

import argparse
import datetime
import logging
import sys
import os
import re
import json
import utils
import pprint
from icecream import ic


def version_report(arguments, debug=False):

    if debug:
        print("in function")
        print(arguments)
        print(arguments.region)
        print(arguments.site_id)
    # Timestamp the start of the run so that a total run time can be calcuated at the end
    start_time = datetime.datetime.now()

    #Date stamp for log file
    # datestamp = datetime.date.today()
    file_timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    # Get the Local current working directory
    curr_dir = os.getcwd()
    # Set the NTC Template repository full path nder the current working directory
    fsm_path = os.path.join(curr_dir, "ntc-templates", "templates")

    # Keep a list of any files that did not have any output information
    no_output = []

    # ########### Set up show command directory selection
    # Set Project Folder Structure Root Path by User Logged In
    root_path = utils.set_base_by_user(debug=True)
    base_path = os.path.join(root_path,"Sites")
    if debug:
        print(f"Base path is {base_path}")
    site_path = utils.find_site_root(base_path, arguments.region, arguments.site_id,
                                                disamabig_dir=arguments.directory)
    showcmd_dir = os.path.join(site_path, '01_Analysis', 'show_cmds')
    if debug:
        print(f"site_path is {site_path} \nshow command dir path is {showcmd_dir}\n")

    # FInd the site Name and deployment JSON file
    site_name = os.path.basename(site_path)

    # ## SET UP LOGGER
    # https://www.kite.com/python/answers/how-to-print-logging-messages-to-both-stdout-and-to-a-file-in-python
    output_logger = logging.getLogger()
    output_logger.setLevel(logging.DEBUG)

    if arguments.directory:
        output_log_fn = f"Cat_{arguments.directory}_IOS_Report_{file_timestamp}.txt"
    else:
        output_log_fn = f"Cat_{site_name}_IOS_Report_{file_timestamp}.txt"
    output_file_handler = logging.FileHandler(output_log_fn)
    stdout_handler = logging.StreamHandler(sys.stdout)

    output_logger.addHandler(output_file_handler)
    output_logger.addHandler(stdout_handler)

    output_logger.debug(f"\nLAN and WLAN Software Upgrade Verification for {arguments.region} {arguments.site_id} {site_name} on {file_timestamp}\n")
    # output_loger.debug(f"Ping Run Message: {arguments.message}\n")

    # ######### Set up Valid File Extension
    valid_file_extenstion = []
    if arguments.extension:
        extensions = arguments.extension
        extensions = re.sub(r'\s+', '', extensions)
        extensions = re.split(r'[;|,|\s]?', extensions)

        for ext in extensions:
            valid_file_extenstion.append(ext)
    else:
        valid_file_extenstion.append(".txt")
        valid_file_extenstion.append(".log")

    dir_list = os.listdir(showcmd_dir)
    pre_dir_path = ''
    post_dir_path = ''
    for a_dir in dir_list:
        dir_path = os.path.join(showcmd_dir, a_dir)
        # print(a_dir)
        if os.path.isdir(dir_path):
            if re.search("PRE", dir_path):
                # print(dir_path)
                pre_dir_path = dir_path
            if re.search("POST", dir_path):
                # print(dir_path)
                post_dir_path = dir_path

    ic(pre_dir_path)

    shcmd_dir = cat_config_utils.generic_select_dir(
        showcmd_dir, "Select Show Command DIR:", debug=False
    )
    # print(shcmd_dir)


    # Get all files in directory

    file_list = utils.get_files_in_dir(pre_dir_path, ext=".txt", debug=False)
    if debug:
        print(file_list)
    ver_pre_post_dict = {}

    # ################################# PRE PRE PRE PRE RE PRE PRE PRE LOOP for each show cmd file in PRE dir
    for shcmd_file in file_list:

        temp_dict = {}
        pre_dict = {}
        wlc_pre_dict = {}
        hostname_from_file = utils.get_hostname_from_filename(shcmd_file)

        if not re.search('wlc', hostname_from_file):

            ############  PARSE SHOW VER PRE
            # output_logger.debug(f"\n   - PRE Version Check for Device {hostname_from_file}")
            # Set the show version textfsm template for parsing
            fsm_template = "cisco_ios_show_version.textfsm"

            # Define the fsm_processing)dictionary for the process_file_section function which will pull out the relevant
            # section of the show commands to parse
            fsm_processing_dict = {}
            fsm_processing_dict['filename_or_dir'] = shcmd_file
            fsm_processing_dict['fsm_template'] = fsm_template
            fsm_processing_dict['extension'] = ".txt"
            fsm_processing_dict['string_start'] = r".+ sh(ow)? ver(sion)?"
            fsm_processing_dict['string_end'] = r"^Configuration register is"

            table = utils.process_file_section(fsm_processing_dict, debug=False)
            # print(table)

            # if there are results set temp_dict the innermost dictionary
            if table:
                temp_dict.update({'version': f"{table[0][1]} {table[0][0]}"})
                temp_dict.update({'hostname': table[0][2]})
                temp_dict.update({'image': table[0][5]})
                temp_dict.update({'model': table[0][6]})
                temp_dict.update({'stack_size': len(table[0][6])})

            # set the innermost dict as the value of an outer dict for PRE data
            pre_dict.update({'pre': temp_dict})

            # define the outermost dictionary key of the host.
            ver_pre_post_dict.update({hostname_from_file: pre_dict})

            # ######### Look for WLCs
            wlc_temp_dict = {}
            fsm_template = "cisco_ios_show_cdp_neighbors_detail.textfsm"
            fsm_processing_dict['fsm_template'] = fsm_template
            fsm_processing_dict['string_start'] = r"^!--- show cd nei det "
            fsm_processing_dict['string_end'] = r"^Total cdp entries displayed :"

            table = utils.process_file_section(fsm_processing_dict, debug=False)

            if table:
                # Iterate through the cdp data to find any WLCs
                for line in table:
                    # if wlc is in the hostname
                    if re.search('wlc', line[0]):
                        # print(line)
                        wlc_name = line[0]
                        wlc_temp_dict.update({'version': line[5]})
                        wlc_temp_dict.update({'hostname': wlc_name})
                        wlc_temp_dict.update({'image': 'aes'})
                        wlc_temp_dict.update({'model': [line[2]]})
                        wlc_temp_dict.update({'stack_size': 1})

                        wlc_pre_dict.update({'pre': wlc_temp_dict})

                        # if wlc_name in ver_pre_post_dict.keys():
                        #     wlc_temp = ver_pre_post_dict[wlc_name]
                        #     # print(wlc_temp)
                        #     ver_pre_post_dict[wlc_name].update(wlc_temp)
                        # else:
                        # print(f"\n================  wlc_name {wlc_name}")
                        # print(wlc_temp_dict)
                        # print(wlc_pre_dict)

                        ver_pre_post_dict.update({wlc_name: wlc_pre_dict})
                        # print('----- full dict')
                        # pprint.pprint(ver_pre_post_dict)
                        # # print(ver_pre_post_dict)
                        # print()


    # print(ver_pre_post_dict)
    # print(ver_pre_post_dict.keys())
    # for k,v in ver_pre_post_dict.items():
    #     print(k)
    #     print(f"\t{v}\n")
    # print(c)
    # Get all files in directory
    file_list = utils.get_files_in_dir(post_dir_path, ext=".txt", debug=False)
    # print(file_list)

    # ## POST
    for shcmd_file in file_list:

        temp_dict = {}
        post_dict = {}
        hostname_from_file = utils.get_hostname_from_filename(shcmd_file)

        if not re.search('wlc', hostname_from_file):

            ############  PARSE SHOW VER PRE
            # !--- show spanning-tree
            # !--- show int  or !--- show spanning-tree root priority system-id
            # output_logger.debug(f"\n   - POST Version Check for Device {hostname_from_file}")
            # print(f"\n---- Checking Spanning Tree")
            fsm_template = "cisco_ios_show_version.textfsm"
            template_full_path = os.path.join(fsm_path, fsm_template)
            data_fh, data = utils.open_read_file(shcmd_file)
            # stp_parsed_data, stp_table_object = cat_config_utils.text_fsm_parse(template_full_path, data)
            # print(f"\tTextFMS Template full path: {template_full_path}")
            # print(stp_parsed_data)
            # print(stp_table_object.header)

            fsm_processing_dict = {}
            fsm_processing_dict['filename_or_dir'] = shcmd_file
            fsm_processing_dict['fsm_template'] = fsm_template
            fsm_processing_dict['extension'] = ".txt"
            fsm_processing_dict['string_start'] = r".+ sh(ow)? ver(sion)?"
            fsm_processing_dict['string_end'] = r"^Configuration register is"

            table = utils.process_file_section(fsm_processing_dict, debug=False)

            if table:
                temp_dict.update({'version': f"{table[0][1]} {table[0][0]}"})
                temp_dict.update({'hostname': table[0][2]})
                temp_dict.update({'image': table[0][5]})
                temp_dict.update({'model': table[0][6]})
                temp_dict.update({'stack_size': len(table[0][6])})

            post_dict.update({'post': temp_dict})

            temp = ver_pre_post_dict[hostname_from_file]
            # print(temp)
            ver_pre_post_dict[hostname_from_file].update(post_dict)

            # ######### Look for WLCs POST
            wlc_temp_dict = {}
            wlc_post_dict = {}
            fsm_template = "cisco_ios_show_cdp_neighbors_detail.textfsm"
            fsm_processing_dict['fsm_template'] = fsm_template
            fsm_processing_dict['string_start'] = r"^!--- show cd nei det "
            fsm_processing_dict['string_end'] = r"^Total cdp entries displayed :"

            table = utils.process_file_section(fsm_processing_dict, debug=False)

            if table:
                for line in table:
                    wlc_temp = {}
                    if re.search('wlc', line[0]):
                        # print(line)
                        wlc_name = line[0]
                        wlc_temp_dict.update({'version': line[5]})
                        wlc_temp_dict.update({'hostname': wlc_name})
                        wlc_temp_dict.update({'image': 'aes'})
                        wlc_temp_dict.update({'model': [line[2]]})
                        wlc_temp_dict.update({'stack_size': 1})

                        wlc_post_dict.update({'post': wlc_temp_dict})

                        wlc_temp = ver_pre_post_dict[wlc_name]
                        # print(wlc_temp)
                        ver_pre_post_dict[wlc_name].update(wlc_post_dict)

    # ########## MAIN REPORT BODY #########################################
    model = ''
    for k, v in ver_pre_post_dict.items():

        if re.search(r'-c?ds?\d\d', k) or re.search(r'-as\d\d', k) or re.search(r'-wlc', k):
            output_logger.debug(f"\n\t--- Version Check for Device {k}")
            # print(v)
            if v['pre']:
                model = v['pre']['model'][0]
                output_logger.debug(f"\tModel: ")
                for dev in v['pre']['model']:
                    output_logger.debug(f"\t\t{dev}: ")
                if re.search('3850', model):
                    output_logger.debug(f"\tAccess Stack Size: {v['post']['stack_size']}")
                output_logger.debug(f"\tPre Upgrade Version: {v['pre']['version']}")
                if re.search('5508', model):
                    output_logger.debug(f"\tCurrent Version: {v['pre']['version']}")
                    output_logger.debug(f"\Hardware does not support new software version.")
                else:
                    output_logger.debug(f"\tPost Upgrade Version: {v['post']['version']}")
                    output_logger.debug(f"\tImage: {v['post']['image']}\n")


    return ver_pre_post_dict

    # output_logger.debug(f"\nScript Execution Time: {datetime.datetime.now() - start_time}\n")

def main():

    version_report(arguments, debug=True)


# Standard call to the main() function.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Script Description",
                                     epilog="Usage: ' python version_report NA_LA 0431' ")
    parser.add_argument('region', type = utils.arg_type_check_region, help=" Region can be 'APAC', "
                                                                                      "'EAME', 'NA_LA' ")
    parser.add_argument('site_id', type = utils.arg_type_check_siteid, help=' 3 or 4 digit site ID ')
    parser.add_argument('-e', '--extension', action='store', default=False, help='Valid file extension in format '
                                                                                 '".xxx" or comma delimited '
                                                                                 '".txt, .fil" Default values if '
                                                                                 'option not give are .txt and .log')
    parser.add_argument('-d', '--directory', action='store', default=False, help='Directory to disambiguate sites')
    parser.add_argument('-c', '--current_only', action='store_true', default=False, help='Execute Report for Current Versiosn Only')
    arguments = parser.parse_args()
    main()
