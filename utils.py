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
import textfsm
from icecream import ic
ic.configureOutput(includeContext=True)


# ### Argument Validation Functions

def arg_type_check_region(region):

    # Region can be 'APAC', 'EAME', 'NA_LA'
    valid_regions = ['APAC', 'EAME', 'NA_LA']
    if region.strip().upper() in valid_regions:
        valid_region = region.upper()
    else:
        raise ValueError("Valid values are 'APAC', 'EAME', 'NA_LA' ")

    return valid_region


def arg_type_check_sitetype(value):

    valid_type = ['med', 'small', 'micro', 'medium']

    if value.strip() in valid_type:
        valid_sitetype = value.strip()
    else:
        raise ValueError

    return valid_sitetype


def arg_type_check_siteid(value):

    if re.search(r'^\d{1,4}$', value.strip()):
        valid_value = value.strip()
        if len(valid_value) == 3:
            valid_value = f"0{valid_value}"
        elif len(valid_value) == 2:
            valid_value = f"00{valid_value}"
        elif len(valid_value) == 1:
            valid_value = f"000{valid_value}"
        else:
            valid_value = value

    else:
        raise ValueError

    return valid_value


########
def set_base_by_user(base_override='', debug=False):


    user = os.getlogin().lower()
    desktop_os = os.name
    base_path = ''
    if debug: print(f"Setting Base Path based on user {user}")

    # If a root or base directory is passed as an argument then set the base path otherwise, set base path depending
    # on who is logged in
    if base_override:
        base_path = base_override
        if debug: print(f"Using Optional Base Path Provided:\n{base_override}")
    else:
        if re.search('lucas', user):
            base_path = os.path.join("D:\\","Dropbox (EIA)","CAT_NT","Network_Transformation_Phase3")

        elif re.search('Claudia', user, re.IGNORECASE):
            # MacBookPro 13 in
            # /Users/Claudia/Dropbox (Indigo Wire Networks)/CAT_NetMon_Project/
            base_path = os.path.join("/Users", "Claudia", "Dropbox (Indigo Wire Networks)", "CAT_NetMon_Project")

        elif re.search('root', user, re.IGNORECASE):
            # MacBookPro 13 in
            # /Users/Claudia/Dropbox (Indigo Wire Networks)/CAT_NetMon_Project/
            base_path = os.path.join("/Users", "Claudia", "Dropbox (Indigo Wire Networks)", "CAT_NetMon_Project")
            # /Users/claudia/Dropbox (Indigo Wire Networks)/Cat_Software_Upgrades/
            # base_path = os.path.join("/Users", "Claudia", "Dropbox (Indigo Wire Networks)", "Cat_Software_Upgrades")



        elif re.search('admin', user):
            # /Users/admin/Dropbox (EIA)/CAT_NT/Network_Transformation_Phase3
            # /Users/claudia/Dropbox (Indigo Wire Networks)/CAT_NetMon_Project/Sites/
            base_path = os.path.join("/Users", "admin", "Dropbox (EIA)", "CAT_NT", "Network_Transformation_Phase3")

        elif re.search('claud', user):
            # if debug: /Users/claudia/Dropbox (Indigo Wire Networks)/CAT_NetMon_Project/Sites/
            if desktop_os == 'nt':
                base_path = os.path.join("D:\\","Dropbox (Indigo Wire Networks)","CAT_NetMon_Project")
            else:
                base_path = os.path.join("/Users","claudia", "Dropbox (Indigo Wire Networks)", "CAT_NetMon_Project")
    if debug: print(f"Base Path for user {user} is:\n\t{base_path}")

    return base_path


def find_site_root(base_path, region, siteid, disamabig_dir=False):
    """
    PATH to Root or top level directory of Site
    :param base_path:
    :param region:
    :param siteid:
    :return:
    """

    site_path = ''
    valid_file_extenstion = [".xlsx"]

    if os.path.exists(base_path):

        # Check to see if the argument is a directory
        if os.path.isdir(base_path):
            print(f"Processing Root Directory: \n\t{base_path}")
            dir_list, total_dirs = read_files_in_dir(base_path, valid_file_extenstion)

            region_dir = os.path.join(base_path, region)
            print("Regional Directory is {}".format(region_dir))

            dir_list, total_dirs = read_files_in_dir(region_dir, valid_file_extenstion)

            #  Find each site in the specified region
            for site_dir in total_dirs:

                if disamabig_dir:
                    if re.match(disamabig_dir, site_dir):
                        # PATH to Root directory of Site
                        site_path = os.path.join(region_dir, site_dir)
                        print(f"\tFound site number {siteid} in site directory {site_path}\n")
                else:
                    # If this is the site we want to process:
                    if re.match(siteid, site_dir):

                        # PATH to Root directory of Site
                        site_path = os.path.join(region_dir, site_dir)
                        print(f"\tFound site number {siteid} in site directory {site_path}\n")

    return site_path


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
    elif re.search('10.', dev, re.IGNORECASE):
        dev_obj.update({'device_type': 'cisco_ios'})
    else:
        dev_obj.update({'device_type': 'unknown'})

    return dev_obj


def get_show_cmd_parsed(dev, shcmd, save_2json=False, level=0, debug=False):

    if level == 0:
        print(f"\n\n==== Device {dev} getting command {shcmd}")
    elif level == 1:
        print(f"\n\t\t--- Device {dev} getting command {shcmd}")
    elif level == 2:
        print(f"\n\t\t\t- Device {dev} getting command {shcmd}")

    outdir = 'local'

    fn = "show_cmds.yml"
    cmd_dict = read_yaml(fn)
    devdict = create_cat_devobj_from_json_list(dev)

    if debug: print(f'devdict is {devdict}')

    # Default to Cisco IOS device type
    if devdict['device_type'] == 'unknown':
        devdict.update({'device_type': 'cisco_ios'})

    # if devdict['device_type'] in ['cisco_ios', 'cisco_nxos', 'cisco_wlc']:
    resp = conn_and_get_output_parsed(devdict, shcmd)
    # print(resp)
    if save_2json:
        output_dir = os.path.join(os.getcwd(), outdir, f"{dev}_{shcmd.replace(' ', '_')}.json")
        print(f"Saving JSON to {output_dir}")
        with open(output_dir, 'w') as f:
            json.dump(resp, f, indent=4)
    # else:
    #     print(f"\n\n\txxx Skip Device {dev} Type {devdict['device_type']}")

    return resp


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


def save_json(filename, data, debug=False):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
    if debug:
        print(f"\n...in the read_json function in utils.py")
        print(f"saved data to {filename}")


def write_txt(filename, data):
    with open(filename, "w") as f:
        f.write(data)
    return f


def sub_dir(output_subdir, debug=False):
    # Create target Directory if does not exist
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


def conn_and_get_output_parsed(dev_dict, cmd, debug=False):

    os.environ["NET_TEXTFSM"] = "./ntc-templates/templates"

    response = ""
    output = ""
    if debug: ic(dev_dict)
    try:
        net_connect = netmiko.ConnectHandler(**dev_dict)
    except netmiko.ssh_exception.NetmikoTimeoutException:
        print(f"Cannot connect to device {dev_dict['ip']}. Connection Timed Out!")
    except netmiko.ssh_exception.NetMikoAuthenticationException:
        print(f"Cannot connect to device {dev_dict['ip']}. Authentication Exception!")

    if debug:
        print(f"--- Show Command: {cmd}")
    try:
        output = net_connect.send_command(cmd.strip(), use_textfsm=True)
    except Exception as e:
        print(f"Cannot execute command {cmd} on device {dev_dict['ip']}.")
        print(f"{e}\n")

    if debug: ic(output)

    return output


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

    if debug: print(f"in get_files_in_dir with {directory} and extension {ext}")
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


def open_file(filename, mode="r", encoding="utf-8", debug=False):

    """

    General Utility to safely open a file.

    encoding="utf-8"

    :param filename:  file to open
    :param mode: mode in which to open file, defaults to read
    :return:  file handle

    """

    if debug: print(f"in open_file function in cat_config_utils module with filename {filename} and mode as {mode}")

    file_handle = ''
    # Mode = r | w | a | r+
    try:
        file_handle = open(filename, mode, encoding=encoding, errors='ignore')

    except IOError:
        print("IOError" + str(IOError))
        print(f"open_file() function could not open file with mode {mode} in given path {path}"
              f"\nPlease make sure all result files are closed!")

    return file_handle


def open_read_file(filename, mode="r"):

    file_handle = ''
    file_contents = ''

    # Mode = r | w | a | r+
    try:
        file_handle = open(filename, mode)

        # Read the file contents into a variable for parsing
        file_contents = file_handle.read()
        # Close file
        file_handle.close()


    except IOError:
        print("IOError" + str(IOError))
        print("Could not open file. Please make sure all result files are closed!")

    return file_handle, file_contents


def fsm_process_string(arg_dict, debug=False):

    if debug:
        print(arg_dict)
        print(arg_dict.keys())

    # Mandatory argument passed to script - either a filename or a directory of files to process
    path = arg_dict['filename_or_dir']

    textfsm_template = os.path.join(".", "ntc-templates", "templates", arg_dict['fsm_template'])
    if debug: print(f"\nUsing TextFSM Template: {textfsm_template}\n")

    # Split filename from path (if any)
    tfsm_dir = os.path.dirname(textfsm_template)
    tfsm_fn = os.path.basename(textfsm_template)

    # set the template name (without extension) to use in results file name
    textfsm_name = os.path.splitext(tfsm_fn)[0]

    # Set table as False so if you don't get anything back from from parsing you can exit gracefully
    table = False

    # Keep a list of any files that did not have any output information
    no_output = []

    # Initialize list of all valid files
    file_list = []
    # Initialize list of valid parsing results
    fsm_all_results = []

    all_macaddr = []

    # Parse Valid file extensions if they were provided as arguments
    valid_file_extension = []
    if arg_dict['extension']:
        extensions = arg_dict['extension']
        extensions = re.sub(r'\s+', '', extensions)
        extensions = re.split(r'[;|,|\s]?', extensions)

        for ext in extensions:
            valid_file_extension.append(ext)
    else:
        valid_file_extension.append(".txt")
        valid_file_extension.append(".log")

    if os.path.exists(path):
        # Check to see if the argument is a directory
        if os.path.isdir(path):

            file_list, total_files = read_files_in_dir(path, valid_file_extension)

            if debug:
                print("\nProcessing Directory: " + path + " for all files with the following extensions: " + str(valid_file_extension))
                print(f"\t Total files in directory: {str(len(total_files))}")
                print(f"\t Valid files in directory: {str(len(file_list))}\n")

            path_list = os.path.basename(path)
            results_fn = path_list + "_" + textfsm_name + "-results.csv"
            results_dir = os.path.join(path, results_fn)
            results_num_files = str(len(file_list))

            # print(f"path is {path}")
            # print(f"path_list is {path_list}")
            # print(f"results_fn is {results_fn}")

        else:
            if debug: print("Processing File: " + path)
            file_list.append(path)
            fn, fext = os.path.splitext(path)
            results_fn = fn + "_" + textfsm_name + "-results.csv"
            curr_dir = os.getcwd()
            results_dir = os.path.join(os.path.basename(curr_dir), results_fn)
            results_num_files = '1'

    else:
        print("Problem with path or filename! {}".format(path))
        sys.exit("Aborting Program Execution due to bad file or directory argument.")

    # Make sure we have files to process (at least 1)
    if len(file_list) > 0:

        # Open the CSV file to store results
        csv_results_fh = gen_utils.open_file(results_dir, 'w')
        csv_writer = csv.writer(csv_results_fh, quoting=csv.QUOTE_MINIMAL)

        # Iterate through the valid file list. If the script was passed a filename it will be a file_list of 1
        # If the script was passed a directory it will be a list of files with a valid extension
        for fil in file_list:

            _ = os.path.basename(fil)
            hostname_from_fn = _.split('.')[0]

            if debug: print(f"\nProcessing device file: {_} with derived hostname {hostname_from_fn}\n")

            # open_file function returns a file handle for the show command file
            fh = gen_utils.open_file(fil, 'r')

            full_output = gen_utils.load_shcmd_lines(fil)
            show_run_output = gen_utils.get_show_section(full_output,arg_dict['string_start'],arg_dict['string_end'],
                                                         debug=False)

            if len(show_run_output) > 0:
                if "!---" in show_run_output[0]:
                    show_run_output.pop(0)

            output_string = gen_utils.list_to_str(show_run_output)
            # print(fil)
            # print(output_string)

            table = textfsm_utility.text_fsm_parse(textfsm_template, gen_utils.list_to_str(show_run_output))
            fil_results = table._result

            # Send TextFSM Template name and data to parse to text_fsm_parsing function
            # file_results returns the table
            # table = textfsm_utility.text_fsm_parse(textfsm_template, file_contents)
            fil_results = table._result

            # for line in fil_results:
            #     print(line)
            # print(len(fil_results))
            # print(table)
            # print(dir(table))
            # print(fil_results)

            # Keep track of files without parser output in the no_output list so it can be printed later
            if len(fil_results) == 0:
                no_output.append(fil)
            else:
                # Add derived hostname
                for line in fil_results:
                    line.append(hostname_from_fn)
                # print(fil_results)
                # Append fil_results list of results to list of all results
                fsm_all_results.append(fil_results)

        # Write the header row in the CSV file
        header_row = table.header
        header_row.append("DERIVED_HOSTNAME")
        # print(f"\nTable Header: {table.header}")
        # print(f"\nHeader Row: {header_row}")
        table.header.append("Source_File_directory")
        if table:
            csv_writer.writerow(header_row)
        else:
            sys.exit("Parsing Error. Execution aborted.")

        # Write each row in the fsm_all_results list to the CSV file
        for re_row in fsm_all_results:
            for single_row in re_row:
                single_row.append(path)
                all_macaddr.append(single_row)
                csv_writer.writerow(single_row)

    return fsm_all_results, all_macaddr, textfsm_name, hostname_from_fn, table


def text_fsm_parse(template_fn, data, debug=False):

    # Run the text through the FSM.
    # The argument 'template' is a file handle and 'raw_text_data' is a
    # string with the content from the show_inventory.txt file
    # print(data)
    template = open(template_fn)
    re_table = textfsm.TextFSM(template)
    fsm_results = re_table.ParseText(data)

    if debug:
        print("===== in text_fsm_parse function")
        print(dir(re_table))
        print(type(re_table))
        print(re_table.header)
        print(re_table._result)
        print(re_table.values)
        print(re_table.value_map)
        print("="*20)

    return re_table


def process_file_section(arg_dict, debug=False):

    if debug:
        print("In process_file_section function...")
        print(f"\tProcessing file with data \n{arg_dict}")

    # ### Extract Section
    full_output = load_shcmd_lines(arg_dict['filename_or_dir'])
    show_run_output = get_show_section(full_output, arg_dict['string_start'], arg_dict['string_end'], debug=False)

    # if len(show_run_output) > 0:
    #     if "!---" in show_run_output[0]:
    #         show_run_output.pop(0)

    output_string = list_to_str(show_run_output)
    if debug:
        print(arg_dict['filename_or_dir'])
        print(output_string)
        print(f"full_output \n{full_output}")

    textfsm_template = os.path.join(".", "ntc-templates", "templates", arg_dict['fsm_template'])
    table = text_fsm_parse(textfsm_template, output_string)
    fil_results = table._result

    return fil_results


def list_to_str(list_of_lines, debug=False):
    """
    Used when a file is read in via readlines() resulting in a list of lines
    and you need to put it back into a single string variable
    Typically used with CiscoConfParse

    Example:
    parsed = ciscoconfparse.CiscoConfParse(save_file("temp_text.txt", text_output))

    :param list_of_lines:
    :param debug:
    :return:
    """
    # ciscoconfparse wants a file so we have to rebuild the text in text_output and pass the parse command a file
    text_output = ""
    for line in list_of_lines:
        text_output = text_output + line
    if debug: print(text_output)

    return text_output


def load_shcmd_lines(filepath):
    """
    Read file into list of lines
    :param filepath:
    :return:
    """

    with open(filepath, "r") as f:
        file_contents = f.readlines()
    # print(len(file_contents))
    # print(file_contents)
    return file_contents


def get_show_section(lines_of_text, start_string, end_string, debug=False):
    """
    Given a file of many show commands, extract out a specific section

    :param lines_of_text:
    :param start_string:
    :param end_string:
    :param debug:
    :return:
    """

    shrun_lines = []
    in_show = False
    for line in lines_of_text:
        if re.search(start_string, line):
            in_show = True

        if in_show:
            shrun_lines.append(line)

        if re.search(end_string, line):
            in_show = False

    if len(shrun_lines) > 0:
        shrun_lines.pop()

    if debug:
        print(f"From get_show_section Function:")
        print(shrun_lines)
        print(len(shrun_lines))
    return shrun_lines


def get_hostname_from_filename(fn, debug=False):

    filenm = os.path.basename(fn)

    # _ = filenm.split('.net.cat.com.show-commands.txt')
    _ = filenm.split('.')
    if debug: print(f"in get_hostname_from_filename, split is {_}")
    hname = _[0]

    return hname


def parse_cat_hostname(filenamex, debug=False):
    """
    Parse Cat hostname (based on show command filename which should equal hostname)
    :param filename:
    :param debug:
    :return:
    """

    filename = os.path.basename(filenamex)

    # Check to see if Region was set in CLI otherwise attempt to derive from filename
    region = re.search(r"(na|ap|ea|la)", filename)
    rr = check_re_search(region)
    # Check to see if Country was set in CLI otherwise attempt to derive from filename

    country = re.search(r"^(na|la|ap|ea)-\w{2}-", filename)
    if country:
        if country.group():
            _ = country.group().split("-")
            if len(_) >= 2:
                cc = _[1]
    else:
        cc = "TBD"

    # Check to see if SiteID was set in CLI otherwise attempt to derive from filename
    site = re.search(r"^(na|la|ap|ea)-\w{2}-\d{2,4}", filename)
    if site:
        if site.group():
            _ = site.group().split("-")
            if len(_) >= 3:
                siteid = _[2]
    else:
        siteid = "TBD"

    # Check to see if Building (City, Bldg) was set in CLI otherwise attempt to derive from filename

    bldg = re.search(r"^(na|la|ap|ea)-\w{2}-\d{2,4}-\w+-",filename)
    if bldg:
        if bldg.group():
            _ = bldg.group().split("-")
            if len(_) >= 4:
                loc = _[3]
    else:
        loc = "TBD"

    if re.search(r'-cs0\d', filename):
        sitetype = "Large"
    elif re.search(r'-ds0\d', filename):
        sitetype = f"Large > Specific Distribution {loc.upper()}"
    elif re.search(r'-cds0\d', filename):
        sitetype = "Medium"
    elif re.search(r'-as0\d', filename):
        sitetype = "Access"
    else:
        sitetype = "Undefined SiteType"

    if debug:
        print(f"====== Parsing Hostname {filename}")
        print(f"REGION is {rr}")
        print(f"COUNTRY is {cc}")
        print(f"SITE ID is {siteid}")
        print(f"BUILDING or LOCATION is {loc}")
        print(f"SITE TYPE is {sitetype}")
    return rr, cc, siteid, loc, sitetype


def check_re_search(reobj, else_txt="TBD"):
    """
    Used to check the results of re.search
    Used to parse a Cat hostname
    :param reobj:
    :param else_txt:
    :return:
    """

    if reobj:
        if reobj.group():
            xx = reobj.group().lstrip("-")
    else:
        xx = else_txt

    return xx


def get_valid_int_input(prompt, max_value=10):
    while True:
        try:
            value = int(input(prompt))
        except ValueError:
            print("Sorry, I didn't understand that.")
            continue

        if value < 0:
            print("Sorry, your response must not be negative.")
            continue
        elif value >= max_value:
            print(f"Sorry, the value you entered is invalid. Please enter a value between 0 and {max_value}.")
            continue
        else:
            break
    return value


def generic_select_dir(base, input_str, debug=False):

    """
    From a list of directories or files for a site select the directory or file that has the show commands you need.

    :param base: This is the root directory for the site
    :return: The full path to the directory or file selected i

    """

    selected_file_list = []

    file_list, total_files = read_files_in_dir(base, '')
    if debug:
        print(file_list)
        print(total_files)

    # Display all the directories available for selection
    for item in total_files:
        print("{}: {}".format(total_files.index(item), item))

    dir_num = get_valid_int_input(f"Select {input_str}: ", max_value=len(total_files))

    selected_path = os.path.join(base,total_files[int(dir_num)])

    if debug:
        print(f"\nSelected path is {selected_path} and is valid [{os.path.isdir(selected_path)}]")

    # Return the directory path and a list of files
    return selected_path




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
