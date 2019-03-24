"""
Discover zeroconf video streams
"""

from zeroconf import ServiceBrowser, Zeroconf


class Listener:
    def remove_service(self, zeroconf, type, name):
        print(f'Service {name} removed')

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        print(f'Service {name} added, service info: {info}')


def discover(service: str = '_axis-video._tcp.local.'):
    """Discover local services"""
    zeroconf = Zeroconf()
    listener = Listener()
    browser = ServiceBrowser(zeroconf, service, listener)
    try:
        input('Press enter to exit...')
    finally:
        zeroconf.close()
