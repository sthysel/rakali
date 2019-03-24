"""
Discover IP cameras on local LAN
"""

import nmap
import click
from ipaddress import ip_interface
from pprint import pprint

import socket
from ..discover import discover


class OptionConfig(object):
    def __init__(self):
        pass


option_config = click.make_pass_decorator(OptionConfig, ensure=True)


def my_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except IOError:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def get_local_net():
    return ip_interface(my_ip() + '/24').network


@click.group(context_settings=dict(max_content_width=120))
@click.version_option()
@option_config
def cli(config):
    """ Discover IP cameras on local LAN """


@cli.command('service')
@click.option(
    '-s',
    '--service',
    help='Look for service',
    default='axis',
    show_default=True,
)
@option_config
def service(config, service):
    """
    Scanning for video feed services
    """

    print(f'Scanning {local_lan} for {vendor_name} cameras or NVRs')
    discover()


@cli.command('cams')
@click.option(
    '-n',
    '--vendor-name',
    help='Look for IP cameras from vendor',
    default='axis',
    show_default=True,
)
@click.option(
    '-l',
    '--local-lan',
    help='Look for IP cameras on network',
    default=get_local_net(),
    show_default=True,
)
def cams(vendor_name, local_lan):
    """
    Discover local IP cameras using vendor name
    """
    print(f'Scanning {local_lan} for {vendor_name} cameras or NVRs')
    found = []
    nm = nmap.PortScanner()
    nm.scan(hosts=str(local_lan), )

    for _name in nm.all_hosts():
        host = nm[_name]
        for hostname in host['hostnames']:
            if hostname['name'].find(vendor_name) >= 0:
                found.append(_name)
    pprint(found)
