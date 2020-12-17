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
import datetime
import utils
import add_2env
import os
import re
import dotenv

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


    datestamp = datetime.date.today()
    print(f"===== Date is {datestamp} ====")

    # Load Credentials from environment variables
    dotenv.load_dotenv(verbose=True)

    usr = os.environ['NET_USR']
    pwd = os.environ['NET_PWD']
    sec = os.environ['NET_PWD']

    fn = "show_cmds.yml"
    cmd_dict = utils.read_yaml(fn)

    # SAVING OUTPUT
    utils.sub_dir(arguments.output_subdir)

    if arguments.mfa:
        mfa_code = input("Enter your VIP Access Security Code: ")
        mfa = pwd + mfa_code.strip()
    else:
        mfa = pwd

    devdict = {
        'device_type': arguments.device_type,
        'ip' : arguments.dev,
        'username' : usr,
        'password' : mfa,
        'secret' : mfa,
        'port' : arguments.port
    }

    # RAW Parsing with Python
    print(f"\n===============  Device {arguments.dev} ===============")

    if devdict['device_type'] in ['cisco_ios', 'cisco_nxos', 'cisco_wlc']:
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

        # Optional Note to distinguish or annotate the show commands
        if arguments.note:
            note_text = utils.replace_space(arguments.note)
            basefn = f"{arguments.dev}_{datestamp}_{note_text}.txt"
        else:
            basefn = f"{arguments.dev}_{datestamp}.txt"

        output_dir = os.path.join(os.getcwd(), arguments.output_subdir, basefn)
        utils.write_txt(output_dir, resp)

        print(f"Saving show command output to {output_dir}")

    else:
        print(f"\n\n\txxx Skip Device {arguments.dev} Type {devdict['device_type']}")


# Standard call to the main() function.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Script Description",
                                     epilog="Usage: ' python test' ")

    parser.add_argument('dev', help='Get show commands from this device (ip or FQDN) and save to file.')
    parser.add_argument('-t', '--device_type',
                        help='Device Types include cisco_nxos, cisco_asa, cisco_wlc Default: cisco_ios',
                        action='store',
                        default='cisco_ios')
    parser.add_argument('-p', '--port',
                        help='Port for ssh connection. Default: 22',
                        action='store',
                        default='22')
    parser.add_argument('-o', '--output_subdir',
                        help='Name of output subdirectory for show command files',
                        action='store',
                        default="local")
    parser.add_argument('-s', '--show_cmd', help='Execute a single show command', action='store')
    parser.add_argument('-n', '--note',
                        action='store',
                        help='Short note to distinguish show commands. Ex. -pre or -post')
    parser.add_argument('-m', '--mfa',
                        action='store',
                        help='Multi Factor Authentication will prompt for VIP code',
                        default="local")
    arguments = parser.parse_args()
    main()
