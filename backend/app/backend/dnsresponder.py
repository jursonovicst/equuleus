import ipaddress
import random
from typing import Union


class NotAuthError(Exception):
    pass


class DNSResponder:
    def __init__(self, config: dict):
        self._name: str = config['name'].lower().rstrip('.') + '.' if 'name' in config else 'example.com.'
        self._mname: str = config['mname'].lower().rstrip('.') + '.' if 'mname' in config else 'ns1.example.com.'
        self._rname: str = config['rname'].lower().rstrip('.') + '.' if 'rname' in config else 'admin.example.com.'

        self._serial: int = 2020010201
        self._refresh: int = int(config['refresh']) if 'refresh' in config else 86400
        self._retry: int = int(config['retry']) if 'retry' in config else 7200
        self._expire: int = int(config['_expire']) if '_expire' in config else 3600000
        self._ttl: int = int(config['_ttl']) if '_ttl' in config else 60


    def processquery(self, qtype: str, qname: str,
                     realremote: Union[ipaddress.IPv4Network, ipaddress.IPv6Network] = None):
        try:
            if not qname.lower().endswith(self._name):
                raise NotAuthError(f"I am authoritative for {self._name} but not for {qname}")

            handler = getattr(self, qtype)
            return handler(qname.lower(), realremote)
        except AttributeError:
            return []


    def SOA(self, qname: str, realremote: Union[ipaddress.IPv4Network, ipaddress.IPv6Network]) -> list:
        if qname != self._name:
            return []

        return [{'qtype': 'SOA', 'qname': self._name,
                 'content': f"{self._mname} {self._rname} {self._serial} {self._refresh} {self._retry} {self._expire} {self._ttl}",
                 'ttl': 3600}]


    def ANY(self, qname: str, realremote: Union[ipaddress.IPv4Network, ipaddress.IPv6Network]) -> list:
        return self.NS(qname, realremote) + self.A(qname, realremote) + self.AAAA(qname, realremote) + self.TXT(qname,
                                                                                                                realremote)


    def NS(self, qname: str, realremote: Union[ipaddress.IPv4Network, ipaddress.IPv6Network]) -> list:
        if qname != self._name:
            return []

        return [{'qtype': 'NS', 'qname': self._name, 'content': self._mname, 'ttl': 3500}]


    def A(self, qname: str, realremote: Union[ipaddress.IPv4Network, ipaddress.IPv6Network]) -> list:
        svc = qname[:-len(self._name)]
        if not svc:
            return []
        elif svc == 'keepalive.':
            return [{'qtype': 'A', 'qname': qname, 'content': "192.0.2.1", 'ttl': 3600}]
        elif svc == 'random.':
            return [{'qtype': 'A', 'qname': qname,
                     'content': f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
                     'ttl': 60, 'scopeMask': realremote.prefixlen}]

        return [{'qtype': 'A', 'qname': qname, 'content': "1.2.3.4", 'ttl': 3600, 'scopeMask': realremote.prefixlen}]


    def AAAA(self, qname: str, realremote: Union[ipaddress.IPv4Network, ipaddress.IPv6Network]) -> list:
        svc = qname[:-len(self._name)]

        if not svc:
            return []
        elif svc == 'keepalive.':
            return [{'qtype': 'AAAA', 'qname': qname, 'content': "2001:db8::1", 'ttl': 3600}]

        return [{'qtype': 'AAAA', 'qname': qname, 'content': "2003::", 'ttl': 3600, 'scopeMask': realremote.prefixlen}]


    def TXT(self, qname: str, realremote: Union[ipaddress.IPv4Network, ipaddress.IPv6Network]) -> list:
        svc = qname[:-len(self._name)]

        if not svc:
            return []
        elif svc == 'keepalive.':
            return [{'qtype': 'TXT', 'qname': qname, 'content': "webisonline", 'ttl': 3600}]

        return []
