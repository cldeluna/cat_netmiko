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


def devs_from_vnoc(vnoc_fn="20200924_vnoc_data_dump.xlsx"):

    df = pd.read_excel(vnoc_fn, dtype={'SiteID': object})
    df.fillna("TBD", inplace=True)
    sites = [11, 61, 68, 78, 96, 118, 234, 240, 262, 266, 266, 323, 339, 341, 364, 367, 419, 709, 743, 836, 854, 1645,
             1864, 1323, 1429, 1621, 1838, 1879, 1878, 265]
    for s in sites:
        tdf = df[df['SiteID'] == s]
        devlist = tdf['fqdn'].tolist()
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

    dev_obj = {}
    # print(os.environ)
    usr = os.environ['NET_USER']
    pwd = os.environ['NET_PWD']

    core_dev = r'(ar|as|ds){1}\d\d'
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
    elif re.search('10.1.10.', dev, re.IGNORECASE):
        dev_obj.update({'device_type': 'cisco_ios'})
    else:
        dev_obj.update({'device_type': 'unknown'})

    return dev_obj


def read_yaml(filename):
    with open(filename) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    return data


def read_json(filename):
    with open(filename) as f:
        data = json.load(f)
    return data


def write_txt(filename, data):
    with open(filename, "w") as f:
        f.write(data)
    return f

def sub_dir(output_subdir):

    # Create target Directory if don't exist
    if not os.path.exists(output_subdir):
        os.mkdir(output_subdir)
        print("Directory ", output_subdir, " Created ")
    else:
        print("Directory ", output_subdir, " Already Exists")


def conn_and_get_output(dev_dict, cmd_list):

    response = ""
    net_connect = netmiko.ConnectHandler(**dev_dict)

    for cmd in cmd_list:
        print(f"--- Show Command: {cmd}")
        output = net_connect.send_command(cmd.strip())
        response += f"\n** {cmd} \n{output}"

    return response


def main():

    fn = "show_cmds.yml"
    cmd_dict = read_yaml(fn)
    print(cmd_dict)
    print(cmd_dict.keys())
    for k,v in cmd_dict.items():
        print(k)
        for cmd in v:
            print(f"- {cmd}")

    cmds = cmd_dict['general_show_commands']

    devs_from_vnoc()

    json_file_subdir = "site_json"
    sub_dir(json_file_subdir)
    json_file_name = arguments.json_file
    json_file_path = os.path.join(os.getcwd(), json_file_subdir, json_file_name)

    devs = read_json(json_file_path)


    # SAVING OUTPUT
    sub_dir("TEST")

    for dev in devs:
        print(f"\n\n==== Device {dev}")
        devdict = create_cat_devobj_from_json_list(dev)
        resp = conn_and_get_output(devdict, cmds)
        print(resp)
        output_dir = os.path.join(os.getcwd(), output_subdir, f"{dev}.txt")
        write_txt(output_dir, resp)

# Standard call to the main() function.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Script Description",
                                     epilog="Usage: ' python utils' ")

    #parser.add_argument('all', help='Execute all exercises in week 4 assignment')
    parser.add_argument('-j', '--json_file', help='Name of JSON file with list of devices', action='store',
                        default="ios_test.json")
    arguments = parser.parse_args()
    main()
