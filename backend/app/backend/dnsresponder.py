# import logging
# import ipaddress
# from typing import Union
#
# class DNSResponder:
#
#     def __init__(self, logger: logging.Logger,
#                  name: str = 'main.xpx.t-online.de.',
#                  mname: str = 'ns1.xpx.t-online.de.',
#                  rname: str = 'admin.t-online.de.',
#                  serial: int = 2020010100,
#                  refresh: int = 86400,
#                  retry: int = 7200,
#                  expire: int = 3600000,
#                  ttl: int = 5 * 60):
#         self._logger = logger
#         self._name = name.lower().rstrip('.') + '.'
#         self._mname = mname.lower().rstrip('.') + '.'
#         self._rname = rname.lower().rstrip('.') + '.'
#         self._serial = serial  # for zone transfer
#         self._refresh = refresh  # for zone transfer
#         self._retry = retry  # for zone transfer
#         self._expire = expire  # for zone transfer
#         self._ttl = ttl  # negative caching
#
#     def processquery(self, qtype: str, qname: str, realremote: Union[ipaddress.IPv4Network, ipaddress.IPv6Network] = None):
#
#         try:
#             if not qname.lower().endswith(self._name):
#                 raise ValueError(f"I am authoritative for {self._name} but not for {qname}")
#
#             handler = getattr(self, qtype)
#             return handler(qname.lower(), realremote)
#         except AttributeError:
#             raise SyntaxError(f"query type '{qtype}' not implemented")
#
#     def SOA(self, qname: str, realremote: Union[ipaddress.IPv4Network, ipaddress.IPv6Network]) -> list:
#         if qname != self._name:
#             raise ValueError(f"I am not authoritative for {qname}")
#
#         return [('SOA', self._name,
#                  f"{self._mname} {self._rname} {self._serial} {self._refresh} {self._retry} {self._expire} {self._ttl}",
#                  3600)]
#
#     def NS(self, qname: str, realremote: Union[ipaddress.IPv4Network, ipaddress.IPv6Network]) -> list:
#         if qname != self._name:
#             raise ValueError(f"I do not have a NS record for {qname}")
#
#         return [('NS', self._name, self._mname, 3500)]
#
#     def A(self, qname: str, realremote: Union[ipaddress.IPv4Network, ipaddress.IPv6Network]) -> list:
#         svc = qname[:-len(self._name)]
#
#         if svc == 'keepalive.':
#             return [('A', qname, "192.0.2.1", 3600)]
#
#         return [('A', qname, "1.2.3.4", 3600)]
#
#     def AAAA(self, qname: str, realremote: Union[ipaddress.IPv4Network, ipaddress.IPv6Network]) -> list:
#         svc = qname[:-len(self._name)]
#
#         if svc == 'keepalive.':
#             return [('AAAA', qname, "2001:db8::1", 3600)]
#
#         return [('AAAA', qname, "2003::", 3600)]
#
#     def ANY(self, qname: str, realremote: Union[ipaddress.IPv4Network, ipaddress.IPv6Network]) -> list:
#         return self.A(qname) + self.AAAA(qname)
