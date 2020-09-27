#!/usr/bin/python -tt
# Project: netmiko38
# Filename: test
# claudia
# PyCharm

from __future__ import absolute_import, division, print_function

__author__ = "Claudia de Luna (claudia@indigowire.net)"
__version__ = ": 1.0 $"
__date__ = "4/20/20"
__copyright__ = "Copyright (c) 2018 Claudia"
__license__ = "Python"

import argparse
import netmiko
import os
import utils

def some_function():
    pass


def main():
    """
    Basic Netmiko script showing how to connect to a device and save the output.  The first section 
    """
    
    # https://github.com/ktbyers/netmiko/blob/develop/netmiko/ssh_autodetect.py


    # user = os.environ.get('username')
    # pwd = os.environ.get('password')
    # sec = os.environ.get('secret')


    # sbx-nxos-mgmt.cisco.com ansible_host=sbx-nxos-mgmt.cisco.com ansible_port=8181 username=admin password=Admin_1234!
    # ios-xe-mgmt.cisco.com ansible_host=ios-xe-mgmt.cisco.com port=8181 username=root password=D_Vay!_10&

    os.environ["NET_TEXTFSM"] = "./ntc-templates/templates"

    user = 'admin'
    pwd = 'Admin_1234!'
    sec = 'Admin_1234!'

    dev = {
        'device_type': 'cisco_nxos',
        'ip' : 'sbx-nxos-mgmt.cisco.com',
        'username' : user,
        'password' : pwd,
        'secret' : sec,
        'port' : 8181

    }

    dev_asa = {
        'device_type': 'cisco_asa',
        'ip' : '10.1.10.27',
        'username' : 'cisco',
        'password' : 'cisco',
        'secret' : 'cisco',
        'port' : 22

    }

    user = 'root'
    pwd = 'D_Vay!_10&'
    sec = 'D_Vay!_10&'
    #
    dev = {
        'device_type': 'cisco_ios',
        'ip' : 'ios-xe-mgmt.cisco.com',
        'username' : user,
        'password' : pwd,
        'secret' : sec,
        'port' : '8181'
    }


    # RAW Parsing with Python
    print(f"\n===============  Netmiko ONLY ===============")
    try:
        dev_conn = netmiko.ConnectHandler(**dev)
        dev_conn.enable()
        response = dev_conn.send_command('show version')
        print(f"\nResponse is of type {type(response)}\n")
        print(response)
        # because the response is a string we need to do some string manipulation
        # first we need to split the string into lines
        resp = response.splitlines()

        with open('test.txt', 'w') as sample_file: 
            sample_file.write(response)

        # now we should have a list in the variable resp over which we can iterate
        print(f"\nSplit Response is of type {type(resp)}\n")
        print(resp)
        find_string = "NXOS: version"
        # look
        for line in resp:
            if find_string in line:
                print(f"******** FOUND LINE! ******\n{line}\n")

    except Exception as e:
        print(e)


    print(f"\n===============  Netmiko with TEXTFSM OPTION  ===============")
    try:
        dev_conn = netmiko.ConnectHandler(**dev)
        dev_conn.enable()
        response = dev_conn.send_command('show interface', use_textfsm=True)
        print(f"\nResponse is of type {type(response)}\n")
        print(response)
        print(f"\n== Pick out specific information from the response!")
        print(f"The OS is {response[0]['os']}")
        print(f"The Platform is {response[0]['platform']}")
        print(f"The boot image is {response[0]['boot_image']}")

    except Exception as e:
        print(e)


# Standard call to the main() function.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Script Description",
                                     epilog="Usage: ' python test' ")

    #parser.add_argument('all', help='Execute all exercises in week 4 assignment')
    parser.add_argument('-a', '--all', help='Execute all exercises in week 4 assignment', action='store_true',
                        default=False)
    arguments = parser.parse_args()
    main()
