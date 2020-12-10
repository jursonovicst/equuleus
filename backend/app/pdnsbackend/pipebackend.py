import logging
import os
from socketserver import UnixStreamServer, StreamRequestHandler, ForkingMixIn

import yaml

from abi import ABIQuery, ABIHandshake


class PipeRequestHandler(StreamRequestHandler):
    _config = None

    _config_default = {
        'listener': {
            'timeout': 1000
        }
    }

    @classmethod
    def loadconfig(cls, configfile: str = 'config.yml'):
        with open(configfile, 'r') as stream:
            cls._config = yaml.safe_load(stream)
            logging.debug(cls._config)

            # TODO: do here: 'main.xpx.t-online.de.'.lower().rstrip('.') + '.'

    @classmethod
    def getconfig(cls, topic: str, key: str):
        if not cls._config or topic not in cls._config or key not in cls._config[topic]:
            if topic not in cls._config_default or key not in cls._config_default[topic]:
                return None
            return cls._config_default[topic][key]
        return cls._config[topic][key]

    def handle(self):
        while True:
            data = self.rfile.readline().strip()
            if data:
                line = data.decode('ASCII')
                if line[0] == 'H':
                    try:
                        msg = ABIHandshake(line)
                    except:
                        msg.set_FAIL()
                    else:
                        msg.set_OK()
                elif line[0] == 'Q':
                    msg = ABIQuery(line)



                else:
                    print(f"Unknown: {line}")
                    continue
                self.wfile.write(msg.answers.encode())

            else:
                return


class PipeServer(ForkingMixIn, UnixStreamServer):
    def server_activate(self) -> None:
        super(PipeServer, self).server_activate()
        logging.info(f"started")

    def server_bind(self):
        super(PipeServer, self).server_bind()
        logging.info(f"bound to {self.server_address}")

    def server_close(self):
        super().server_close()
        logging.info(f"stopped listening on {self.server_address}")
        os.unlink(self.server_address)

# class PipeBackend2:
#     _server = None
#     _workers = []
#     _config = None
#     _stop = Event()
#
#     @classmethod
#     def bind(cls, addr: str):
#
#         poller = select.poll()
#
#         try:
#             logging.info(f"started")
#             # check if the socket already exists, remove if it does
#             if os.path.exists(addr):
#                 logging.warning(f"Unix domain socket '{addr}' exists, removing")
#                 os.unlink(addr)
#
#             # create server socket
#             cls._server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM, 0)
#             cls._server.setblocking(False)
#             cls._server.bind(addr)
#
#             # listen for incoming connections (this WILL NOT block)
#             cls._server.listen()
#             logging.info(f"listening on '{addr}")
#
#             # set up the poller, use flags to accept connection TODO: check if both needed
#             poller.register(cls._server, select.POLLIN | select.POLLPRI | select.POLLERR)
#
#             while not cls._stop.is_set():
#                 # Wait for at least one of the sockets to be ready for processing
#                 events = poller.poll(cls.getconfig('listener', 'timeout'))
#
#                 for fd, flag in events:
#
#                     if flag & (select.POLLIN | select.POLLPRI):
#                         # just to be sure...
#                         if fd == cls._server.fileno():
#                             # a "readable" server socket is ready to accept a connection
#                             connection, client_address = cls._server.accept()
#                             logging.info(f"accepted connection from {client_address}")
#
#                             worker = PipeBackend(connection)
#                             worker.start()
#                             cls._workers.append(worker)
#                     elif flag & select.POLLERR:
#                         logging.error(f"Poll error")  # TODO: add error message
#                         cls._stop.set()
#
#
#         except Exception as e:
#             logging.error(e)
#             cls._stop.set()
#         except KeyboardInterrupt:
#             cls._stop.set()
#         finally:
#             # unregister
#             poller.unregister(cls._server)
#
#             # close listening socket
#             if cls._server:
#                 cls._server.close()
#                 logging.info(f"stopped listening on '{addr}'")
#             os.unlink(addr)
#
#             # wait for workers
#             for worker in cls._workers:
#                 if worker.is_alive():
#                     if worker.join(1) is None:
#                         if worker.is_alive():
#                             worker.terminate()
#
#             logging.info(f"exited")
#
#
#     def __init__(self, connection: socket):
#         super().__init__(name=names.get_full_name())
#         self._socket = connection
#         self._logger = mp.get_logger()
#         self._logger.name = self.name
#
#     def run(self):
#         self._logger.debug(f"worker started")
#         self._socket
#         self._logger.debug(f"worker exited")
