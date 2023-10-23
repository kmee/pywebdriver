from requests import get

from pif.base import BasePublicIPChecker, registry

__title__ = 'pif.checkers.ip42.pif_ip_checker'
__author__ = 'Bruno Santeramo'
__copyright__ = 'Copyright (c) 2016 Bruno Santeramo'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ('Ip42PlIPChecker',)


class Ip42PlIPChecker(BasePublicIPChecker):
    """Checks IPs using ip.42.pl"""

    uid = 'ip.42.pl'

    def get_public_ip(self):
        """Get public IP.

        :return str:
        """
        try:
            return get('http://ip.42.pl/raw', verify=False).text
        except Exception as err:
            if self.verbose:
                self.logger.error(err)


registry.register(Ip42PlIPChecker)
