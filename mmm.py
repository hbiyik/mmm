'''
Created on Nov 1, 2022

@author: boogie
'''
from libmmm.io import Memory
from libmmm import devices
import argparse


def addfilters(parser, required=False):
    parser.add_argument("-c", "--catalog", choices=devices.catalogs.keys(), required=required)
    parser.add_argument("-d", "--device", required=required)
    parser.add_argument("-r", "--register", required=required)
    parser.add_argument("-p", "--point", required=required)


parser = argparse.ArgumentParser(prog='mmm')

arg_command = parser.add_subparsers(dest="command", required=True)
arg_list = arg_command.add_parser('list', help="list available registers")
addfilters(arg_list)

arg_get = arg_command.add_parser('get', help="get the value of resgiter")
addfilters(arg_get)

arg_set = arg_command.add_parser('set', help="set the value of register to [value] positional argument")
addfilters(arg_set, True)
arg_set.add_argument("value", help="value to be set")

args = parser.parse_args()


def iterfilter(io=None, read=False):
    for catalog, catalogs in devices.catalogs.items():
        if args.catalog is None or catalog == args.catalog:
            for device in catalogs:
                device = device()
                if args.device is None or device.name == args.device:
                    for block in device:
                        if args.register is None or block.name == args.register:
                            if read:
                                # attach the io only when needed so we wont mmap for no reason
                                if io and not device.io:
                                    device.io = io
                                block.read()
                            for point in block:
                                if args.point is None or point.name == args.point:
                                    yield catalog, device, block, point
                        if device.io:
                            device.io = None


if args.command == "list":
    for cat, device, block, point in iterfilter():
        print("-c %s -d %s -r %s -p %s" % (cat,
                                           device.name,
                                           block.name,
                                           point.name))
elif args.command == "get":
    for cat, device, block, point in iterfilter(Memory, True):
        print("-c %s -d %s -r %s -p %s" % (cat,
                                           device.name,
                                           block.name,
                                           point))

elif args.command == "set":
    for cat, device, block, point in iterfilter(Memory):
        device.io = Memory
        block.write(point.name, args.value)
