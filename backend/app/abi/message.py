import ipaddress

class ABIMessage:
    _abi_version = 3

    @classmethod
    def setversion(cls, version: int):
        if version < 1 or 3 < version:
            raise SyntaxError(f"protocol version {version} not implemented")
        cls._abi_version = version

    def __init__(self, msg: str):
        self._question = msg.split('\t')
        self._answers = []

    def _add_answer(self, fields: list):
        self._answers.append(fields)

    @property
    def answers(self):
        buff = ''
        for answer in self._answers:
            buff += '\t'.join(answer) + '\n'

        return buff

class ABIHandshake(ABIMessage):

    def __init__(self, msg: str):
        super(ABIHandshake, self).__init__(msg)
        if len(self._question) != 2 or self._question[0] != 'HELO' or int(self._question[1]) < 1 or 3 < int(self._question[1]):
            raise SyntaxError(f"wrong handshake message format: '{msg}'")

    @property
    def version(self):
        return int(self._question[0])

    def set_OK(self):
        self._add_answer(['OK'])

    def set_FAIL(self):
        if not self._answers:
            self._add_answer(['FAIL'])

class ABIQuery(ABIMessage):

    def __init__(self, msg: str):
        super(ABIQuery, self).__init__(msg)
        if len(self._question) != 5 + self._abi_version or self._question[0] != 'Q':
            raise SyntaxError(f"wrong question message format: '{msg}' (abi version {self._abi_version} expected)")

    @property
    def qname(self):
        return self._question[1]

    @property
    def qclass(self):
        return self._question[2]

    @property
    def qtype(self):
        return self._question[3]

    @property
    def id(self):
        return self._question[4]

    @property
    def remote_ip_address(self):
        return ipaddress.ip_address(self._question[5])

    @property
    def local_ip_address(self):
        if self._abi_version <2:
            return None
        return ipaddress.ip_address(self._question[6])

    @property
    def edns_subnet_address(self):
        if self._abi_version <3:
            return None
        return ipaddress.ip_network(self._question[7])



    def set_OK(self):
        self._add_answer(['OK'])

    def set_FAIL(self):
        if not self._answers:
            self._add_answer(['FAIL'])

