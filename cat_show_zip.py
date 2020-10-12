#!/usr/bin/python -tt
# Project: cat_netmiko
# Filename: cat_show_zip
# claudia
# PyCharm

from __future__ import absolute_import, division, print_function

__author__ = "Claudia de Luna (claudia@indigowire.net)"
__version__ = ": 1.0 $"
__date__ = "10/9/20"
__copyright__ = "Copyright (c) 2018 Claudia"
__license__ = "Python"

import argparse
import utils
import add_2env
import os
# import zipfile
import re
import dotenv
import datetime
import shutil


def main():

    datestamp = datetime.date.today()
    print(f"===== Date is {datestamp} ====")

    # Load Credentials from environment variables
    dotenv.load_dotenv(verbose=True)

    usr_env = add_2env.check_env("NET_USR")
    pwd_env = add_2env.check_env("NET_PWD")

    # print(usr_env)
    # print(pwd_env)

    if not usr_env['VALID'] and not pwd_env['VALID']:
        add_2env.set_env()
        # Call the set_env function with a description indicating we are setting a password and set the
        # sensitive option to true so that the password can be typed in securely without echo to the screen
        add_2env.set_env(desc="Password", sensitive=True)

    fn = "show_cmds.yml"
    cmd_dict = utils.read_yaml(fn)
    # print(cmd_dict)
    # print(cmd_dict.keys())
    # for k,v in cmd_dict.items():
    #     print(k)
    #     for cmd in v:
    #         print(f"- {cmd}")

    # utils.devs_from_vnoc()

    json_file_subdir = "site_json"
    utils.sub_dir(json_file_subdir)
    json_file_name = arguments.json_file
    json_file_path = os.path.join(os.getcwd(), json_file_subdir, json_file_name)

    devs = utils.read_json(json_file_path)

    # Its a good practice to be explicit in code and so explicitly telling dotenv to look in the directory that contains
    # the running script is a good idea
    # Create an OS agnostic full path to the .env file (assuming the .env file you want is in the current working dir
    dotenv_path = os.path.join(os.getcwd(), '.env')

    # load_env_from_dotenv_file(dotenv_path)

    # SAVING OUTPUT
    utils.sub_dir(arguments.output_subdir)

    for dev in devs:
        print(f"\n\n==== Device {dev}")
        devdict = utils.create_cat_devobj_from_json_list(dev)

        if devdict['device_type'] in ['cisco_ios', 'cisco_nxos']:
            if arguments.show_cmd:
                cmds = []
                cmds.append(arguments.show_cmd)
            elif re.search('ios', devdict['device_type']):
                cmds = cmd_dict['ios_show_commands']
            elif re.search('nxos', devdict['device_type']):
                cmds = cmd_dict['nxos_show_commands']
            elif re.search('wlc', devdict['device_type']):
                cmds = cmd_dict['wlc_show_commands']
            else:
                cmds = cmd_dict['general_show_commands']
            resp = utils.conn_and_get_output(devdict, cmds)
            print(resp)
            output_dir = os.path.join(os.getcwd(), arguments.output_subdir, f"{dev}.txt")
            utils.write_txt(output_dir, resp)

        else:
            print(f"\n\n\txxx Skip Device {dev} Type {devdict['device_type']}")

        print(cmds)

    ##  Zip the Dir
    # path to folder which needs to be zipped
    directory = f"./{arguments.output_subdir}"

    # calling function to get all file paths in the directory
    file_paths = utils.get_all_file_paths(directory)

    # printing the list of all files to be zipped
    print('Following files will be zipped:')
    for file_name in file_paths:
        print(file_name)

    # writing files to a zipfile
    # Create zipfile name with timestamp
    jsonfile_parts = arguments.json_file.split('.')
    zip_basefn = f"{jsonfile_parts[0].strip()}_{datestamp}"
    if arguments.show_cmd:
        formatted_shcmd = utils.replace_space(arguments.show_cmd, debug=True)
        zip_fn = f"{zip_basefn}_{formatted_shcmd}"
    else:
        zip_fn = f"{zip_basefn}"

    # with zipfile.ZipFile(zip_fn, 'w') as zip:
    #     # writing each file one by one
    #     for file in file_paths:
    #         zip.write(file)
    shutil.make_archive(zip_fn, 'zip', directory)

    print(f"All files zipped successfully to Zip file {zip_fn}!\n\n")


# Standard call to the main() function.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Script Description",
                                     epilog="Usage: ' python utils' ")

    #parser.add_argument('all', help='Execute all exercises in week 4 assignment')
    parser.add_argument('-j', '--json_file', help='Name of JSON file with list of devices', action='store',
                        default="ios_test.json")
    parser.add_argument('-o', '--output_subdir', help='Name of output subdirectory for show command files', action='store',
                        default="DEFAULT_IOS_TEST")
    parser.add_argument('-s', '--show_cmd', help='Execute a single show command across all devices', action='store',
                        )
    arguments = parser.parse_args()
    print(arguments)
    main()
