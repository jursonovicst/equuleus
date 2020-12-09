import importlib
import ipaddress
import logging
from typing import Union

import yaml

from remoteapi import Query


class lookup(Query):
    """
    This method is used to do the basic query. You can omit auth, but if you are using DNSSEC this can lead into trouble.

    Mandatory: Yes
    Parameters: qtype, qname, zone_id
    Optional parameters: remote, local, real-remote
    Reply: array of qtype,qname,content,ttl,domain_id,scopeMask,auth
    Optional values: domain_id, scopeMask and auth
    Note: priority field is required before 4.0, after 4.0 priority is added to content. This applies to any resource record which uses priority, for example SRV or MX.
    """

    def __init__(self, parameters: dict):
        # check mandatory parameters
        if 'qtype' not in parameters or 'qname' not in parameters or 'zone-id' not in parameters:
            raise SyntaxError(f"Missing parameters in lookup: {str(parameters)}")
        super().__init__(parameters)

        self._record = Record.load(self)

    @property
    def reply(self) -> dict:
        results = []
        for qtype, qname, content, ttl, scopeMask in self._record.reply:
            result = {"qtype": qtype, "qname": qname, "content": content, "ttl": ttl}
            if scopeMask:
                result['scopeMask'] = scopeMask
            results.append(result)

        return {"result": results}

    @property
    def qtype(self) -> str:
        return self._parameters['qtype']

    @property
    def qname(self) -> str:
        return self._parameters['qname']

    @property
    def zone_id(self) -> str:
        return self._parameters['zone-id']

    @property
    def remote(self) -> Union[ipaddress.IPv4Address, ipaddress.IPv6Address, None]:
        if 'remote' in self._parameters:
            return ipaddress.ip_address(self._parameters['remote'])
        else:
            return None

    @property
    def local(self) -> Union[ipaddress.IPv4Address, ipaddress.IPv6Address, None]:
        if 'local' in self._parameters:
            return ipaddress.ip_address(self._parameters['local'])
        else:
            return None

    @property
    def real_remote(self) -> Union[ipaddress.IPv4Network, ipaddress.IPv6Network, None]:
        if 'real-remote' in self._parameters:
            return ipaddress.ip_network(self._parameters['real-remote'])
        else:
            return None

    def __str__(self):
        return f"{self.qtype} {self.qname} {self.zone_id} {self.remote} {self.local} {self.real_remote}"


class Record:
    @classmethod
    def load(cls, query: lookup):
        module = importlib.import_module('remoteapi')
        class_ = getattr(module, query.qtype)
        return class_(query)

    _config = None

    @classmethod
    def loadconfig(cls, configfile: str = 'config.yml'):
        """

        :param dsfile:
        :return:
        :raises yaml.YAMLError
        """
        with open(configfile, 'r') as stream:
            cls._config = yaml.safe_load(stream)
            logging.debug(cls._config)

            # TODO: do here: 'main.xpx.t-online.de.'.lower().rstrip('.') + '.'

    @classmethod
    def name(cls) -> str:
        return cls._config['SOA']['name']

    @classmethod
    def mname(cls) -> str:
        return cls._config['SOA']['mname']

    @classmethod
    def rname(cls) -> str:
        return cls._config['SOA']['rname']

    @classmethod
    def serial(cls) -> int:
        return cls._config['SOA']['serial']

    @classmethod
    def refresh(cls) -> int:
        return cls._config['SOA']['refresh']

    @classmethod
    def retry(cls) -> int:
        return cls._config['SOA']['retry']

    @classmethod
    def expire(cls) -> int:
        return cls._config['SOA']['expire']

    @classmethod
    def ttl(cls) -> int:
        return cls._config['SOA']['ttl']

    def __init__(self, query: lookup):
        self._query = query

        logging.debug(str(self))

    @property
    def svc(self):
        return self._query.qname[:-len(self.name())]

    @property
    def reply(self) -> list:
        return []

    def __str__(self):
        return f"{self._query.qname} {self._query.remote} {self._query.real_remote}"


class A(Record):

    @property
    def reply(self) -> list:
        if self.svc == 'keepalive.':
            return [('A', self._query.qname, "192.0.2.1", 3600, None)]

        return [('A', self._query.qname, "1.2.3.4", 3600, self._query.real_remote.prefixlen)]


class AAAA(Record):

    @property
    def reply(self) -> list:
        if self.svc == 'keepalive.':
            return [('AAAA', self._query.qname, "2001:db8::1", 3600, None)]

        return [('AAAA', self._query.qname, "2003::", 3600, self._query.real_remote.prefixlen)]


class ANY(Record):

    @property
    def reply(self) -> list:
        a = A(self._query)
        aaaa = AAAA(self._query)
        return a.reply + aaaa.reply


class SOA(Record):

    @property
    def reply(self) -> list:
        if self._query.qname != self.name():
            raise ValueError(f"I am not authoritative for {self._query.qname} (but for {self.name()})")

        return [('SOA', self.name(),
                 f"{self.mname()} {self.rname()} {self.serial()} {self.refresh()} {self.retry()} {self.expire()} {self.ttl()}",
                 3600, None)]


class NS(Record):

    @property
    def reply(self) -> list:
        if self._query.qname != self.name():
            raise ValueError(f"I do not have a NS record for {self._query.qname}")

        if self.svc == 'keepalive.':
            return [('AAAA', self._query.qname, "2001:db8::1", 3600, None)]

        return [('NS', self.name(), self.mname(), 3600, None)]
