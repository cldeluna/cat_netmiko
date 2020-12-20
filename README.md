# Cat Netmiko Utilities

##Synopsis

Commonly used Netmiko utilities for Cisco network devices.



##Installation



```
pip install -r requests.txt
```



##Usage



#### cat_showcmd.py

This script requires the IP or FQDN of a network device.   The script executes one or more show commands and saves the output to a timestamped file with an optional note.

The script will load credentials as environment variables and with the -m option (for MFA) concatenate a password with the VIP Access Security Code so as to minimize typing.

The script has a variety of option to tailor the script execution.

An optional device type can be provided. The default device type cisco_ios.

This script executes show commands either via a single show command provided with the -s option on the CLI when the script is called or via a set of standard show commands loaded from a YAML file based on device type.

```
(netmiko38) claudia@Claudias-iMac cat_netmiko % python cat_showcmd.py -h                             
usage: cat_showcmd.py [-h] [-t DEVICE_TYPE] [-p PORT] [-o OUTPUT_SUBDIR] [-s SHOW_CMD] [-n NOTE] [-m] dev

Script Description

positional arguments:
  dev                   Get show commands from this device (ip or FQDN) and save to file.

optional arguments:
  -h, --help            show this help message and exit
  -t DEVICE_TYPE, --device_type DEVICE_TYPE
                        Device Types include cisco_nxos, cisco_asa, cisco_wlc Default: cisco_ios
  -p PORT, --port PORT  Port for ssh connection. Default: 22
  -o OUTPUT_SUBDIR, --output_subdir OUTPUT_SUBDIR
                        Name of output subdirectory for show command files
  -s SHOW_CMD, --show_cmd SHOW_CMD
                        Execute a single show command
  -n NOTE, --note NOTE  Short note to distinguish show commands. Ex. -pre or -post
  -m, --mfa             Multi Factor Authentication will prompt for VIP code

Usage: ' python test'
(netmiko38) claudia@Claudias-iMac cat_netmiko % 

```





##License

TBD


Will become a heading
==============

Will become a sub heading
--------------

*This will be Italic*

**This will be Bold**

- This will be a list item
- This will be a list item

    Add a indent and this will end up as code
	
	

Read about Markdown:

http://daringfireball.net/projects/markdown/

http://en.wikipedia.org/wiki/Markdown

Also:

http://github.github.com/github-flavored-markdown/	