#!/usr/bin/env python3

import argparse
import configparser
import os, asyncio

from pytradfri import Gateway
from pytradfri.api.aiocoap_api import APIFactory

INIFILE = "{0}/tradfri.ini".format(os.path.dirname(os.path.realpath(__file__)))

config = configparser.ConfigParser()

if os.path.exists(INIFILE):
    config.read(INIFILE)
else:
    print("Missing configuration")


parser = argparse.ArgumentParser()
parser.add_argument("gateway")
parser.add_argument("key")
parser.add_argument("identity")

args = parser.parse_args()

def cleanupTasks():
    print ("Number of tasks: {0}".format(len(asyncio.Task.all_tasks())))
    for task in asyncio.Task.all_tasks():
       task.cancel()

async def run():
    api_factory = APIFactory(args.gateway, args.identity)    
    psk = await api_factory.generate_psk(args.key)

    print('Generated PSK: ', psk)

    config["Gateway"] = {"ip": args.gateway}
    config["Credentials"] = {"ident": args.identity, "psk": psk}

    with open(INIFILE, "w") as configfile:
        config.write(configfile)

    # cleanupTasks()

# Entry
asyncio.get_event_loop().run_until_complete(run())