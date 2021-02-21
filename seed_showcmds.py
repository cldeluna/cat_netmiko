#!/usr/bin/python -tt
# Project: cat_netmiko
# Filename: seed_showcmds
# claudia
# PyCharm

from __future__ import absolute_import, division, print_function

__author__ = "Claudia de Luna (claudia@indigowire.net)"
__version__ = ": 1.0 $"
__date__ = "2/20/21"
__copyright__ = "Copyright (c) 2018 Claudia"
__license__ = "Python"

import argparse
import utils
import add_2env
import os
import re
import dotenv
import datetime
import shutil
import json

def get_list_of_nei(dev, root_dev):

    # Use full show command for parsing to work!!
    response = utils.get_show_cmds_parsed(dev, arguments.output_subdir, "show cdp neighbors detail")
    # Returns a list of dictionaries

    device_lod = []
    filter_regex_list = r'.+WS-'
    for line in response:
        tmpd = dict()

        if re.search(filter_regex_list, line['platform']):

            tmpd.update({
                'fqdn': line['destination_host'],
                'mgmt_ip': line['management_ip'],
                'platform': line['platform']

            })
            device_lod.append(tmpd)

    print(json.dumps(device_lod, indent=4))


def main():

    datestamp = datetime.date.today()
    print(f"===== Date is {datestamp} ====")

    # Load Credentials from environment variables
    dotenv.load_dotenv(verbose=True)

    usr_env = add_2env.check_env("NET_USR")
    pwd_env = add_2env.check_env("NET_PWD")
    #
    #     # print(usr_env)
    #     # print(pwd_env)

    if not usr_env['VALID'] and not pwd_env['VALID']:
        add_2env.set_env()
        # Call the set_env function with a description indicating we are setting a password and set the
        # sensitive option to true so that the password can be typed in securely without echo to the screen
        add_2env.set_env(desc="Password", sensitive=True)

    fn = "show_cmds.yml"
    cmd_dict = utils.read_yaml(fn)

    # devdict = utils.create_cat_devobj_from_json_list("10.1.10.212")
    #     # print(devdict)

    dev = "10.1.10.212"


# Standard call to the main() function.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Script Description",
                                     epilog="Usage: ' python seed_showcmds' ")

    #parser.add_argument('all', help='Execute all exercises in week 4 assignment')
    parser.add_argument('-o', '--output_subdir', help='Name of output subdirectory for show command files', action='store',
                        default="DEFAULT_IOS_TEST")
    arguments = parser.parse_args()
    main()
