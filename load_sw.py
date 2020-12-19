#!/usr/bin/python -tt
# Project: cat_netmiko
# Filename: load_sw
# claudia
# PyCharm

from __future__ import absolute_import, division, print_function

__author__ = "Claudia de Luna (claudia@indigowire.net)"
__version__ = ": 1.0 $"
__date__ = "12/1/20"
__copyright__ = "Copyright (c) 2018 Claudia"
__license__ = "Python"

import argparse
import utils
from datetime import datetime
from netmiko import ConnectHandler
from getpass import getpass
import os
import re



def some_function():
    pass


def main():


    start_time = datetime.now()

    # Set the environment variable for Netmiko to use TextFMS ntc-templates library
    os.environ["NET_TEXTFSM"] = "./ntc-templates/templates"

    host = input("Enter your hostname: ")
    device = {
        'device_type': 'cisco_ios',
        'host': host,
        'username': 'cisco',
        'password': getpass(),
        'global_delay_factor': 2,
    }

    net_connect = ConnectHandler(**device)

    response = net_connect.send_command('show version', use_textfsm=True)
    print(f"\nResponse is of type {type(response)}\n")
    print(response)

    response = net_connect.send_command('dir', use_textfsm=True)
    # print(f"\nResponse is of type {type(response)}\n")
    # print(response)

    load_sw = True
    sw_image = r'cat3k_caa-universalk9.16.12.04.SPA.bin'

    for line in response:
        if re.search(sw_image, line['name']):
            print(line['name'])
            print(f"Found bin file {sw_image} already installed!")
            load_sw = False
            break

    if load_sw:
        cmd = 'copy http://10.1.10.11/cat3k_caa-universalk9.16.12.04.SPA.bin flash:'
        output = net_connect.send_command(
            cmd,
            expect_string=r'Destination filename'
        )
        output += net_connect.send_command('\n',
                                           expect_string=r'#',
                                           delay_factor=5)

        print("\n")
        print("#" * 60)
        print(output)
        print("#" * 60)
        print("\n")

        response = net_connect.send_command('dir', use_textfsm=True)
        for line in response:
            if re.search(sw_image, line['name']):
                print(f"Software bin file {sw_image} loaded!")

    end_time = datetime.now()
    print("\nTotal time: {}".format(end_time - start_time))
    print("\n")


# Standard call to the main() function.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Script Description",
                                     epilog="Usage: ' python load_sw' ")

    # parser.add_argument('device_file', help='Device file in .yml or .json format')
    # parser.add_argument('-p', '--platform', help='Platform for software load. Default: 3850', action='store',
    #                     default='3850')
    arguments = parser.parse_args()
    main()
