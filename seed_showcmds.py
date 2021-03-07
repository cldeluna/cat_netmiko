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
from icecream import ic


def get_list_of_nei(dev_fqdn, root_dev, level=0, debug=False):

    # Use full show command for parsing to work!!
    response = utils.get_show_cmd_parsed(
        dev_fqdn, "show cdp neighbors detail", save_2json=False, level=level, debug=False
    )
    # Returns a list of dictionaries
    # ic(dev_fqdn)
    devices_dict = dict()
    root_dict = dict()
    filter_regex_list = r".+(WS-)?C\d{4}"

    # For every neighbor found weed out connections to self and connections to upstream root device
    for line in response:
        # ic(line)
        # ic(dev_fqdn)
        # print(f"\nline is {line}")

        # Ignore connections to self
        if line["destination_host"] != dev_fqdn:

            # Only interested in devices that are downstream not upstream to root device
            # if not re.search(root_dev, line['destination_host']):

            tmpd = dict()

            if re.search(filter_regex_list, line["platform"]):

                tmpd.update(
                    {
                        "fqdn": line["destination_host"],
                        "mgmt_ip": line["management_ip"],
                        "platform": line["platform"],
                    }
                )

                if line["destination_host"] not in devices_dict.keys():
                    devices_dict.update({line["destination_host"]: tmpd})

        else:
            root_dict = dict()

            if re.search(filter_regex_list, line["platform"]):

                root_dict.update(
                    {
                        "fqdn": line["destination_host"],
                        "mgmt_ip": line["management_ip"],
                        "platform": line["platform"],
                    }
                )


    if debug:
        print(json.dumps(devices_dict, indent=4))

    return devices_dict, root_dict


def main():

    datestamp = datetime.date.today()
    print(f"========== Date is {datestamp} =========")

    # Load Credentials from environment variables
    dotenv.load_dotenv(verbose=False)

    usr_env = add_2env.check_env("NET_USR")
    pwd_env = add_2env.check_env("NET_PWD")

    if not usr_env["VALID"] and not pwd_env["VALID"]:
        add_2env.set_env()
        # Call the set_env function with a description indicating we are setting a password and set the
        # sensitive option to true so that the password can be typed in securely without echo to the screen
        add_2env.set_env(desc="Password", sensitive=True)

    # Get Show Command Dictionary
    fn = "show_cmds.yml"
    cmd_dict = utils.read_yaml(fn)

    print(f"========== GET NEIGHBORS FROM SEED DEVICE {arguments.seed_device_fqdn} ==========")
    seed_dict, seed_dev_dict = get_list_of_nei(arguments.seed_device_fqdn, arguments.seed_device_fqdn, level=0)

    # ic(seed_dict)
    # ic(seed_dict.keys())

    print(f"\n\n------------------ Level 1 Processing Starting ------------------")
    # level1_list = []
    print(f"\n\tLook for nested switches in these devices:")
    for k in seed_dict.keys():
        print(f"\t* {k}")
    for dev in seed_dict.keys():

        print(f"\n\t- Level 1 connection to {seed_dict[dev]}....")
        level1_dict, _ = get_list_of_nei(
            seed_dict[dev]["fqdn"], arguments.seed_device_fqdn, level=1, debug=False
        )
    print(f"------------------ Level 1 Processing Complete ------------------")
    # print(json.dumps(level1_dict))

    # ic(seed_dict)
    # ic(level1_dict)
    seed_dict.update(level1_dict)
    # ic(seed_dict)

    # The keys build the json dev list used by the other scripts in this repo
    list_of_devices = list(seed_dict.keys())
    #
    # print(f"\n************* printing Level 1 list of devices with {len(list_of_devices)} devices")
    # for line in level1_dict:
    #     print(f"-- {line}")

    # ###################### START LEVEL 2 PROCESSING
    level2_dict = {}
    print(f"\n\n\t------------------ Level 2 Processing Starting ------------------")
    print(f"\n\t\tLook for nested switches in these devices:")
    for k in level1_dict.keys():
        print(f"\t\t* {k}")

    # level2_list = []
    for dev in level1_dict.keys():

        print(f"\n\t\t- Level 2 connection to {level1_dict[dev]}....")
        level2_dict, _ = get_list_of_nei(
            level1_dict[dev]["fqdn"], level1_dict[dev]["fqdn"], level=2, debug=False
        )
    print(f"\t------------------ Level 2 Processing Complete ------------------")
    # print(json.dumps(level1_dict))

    # ic(seed_dict)
    # ic(level1_dict)
    seed_dict.update(level2_dict)
    # ic(seed_dict)

    # ###################### END LEVEL 2 PROCESSING

    # FINAL CHECK
    if arguments.seed_device_fqdn in seed_dict.keys():
        print(f"\n\nOK! Seed device {arguments.seed_device_fqdn} in devices dictionary.")
    else:
        print(f"\n\nWARNING!!!!!! Seed device {arguments.seed_device_fqdn} NOT in devices dictionary.")
        print(f"{seed_dev_dict}")
        seed_dict.update(seed_dev_dict)

    # The keys build the json dev list used by the other scripts in this repo
    list_of_devices = list(seed_dict.keys())

    region, cntry, site_id, location, site_type = utils.parse_cat_hostname(arguments.seed_device_fqdn)
    # ic(utils.parse_cat_hostname(arguments.seed_device_fqdn))
    json_dir = "site_json"
    json_fn = f"{site_id}_auto_devlist.json"
    json_fp = os.path.join(os.getcwd(), json_dir, json_fn)

    utils.save_json(json_fp, list_of_devices, debug=False)

    json_dict = os.path.join(os.getcwd(), json_dir, f"{site_id}_auto_devdict.json")
    utils.save_json(json_dict, seed_dict, debug=False)

    print(f"\nDevice List saved at {json_fp}\n\n")

# Standard call to the main() function.
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Script Description", epilog="Usage: ' python seed_showcmds' "
    )

    parser.add_argument(
        "seed_device_fqdn",
        help="Enter FQDN of Seed or Root device to start CDP based device discovery",
    )

    parser.add_argument(
        "-o",
        "--output_subdir",
        help="Name of output subdirectory for show command files",
        action="store",
        default="DEFAULT_IOS_TEST",
    )
    arguments = parser.parse_args()
    main()
