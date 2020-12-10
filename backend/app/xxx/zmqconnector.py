import json
import logging
from threading import Thread, Event

import zmq

from remoteapi import Query


# from backend import DNSResponder


class ZMQConnector(Thread):
    def __init__(self, name: str, stopevent: Event, context: zmq.Context, broker: str, logger: logging.Logger):
        super().__init__(name=name)
        self._stopevent = stopevent
        self._broker = broker
        self._logger = logger.getChild(name)

        self._server = context.socket(zmq.REP)

    def run(self):
        self._logger.info(f"connector started")

        self.connect()

    def connect(self):
        try:
            self._server.connect(self._broker)

            while not self._stopevent.is_set():
                response = ''
                try:
                    #  Wait for next request from client, receive as string
                    message = self._server.recv_string()
                    self._logger.debug(f"received: '{message}')")

                    # decode json, trim trailing null
                    query = Query.load(json.loads(message.rstrip('\0')))

                    # process and encode reply
                    response = json.dumps(query.reply)

                except Exception as e:
                    self._logger.warning(e)

                    # make sure, that we send something back
                    response = json.dumps({'result': False, 'log': str(e).splitlines()})

                finally:
                    # send response (or error) back
                    self._server.send_string(response)
                    self._logger.debug(json.dumps(response, indent=4, sort_keys=True))

        except Exception as e:
            self._logger.error(e)
        finally:
            self._server.close()
    #
    # def processquery(self, query: dict) -> dict:
    #     try:
    #         if 'method' not in query or 'parameters' not in query:
    #             raise SyntaxError(f"Mailformed query: {query}")
    #
    #         # log some basic info
    #         self._logger.info(f"Query: {query['method']}")
    #         self._logger.debug(query)
    #
    #         handler = getattr(self, query['method'])
    #         results = handler(query['parameters'])
    #         self._logger.info(f"Reply: {results}")
    #         return results
    #
    #     except AttributeError:
    #         self._logger.warning(f"method '{query['method']}' not implemented")
    #         return {'result': False, 'log': f"method '{query['method']}' not implemented"}
    #     except Exception as e:
    #         self._logger.warning(str(e))
    #         return {'result': False, 'log': str(e).splitlines()}
    #
    # def initialize(self, parameters: dict) -> dict:
    #     return {'result': True}
    #
    # def lookup(self, parameters: dict) -> dict:
    #     if 'qtype' not in parameters or 'qname' not in parameters or 'zone-id' not in parameters:
    #         raise SyntaxError(f"Missing parameters in lookup: {str(parameters)}")
    #
    #     self._logger.info(
    #         f"{parameters['qtype']} {parameters['qname']} {parameters['zone-id']} {parameters['remote'] if 'remote' in parameters else '-'} {parameters['local'] if 'local' in parameters else '-'} {parameters['real-remote'] if 'real-remote' in parameters else '-'}")
    #
    #     results = []
    #     for qtype, qname, content, ttl in self._dnsresponder.processquery(parameters['qtype'], parameters['qname'],
    #                                                                       realremote=ip_network(parameters[
    #                                                                                                 'real-remote']) if 'real-remote' in parameters else None):
    #         results.append({"qtype": qtype, "qname": qname, "content": content, "ttl": ttl})
    #
    #     return {"result": results}
    #
    # def getDomainMetadata(self, parameters: dict) -> dict:
    #     if 'kind' not in parameters:
    #         raise SyntaxError(f"Missing parameters in getDomainMetadata: {str(parameters)}")
    #
    #     self._logger.info(
    #         f"{parameters['kind']} {parameters['name']}")
    #
    #     if parameters['kind'] == 'ENABLE-LUA-RECORDS':
    #         return {"result": ["0"]}
    #     else:
    #         raise NotImplementedError(f"I do not support {parameters['kind']} metadata")
