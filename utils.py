#!/usr/bin/python -tt
# Project: cat_netmiko
# Filename: utils
# claudia
# PyCharm

from __future__ import absolute_import, division, print_function

__author__ = "Claudia de Luna (claudia@indigowire.net)"
__version__ = ": 1.0 $"
__date__ = "9/27/20"
__copyright__ = "Copyright (c) 2018 Claudia"
__license__ = "Python"

import argparse
import yaml
import netmiko
import numpy as np
import pandas as pd
import json
import os
import re
import dotenv
import add_2env
import shutil
import ntpath
import datetime
import logging
import subprocess
import sys


def replace_space(text, debug=False):
    newtext = re.sub('\s+', '_', text)
    if debug:
        print(f"Original Text: {text}\nReturning Text: {newtext.strip()}")
    return newtext.strip()


def load_env_from_dotenv_file(path):
    # Load the key/value pairs in the .env file as environment variables
    if os.path.isfile(path):
        dotenv.load_dotenv(path)
    else:
        print(f"ERROR! File {path} NOT FOUND! Aborting program execution...")
        exit()


def devs_from_vnoc(vnoc_fn="20200924_vnoc_data_dump.xlsx", debug=False):

    df = pd.read_excel(vnoc_fn, dtype={'SiteID': object})
    df.fillna("TBD", inplace=True)
    sites = [11, 61, 68, 78, 96, 118, 234, 240, 262, 266, 266, 323, 339, 341, 364, 367, 419, 709, 743, 836, 854, 1645,
             1864, 1323, 1429, 1621, 1838, 1879, 1878, 265]
    for s in sites:
        tdf = df[df['SiteID'] == s]
        devlist = tdf['fqdn'].tolist()
        if debug:
            print(f"==========Site {s}  Total Devices {len(devlist)}==============")
            print(devlist)
        # This subdir must exists
        json_file_subdir = "site_json"
        sub_dir(json_file_subdir)
        json_file_name = f"site_{s}_devlist.json"
        json_file_path = os.path.join(os.getcwd(),json_file_subdir, json_file_name)
        with open(json_file_path,"w") as f:
            f.write(json.dumps(devlist, indent=4))


def create_cat_devobj_from_json_list(dev):
    """
        dev = {
        'device_type': 'cisco_nxos',
        'ip' : 'sbx-nxos-mgmt.cisco.com',
        'username' : user,
        'password' : pwd,
        'secret' : sec,
        'port' : 8181
    }
    """
    dotenv.load_dotenv()
    dev_obj = {}
    # print(os.environ)
    usr = os.environ['NET_USR']
    pwd = os.environ['NET_PWD']

    core_dev = r'(ar|as|ds|cs){1}\d\d'
    dev_obj.update({'ip': dev.strip()})
    dev_obj.update({'username': usr})
    dev_obj.update({'password': pwd})
    dev_obj.update({'secret': pwd})
    dev_obj.update({'port': 22})
    if re.search(core_dev, dev, re.IGNORECASE):
        dev_obj.update({'device_type': 'cisco_ios'})
    elif re.search(r'-srv\d\d', dev, re.IGNORECASE):
        dev_obj.update({'device_type': 'cisco_nxos'})
    elif re.search(r'-sp\d\d', dev, re.IGNORECASE):
        dev_obj.update({'device_type': 'silverpeak'})
    elif re.search(r'-wlc\d\d', dev, re.IGNORECASE):
        dev_obj.update({'device_type': 'cisco_wlc'})
    elif re.search('10.1.10.109', dev, re.IGNORECASE):
        dev_obj.update({'device_type': 'cisco_wlc'})
        dev_obj.update({'username': 'adminro'})
        dev_obj.update({'password': 'Readonly1'})
        dev_obj.update({'secret': 'Readonly1'})
        # dev_obj.update({'username': 'admin'})
        # dev_obj.update({'password': 'A123m!'})
        # dev_obj.update({'secret': 'A123m!'})
    elif re.search('10.1.10.', dev, re.IGNORECASE) or re.search('1.1.1.', dev, re.IGNORECASE):
        dev_obj.update({'device_type': 'cisco_ios'})
    else:
        dev_obj.update({'device_type': 'unknown'})

    return dev_obj


def read_yaml(filename):
    with open(filename) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    return data


def read_json(filename, debug=False):
    with open(filename) as f:
        data = json.load(f)
    if debug:
        print(f"\n...in the read_json function in utils.py")
        print(data)
        print(f"returning data of type {type(data)} with {len(data)} elements\n")
    return data


def write_txt(filename, data):
    with open(filename, "w") as f:
        f.write(data)
    return f


def sub_dir(output_subdir, debug=False):
    # Create target Directory if don't exist
    if not os.path.exists(output_subdir):
        os.mkdir(output_subdir)
        print("Directory ", output_subdir, " Created ")
    else:
        if debug:
            print("Directory ", output_subdir, " Already Exists")


def conn_and_get_output(dev_dict, cmd_list, debug=False):

    response = ""
    try:
        net_connect = netmiko.ConnectHandler(**dev_dict)
    except (netmiko.ssh_exception.NetmikoTimeoutException, netmiko.ssh_exception.NetMikoAuthenticationException):
        print(f"Cannot connect to device {dev_dict['ip']}.")

    for cmd in cmd_list:
        if debug:
            print(f"--- Show Command: {cmd}")
        try:
            output = net_connect.send_command(cmd.strip())
            response += f"\n!--- {cmd} \n{output}"
        except Exception as e:
            print(f"Cannot execute command {cmd} on device {dev_dict['ip']}.")
            # continue

    return response


def get_all_file_paths(directory):
    # initializing empty file paths list
    file_paths = []

    # crawling through directory and subdirectories
    for root, directories, files in os.walk(directory):
        for filename in files:
            # join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)

            # returning all file paths
    return file_paths


def get_files_in_dir(directory, ext=".txt", debug=False):

    # Initialise list of files
    file_list = []

    # Make sure extension has leading dot
    if not re.match(r'.',ext):
        ext = "." + ext

    # Iterate through directory looking for files with provided extension
    for file in os.listdir(directory):
        if file.endswith(ext):
            # print(os.path.join(directory, file))
            file_list.append(os.path.join(directory, file))

    if debug:
        print(f"\nFrom get_files_in_dir Function, List of all files of type {ext} in directory:\n{directory}\n")
        for afile in file_list:
            print(afile)

    return file_list


def read_files_in_dir(dir, ext, debug=False):

    valid_file_list = []

    try:
        dir_list = os.listdir(dir)
        # other code goes here, it iterates through the list of files in the directory

        for afile in dir_list:

            filename, file_ext = os.path.splitext(afile)

            if file_ext.lower() in ext:
                afile_fullpath = os.path.join(dir,afile)
                valid_file_list.append(afile_fullpath)

        if debug:
            print(f"\nFrom read_files_in_dir Function, List of all files of type {ext} in directory:\n{dir}\n")
            for afile in valid_file_list:
                print(afile)

    except WindowsError as winErr:

        print("Directory error: " + str((winErr)))
        print(sys.exit("Aborting Program Execution"))

    return valid_file_list, dir_list


def load_environment(debug=False):
    # Load Credentials from environment variables
    dotenv.load_dotenv(verbose=True)

    usr_env = add_2env.check_env("NET_USR")
    pwd_env = add_2env.check_env("NET_PWD")

    if debug:
        print(usr_env)
        print(pwd_env)

    if not usr_env['VALID'] and not pwd_env['VALID']:
        add_2env.set_env()
        # Call the set_env function with a description indicating we are setting a password and set the
        # sensitive option to true so that the password can be typed in securely without echo to the screen
        add_2env.set_env(desc="Password", sensitive=True)


def get_and_zip_output(devices_list, save_to_subdir, debug=False, log=False):

    logging.basicConfig(filename='netmiko.log', level=logging.DEBUG)
    logger = logging.getLogger("netmiko")

    datestamp = datetime.date.today()
    print(f"===== Date is {datestamp} ====")

    fn = "show_cmds.yml"
    cmd_dict = read_yaml(fn)

    # SAVING OUTPUT
    sub_dir(save_to_subdir)

    for dev in devices_list:
        print(f"\n\n==== Device {dev}")
        devdict = create_cat_devobj_from_json_list(dev)
        print(f"---- Device Type {devdict['device_type']}")

        if devdict['device_type'] in ['cisco_ios', 'cisco_nxos', 'cisco_wlc']:
            if re.search('ios', devdict['device_type']):
                cmds = cmd_dict['ios_show_commands']
            elif re.search('nxos', devdict['device_type']):
                cmds = cmd_dict['nxos_show_commands']
            elif re.search('wlc', devdict['device_type']):
                cmds = cmd_dict['wlc_show_commands']
            else:
                cmds = cmd_dict['general_show_commands']
            resp = conn_and_get_output(devdict, cmds, debug=True)
            # print(resp)
            output_dir = os.path.join(os.getcwd(), save_to_subdir, f"{dev}.txt")
            write_txt(output_dir, resp)

        else:
            print(f"\n\n\txxx Skip Device {dev} Type {devdict['device_type']}")

        # print(cmds)

    ##  Zip the Dir
    # path to folder which needs to be zipped
    directory = save_to_subdir

    curr_dir = os.getcwd()
    # calling function to get all file paths in the directory
    file_paths = get_all_file_paths(directory)

    # printing the list of all files to be zipped
    print('\n\nFollowing files will be zipped:')
    for file_name in file_paths:
        print(file_name)

    # writing files to a zipfile
    # Create zipfile name with timestamp
    zip_basefn = f"{save_to_subdir}_{datestamp}"
    zip_fn = f"{zip_basefn}"

    shutil.make_archive(zip_fn, 'zip', directory)

    print(f"All files zipped successfully to Zip file {zip_fn} in directory {directory}!\n\n")

    return zip_fn


def get_filename_wo_extension(fn_sting, debug=True):
    head, tail = ntpath.split(fn_sting)
    if tail:
        fn = tail
    else:
        fn = ntpath.basename(head)
    filename = os.path.splitext(fn)
    if debug: print(f"{head} {tail} \nReturn: {filename[0]}")
    return filename[0]


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
            file_list, total_files = read_files_in_dir(pth, valid_file_extenstion)
            print("\t Total files in directory: " + str(len(total_files)))
            print("\t Valid files in directory: " + str(len(file_list)))

        else:
            print("Processing File: " + pth)
            file_list.append(pth)

    else:
        print("Problem with path or filename! {}".format(pth))
        sys.exit("Aborting Program Execution due to bad file or directory argument.")

    return file_list


def os_is():
    # Determine OS to set ping arguments
    local_os = ''
    if sys.platform == "linux" or sys.platform == "linux2":
        local_os = 'linux'
    elif sys.platform == "darwin":
        local_os = 'linux'
    elif sys.platform == "win32":
        local_os = 'win'

    return local_os


def ping_device(ip, debug=False):

    pings = False

    local_os = os_is()

    ## Ping with -c 3 on Linux or -n 3 on windows
    if local_os == 'linux':
        ping_count = "-c"
        timeout = '-t'
    else:
        ping_count = "-n"
        timeout = '-w'

    device_pings = False
    #info = subprocess.STARTUPINFO()
    #output = subprocess.Popen(['ping', ping_count, '3', '-w', '500', ip], stdout=subprocess.PIPE,
    #                          startupinfo=info).communicate()[0]
    output = subprocess.Popen(['ping', ping_count, '3', timeout, '1000', ip], stdout=subprocess.PIPE
                              ).communicate()[0]

    if debug:
        # output is bitecode so need to decode to string
        print(output.decode('UTF-8'))

    if "Destination host unreachable" in output.decode('utf-8'):
        print(ip + " is Offline. Destination unreachable.")
        pings = False
    elif "TTL expired in transit" in output.decode('utf-8'):
        print(ip + " is not reachable. TTL expired in transit.")
        pings = False
    elif "Request timed out" in output.decode('utf-8'):
        print("\n" + ip + " is Offline. Request timed out.")
        pings = False
    elif "Request timeout" in output.decode('utf-8'):
        print("\n" + ip + " is Offline. Request timed out.")
        pings = False
    else:
        pings = True

    return pings


def main():

    add_2env.set_env()

    # Call the set_env function with a description indicating we are setting a password and set the
    # sensitive option to true so that the password can be typed in securely without echo to the screen
    add_2env.set_env(desc="Password", sensitive=True)

    fn = "show_cmds.yml"
    cmd_dict = read_yaml(fn)
    # print(cmd_dict)
    # print(cmd_dict.keys())
    # for k,v in cmd_dict.items():
    #     print(k)
    #     for cmd in v:
    #         print(f"- {cmd}")

    devs_from_vnoc()

    json_file_subdir = "site_json"
    sub_dir(json_file_subdir)
    json_file_name = arguments.json_file
    json_file_path = os.path.join(os.getcwd(), json_file_subdir, json_file_name)

    devs = read_json(json_file_path)

    # Its a good practice to be explicit in code and so explicitly telling dotenv to look in the directory that contains
    # the running script is a good idea
    # Create an OS agnostic full path to the .env file (assuming the .env file you want is in the current working dir
    dotenv_path = os.path.join(os.getcwd(), '.env')

    # load_env_from_dotenv_file(dotenv_path)

    # SAVING OUTPUT
    sub_dir(arguments.output_subdir)

    for dev in devs:
        print(f"\n\n==== Device {dev}")
        devdict = create_cat_devobj_from_json_list(dev)
        if devdict['device_type'] in ['cisco_ios', 'cisco_nxos']:
            if re.search('ios', devdict['device_type']):
                cmds = cmd_dict['ios_show_commands']
            elif re.search('nxos', devdict['device_type']):
                cmds = cmd_dict['nxos_show_commands']
            elif re.search('wlc', devdict['device_type']):
                cmds = cmd_dict['wlc_show_commands']
            else:
                cmds = cmd_dict['general_show_commands']
            resp = conn_and_get_output(devdict, cmds)
            print(resp)
            output_dir = os.path.join(os.getcwd(), arguments.output_subdir, f"{dev}.txt")
            write_txt(output_dir, resp)
        else:
            print(f"\n\n\txxx Skip Device {dev} Type {devdict['device_type']}")


# Standard call to the main() function.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Script Description",
                                     epilog="Usage: ' python utils' ")

    #parser.add_argument('all', help='Execute all exercises in week 4 assignment')
    parser.add_argument('-j', '--json_file', help='Name of JSON file with list of devices', action='store',
                        default="ios_test.json")
    parser.add_argument('-o', '--output_subdir', help='Name of output subdirectory for show command files', action='store',
                        default="TEST")
    arguments = parser.parse_args()
    main()
