#!/usr/bin/env python

__author__ = "Justin Miller"
__copyright__ = "Copyright 2015, Justin Miller"
__credits__ = []
__version__ = "1.0"
__maintainer__ = "Justin Miller"
__email__ = "justinrmiller@gmail.com"

# external dependencies
# digitalocean - pip install -U python-digitalocean

import ConfigParser
import argparse
import os
import json
import sys

import digitalocean

Config = ConfigParser.ConfigParser()
read_ok = Config.read(os.path.expanduser('~/.tanker/config'))

DELIMITER = "-"

if not read_ok:
    print("Can't parse/find config file at ~/.tanker/config")
    exit()

def config_extractor(section):
    config = {}
    options = Config.options(section)
    for option in options:
        try:
            config[option] = Config.get(section, option)
            if config[option] == -1:
                print("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            config[option] = None
    return config

try:
    access_section = config_extractor("Access")
    drop_settings_section = config_extractor("DropSettings")
    tanker_settings_section = config_extractor("TankerSettings")

    api_key = access_section['apikey']

    region = drop_settings_section['region']
    size_slug = drop_settings_section['size_slug']

    prefix = tanker_settings_section['prefix']

    if DELIMITER in prefix:
        print("Prefix cannot contain " + DELIMITER + ".")
        exit()
except KeyError, noe:
    print("Missing key: {}".format(noe))
    exit()

manager = digitalocean.Manager(token=api_key)


def create_tanker(args):
    # TODO: ADD CODE TO ENSURE A TANKER DOESN'T ALREADY EXIST OF THE SAME NAME

    if DELIMITER in args.tankername:
        print ("tanker name cannot contain -.")
        exit()

    for i in range(1, int(args.count) + 1):
        droplet = digitalocean.Droplet(
            token=api_key,
            name="{}-{}-{}".format(prefix, args.tankername, i),
            region=region,
            image=args.image,
            size_slug=size_slug,
            ssh_keys=manager.get_all_sshkeys(),
            private_networking=True
        )

        print("Creating {}".format(droplet.name))
        droplet.create()


def destroy_tanker(args):
    if "-" in args.tankername:
        print ("tanker name cannot contain -.")
        exit()

    droplets = manager.get_all_droplets()
    tanker_drops = filter(lambda s: s.name.startswith(prefix + DELIMITER + args.tankername + DELIMITER), droplets)

    for droplet in tanker_drops:
        try:
            print("Destroying {}".format(droplet.name))
            droplet.destroy()
        except digitalocean.baseapi.DataReadError, e:
            print(e)


def list_tankers(args):
    droplets = manager.get_all_droplets()
    tanker_drops = filter(lambda s: s.startswith(prefix + DELIMITER), [droplet.name for droplet in droplets])
    for droplet in tanker_drops:
        print(droplet)


def list_drops(args):
    droplets = manager.get_all_droplets()
    tanker_drops = filter(lambda s: s.name.startswith(prefix + DELIMITER), droplets)
    for drop in tanker_drops:
        print(drop.name + " " + drop.ip_address)


def list_tanker_json(args):
    droplets = manager.get_all_droplets()
    tanker_drops = filter(lambda s: s.name.startswith(prefix + DELIMITER + args.tankername), droplets)
    drop_list = []
    for drop in tanker_drops:
        node = {}
        node['name'] = drop.name
        node['ip_address'] = drop.ip_address
        node['status'] = drop.status
        drop_list.append(node)
    print json.dumps(drop_list)


def list_tanker_separated_public(args, separator):
    droplets = manager.get_all_droplets()
    tanker_drop_ips = [drop.ip_address for drop in filter(lambda s: s.name.startswith(prefix + "-" + args.tankername), droplets)]
    print separator.join(tanker_drop_ips)


def list_tanker_separated_private(args, separator):
    droplets = manager.get_all_droplets()
    tanker_drop_ips = [drop.private_ip_address for drop in filter(lambda s: s.name.startswith(prefix + "-" + args.tankername), droplets)]
    print separator.join(tanker_drop_ips)
    

def list_tanker_comma_public(args):
    list_tanker_separated_public(args, ",")


def list_tanker_space_public(args):
    list_tanker_separated_public(args, " ")


def list_tanker_comma_private(args):
    list_tanker_separated_private(args, ",")


def list_tanker_space_private(args):
    list_tanker_separated_private(args, " ")


def list_private_images(args):
    images = manager.get_my_images()
    for image in images:
        print(image)


def list_public_images(args):
    images = manager.get_global_images()
    for image in images:
        print(image)


def list_ssh_keys(args):
    ssh_keys = manager.get_all_sshkeys()
    for ssh_key in ssh_keys:
        print(ssh_key)


def main(argv):
    parser = argparse.ArgumentParser(prog='tanker')
    subparsers = parser.add_subparsers(help='commands')

    list_parser = subparsers.add_parser('list', help='List tankers')
    list_parser.set_defaults(func=list_tankers)

    create_parser = subparsers.add_parser('create', help='Create a tanker')
    create_parser.add_argument('tankername', action='store', help='Name of the tanker')
    create_parser.add_argument('count', action='store', help='Number of drops in the tanker')
    create_parser.add_argument('image', action='store', help='Image id for the drops in the tanker')
    create_parser.set_defaults(func=create_tanker)

    destroy_parser = subparsers.add_parser('destroy', help='Destroy a tanker')
    destroy_parser.add_argument('tankername', action='store', help='Name of the tanker')
    destroy_parser.set_defaults(func=destroy_tanker)

    list_private_images_parser = subparsers.add_parser('private', help='List private images')
    list_private_images_parser.set_defaults(func=list_private_images)

    list_public_images_parser = subparsers.add_parser('public', help='List public images')
    list_public_images_parser.set_defaults(func=list_public_images)

    list_ssh_keys_parser = subparsers.add_parser('keys', help='List ssh keys')
    list_ssh_keys_parser.set_defaults(func=list_ssh_keys)

    list_drops_parser = subparsers.add_parser('drops', help='List all drops')
    list_drops_parser.set_defaults(func=list_drops)

    list_json_parser = subparsers.add_parser('json', help='List a tanker as json')
    list_json_parser.add_argument('tankername', action='store', help='Name of the tanker')
    list_json_parser.set_defaults(func=list_tanker_json)

    list_comma_parser = subparsers.add_parser('comma-public', help='List a tanker\'s public ips as comma separated list')
    list_comma_parser.add_argument('tankername', action='store', help='Name of the tanker')
    list_comma_parser.set_defaults(func=list_tanker_comma_public)

    list_space_parser = subparsers.add_parser('space-public', help='List a tanker\'s public ips as space separated list')
    list_space_parser.add_argument('tankername', action='store', help='Name of the tanker')
    list_space_parser.set_defaults(func=list_tanker_space_public)

    list_comma_parser = subparsers.add_parser('comma-private', help='List a tanker\'s private ips as comma separated list')
    list_comma_parser.add_argument('tankername', action='store', help='Name of the tanker')
    list_comma_parser.set_defaults(func=list_tanker_comma_private)

    list_space_parser = subparsers.add_parser('space-private', help='List a tanker\'s private ips as space separated list')
    list_space_parser.add_argument('tankername', action='store', help='Name of the tanker')
    list_space_parser.set_defaults(func=list_tanker_space_private)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main(sys.argv)
