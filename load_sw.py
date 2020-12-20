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
import datetime
from netmiko import ConnectHandler
from getpass import getpass
import os
import re
import dotenv
import add_2env
import logging



def some_function():
    pass


def main():


    datestamp = datetime.date.today()
    print(f"===== Date is {datestamp} ====")

    start_time = datetime.datetime.now()

    # Set the environment variable for Netmiko to use TextFMS ntc-templates library
    os.environ["NET_TEXTFSM"] = "./ntc-templates/templates"

    # Load Credentials from environment variables
    dotenv.load_dotenv(verbose=True)

    usr_env = add_2env.check_env("NET_USR")
    pwd_env = add_2env.check_env("NET_PWD")
    #
    # print(usr_env)
    # print(pwd_env)

    if not usr_env['VALID'] and not pwd_env['VALID']:
        add_2env.set_env()
        # Call the set_env function with a description indicating we are setting a password and set the
        # sensitive option to true so that the password can be typed in securely without echo to the screen
        add_2env.set_env(desc="Password", sensitive=True)

    if arguments.device:
        host = arguments.device
    else:
        host = input("Enter your device IP or FQDN: ")

    logging.basicConfig(filename=f"netmiko_log_{host}_{datestamp}.txt", level=logging.DEBUG)
    logger = logging.getLogger("netmiko")

    if arguments.mfa:
        # User is using MFA
        usr = os.environ['INET_USR']
        pwd = os.environ['INET_PWD']
        sec = os.environ['INET_PWD']
        mfa_code = input("Enter your VIP Access Security Code: ")
        mfa = f"{pwd}{mfa_code.strip()}"
    else:
        # User has account without MFA
        usr = os.environ['NET_USR']
        pwd = os.environ['NET_PWD']
        sec = os.environ['NET_PWD']
        mfa = pwd

    devdict = {
        'device_type': arguments.device_type,
        'ip' : host,
        'username' : usr,
        'password' : mfa,
        'secret' : mfa,
        'port' : arguments.port,
        'global_delay_factor': int(arguments.global_delay_factor),
    }

    net_connect = ConnectHandler(**devdict)

    response = net_connect.send_command('show version', use_textfsm=True)
    # print(f"\nResponse is of type {type(response)}\n")
    # print(response)

    # Varialbe to note if the switch is running Denali or greater. Default to True, the device is running Denali or later
    denali = True
    hostname = host
    # 'running_image': 'packages.conf'
    # 'running_image': 'cat3k_caa-universalk9.16.06.02.SPA.bin'
    # 'hardware': ['WS-C3850-24P']
    for line in response:
        hostname = line['hostname']
        print(f"\n--- Device {line['hostname']} "
              f"\n------ Model {line['hardware']}"
              f"\n------ Running version {line['version']}"
              f"\n------ Running image {line['running_image']}")

        if re.search('packages.conf', line['running_image']):
            print(f"------ Device Looks to be in INSTALL mode")
        else:
            print(f"--- WARNING! Device may be in BUNDLE mode!!")

        # pre Denali
        # [1]: Do you want to proceed with the deletion? [yes/no]: yes

        # Post Denali
        # Do you want to proceed? [y/n]y

        if re.search(r'^16.\d', line['version']):
            print(f"------ On Mountain Peak code. Use clean command: \n\t         request platform software package clean switch all verbose")
            # request platform software package clean switch all
            clean_cmd = 'request platform software package clean switch all'
        else:
            print(f"------Pre Mountain Peak code. Use clean command: \n\t         software clean verbose")
            clean_cmd = 'software clean verbose'
            denali = False

    response = net_connect.send_command('dir', use_textfsm=True)
    # print(f"\nResponse is of type {type(response)}\n")
    # print(response)

    sw_image = arguments.image_file
    file_size = int(arguments.image_size_bytes)
    md5_verification = arguments.md5_verification

    for line in response:
        # print(line)
        if re.search(sw_image, line['name']):
            # print(line['name'])
            print(f"Found bin file {sw_image} already installed!")
            load_sw = False
            break

    total_free  = int(response[0]['total_free'])
    remaining = total_free - file_size
    print(f"--- Sufficient Space Check (bytes): "
          f"Total Free: {total_free} "
          f"Space required: {file_size} "
          f"Remaining Space: {remaining}")
    if remaining >= (2 * file_size):
        print(f"--- 2X Space Check: PASS")
    else:
        print(f"--- 2X Space Check: Fail Only {remaining/file_size} x file size remains")

    # ##############################################################################################################
    # ## Executing CLAN LOAD VERIFY
    if arguments.execute_load:
        output = ''
        print(f"\n\n====== CLEANING {hostname} and LOADING {sw_image} ======\n")
        # copy http://10.222.129.1:8080/cat3k_caa-universalk9.16.12.04.SPA.bin flash:
        # verify /md5 flash:cat3k_caa-universalk9.16.12.04.SPA.bin 4bb3ad09220d0d38131662296568c717

        # ## CLEAN
        # print(f"\tExecuting CLEAN Command: {clean_cmd}\n")
        if denali:
            print(f"\tExecuting CLEAN Command for Denali or Later: {clean_cmd}\n")
            # output = net_connect.send_command(
            #     clean_cmd,
            #     expect_string=r'Do you want to proceed? [y/n]',
            #     delay_factor=10
            # )
            # output += net_connect.send_command('y\n',
            #                                    expect_string=r'#',
            #                                    delay_factor=2)

            # cmd1 = "copy running-config flash:test1.txt
            output += net_connect.send_command_timing(clean_cmd, delay_factor=6)
            if 'Do you want to proceed' in output:
                print(f"\t\tProceeding with clean...")
                output += net_connect.send_command_timing("y\n")
            # print(output)

            if 'Nothing to clean' in output:
                print(f"\t\tNothing to clean!")
        # PRE Denali Switch
        else:
            print(f"\tExecuting CLEAN Command for PRE Denali device: {clean_cmd}\n")
            # output = net_connect.send_command(
            #     clean_cmd,
            #     expect_string=r'.+Do you want to proceed with the deletion? [yes/no]:'
            # )

            output += net_connect.send_command_timing(clean_cmd, delay_factor=6)
            if 'Do you want to proceed' in output:
                print(f"\t\tProceeding with CLEAN.")
                output += net_connect.send_command_timing("yes\n")

            if 'Nothing to clean' in output:
                print(f"\t\tNothing to clean!")

            # output += net_connect.send_command('yes\n',
            #                                    expect_string=r'#',
            #                                    delay_factor=10)


        # ## COPY
        # cmd = 'copy http://10.222.129.1:8080/cat3k_caa-universalk9.16.12.04.SPA.bin flash:'
        # cmd = 'copy http://10.1.10.11/cat3k_caa-universalk9.16.12.04.SPA.bin flash:'
        cmd = f"copy http://{arguments.http_server}/{sw_image} flash:"
        print(f"\tExecuting COPY Command: {cmd}\n")
        output += net_connect.send_command(
            cmd,
            expect_string=r'Destination filename',
            delay_factor=2
        )
        output += net_connect.send_command('\n',
                                           expect_string=r'#',
                                           delay_factor=25)

        # cmd1 = "copy running-config flash:test1.txt
        # output += net_connect.send_command_timing(cmd, delay_factor=2)
        # if 'Destination filename' in output:
        #     output += net_connect.send_command_timing("\n")
        # print(output)



        # ## Verify
        # cmd = 'verify /md5 flash:cat3k_caa-universalk9.16.12.04.SPA.bin 4bb3ad09220d0d38131662296568c717'
        cmd = f"verify /md5 flash:{sw_image} {md5_verification}"
        print(f"\tExecuting VERIFY Command: {cmd}\n")
        output += net_connect.send_command(
            cmd,
            expect_string=r'#',
            delay_factor=10)

        print("\n")
        print("#" * 60)
        #       ############################################################
        print(f"######################## Run Output ########################")
        print(output)
        print("#" * 60)
        print("\n")

        response = net_connect.send_command('dir', use_textfsm=True)
        for line in response:
            if re.search(sw_image, line['name']):
                print(f"Software bin file {sw_image} loaded!")

    # verify /md5 flash:cat3k_caa-universalk9.16.12.04.SPA.bin 4bb3ad09220d0d38131662296568c717

    else:
        print(f"\n\nValidation Run Only - No Files will be loaded or Clean commands Executed.\n")

    end_time = datetime.datetime.now()
    print("\nTotal time: {}".format(end_time - start_time))
    print("\n")


# Standard call to the main() function.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Script Description",
                                     epilog="Usage: ' python load_sw' ")

    parser.add_argument('-d', '--device',
                        action='store',
                        help='Device IP or FQDN',
                        default=False)
    parser.add_argument('-t', '--device_type',
                        help='Device Types include cisco_nxos, cisco_asa, cisco_wlc Default: cisco_ios',
                        action='store',
                        default='cisco_ios')
    parser.add_argument('-p', '--port',
                        help='Port for ssh connection. Default: 22',
                        action='store',
                        default='22')
    parser.add_argument('-g', '--global_delay_factor',
                        help='Netmiko Global Delay Factor to slow everything down. Default: 1',
                        action='store',
                        default='1')
    parser.add_argument('-c', '--conn_delay_factor',
                        help='Netmiko Connection Delay Factor to add more time to connection responses. Default: 2',
                        action='store',
                        default='2')
    parser.add_argument('-m', '--mfa',
                        action='store_true',
                        help='Multi Factor Authentication will prompt for VIP code',
                        default=False)
    parser.add_argument('-x', '--execute_load',
                        action='store_true',
                        help='Execute the Software Load Process Default: False',
                        default=False)
    # 10.1.10.11
    parser.add_argument('-s', '--http_server',
                        help='HTTP Server used to download software. Default: 10.1.10.11',
                        action='store',
                        default='10.1.10.11')
    #     sw_image = r'cat3k_caa-universalk9.16.12.04.SPA.bin'
    parser.add_argument('-i', '--image_file',
                        help='Cisco Software image file Default: cat3k_caa-universalk9.16.12.04.SPA.bin',
                        action='store',
                        default=r'cat3k_caa-universalk9.16.12.04.SPA.bin')
    #     file_size = 479750531
    parser.add_argument('-b', '--image_size_bytes',
                        help='Cisco Software image file size Default: 479750531',
                        action='store',
                        default='479750531')
    #   4bb3ad09220d0d38131662296568c717
    parser.add_argument('-v', '--md5_verification',
                        help='Cisco Software image file MD5 Verification Default: 4bb3ad09220d0d38131662296568c717',
                        action='store',
                        default='4bb3ad09220d0d38131662296568c717')
    arguments = parser.parse_args()
    main()
