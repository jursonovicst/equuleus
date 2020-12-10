import ipaddress
import json
import logging
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import yaml

# from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from backend import DNSResponder


class HTTPRequestHandler(BaseHTTPRequestHandler):

    def setup(self):
        super(HTTPRequestHandler, self).setup()
        self.dnsresponder = DNSResponder(self.server.config['SOA'])

    def log_request(self, code='-', size='-'):

        if isinstance(code, HTTPStatus):
            code = code.value

        self.log_message('"%s" %s %s %.3f %d %s %s', self.requestline, str(code), str(size),
                         time.time() - self.requesttime, self.content_length, self.post_data, self.response)

    # def log_message(self, format: str, *args: Any):
    # logging.info(format % args)

    def handle_one_request(self):
        # remember time of request in (for logging)
        self.requesttime = time.time()
        super(HTTPRequestHandler, self).handle_one_request()

    def do_POST(self):

        reply = False
        self.response = b'{"result": false}'

        try:
            if self.path != '/dns':
                raise SyntaxError(f"unsupported path: '{self.path}'", 400)

            if 'Content-Length' not in self.headers:
                raise SyntaxError(f"Content-Length is missing from request")

            content_length = int(self.headers['Content-Length'])

            self.post_data = self.rfile.read(content_length)

            query = json.loads(self.post_data.decode('ASCII'))

            # process query
            if 'method' in query:
                if query['method'] == 'lookup' and 'parameters' in query and 'qname' in query[
                    'parameters'] and 'qtype' in query['parameters'] and 'real-remote' in query['parameters']:
                    reply = self.dnsresponder.processquery(query['parameters']['qtype'], query['parameters']['qname'],
                                                           ipaddress.ip_network(query['parameters']['real-remote']))
                elif query['method'] == 'getDomainMetadata' and 'parameters' in query and 'kind' in query['parameters']:
                    if query['parameters']['kind'] == 'ENABLE-LUA-RECORDS':
                        reply = ["0"]
                    elif query['parameters']['kind'] == 'ENABLE-LUA-RECORDS':
                        reply = ["0"]

                else:
                    raise SyntaxError(f"method {query['method']} not implemented")
            else:
                raise SyntaxError(f"missing method: {query}")

        except Exception as e:
            self.response = json.dumps({'result': False, 'log': str(e).splitlines()}).encode()
            self.content_length = len(self.response)
            self.send_response(400, type(e).__name__)
        else:
            self.response = json.dumps({"result": reply}).encode()
            self.content_length = len(self.response)
            self.send_response(200, 'OK')
        finally:
            self.send_header('Content-Type', 'text/javascript; charset=utf-8')
            self.send_header('Content-Length', str(self.content_length))
            self.end_headers()
            self.wfile.write(self.response)


class HTTPBackend(ThreadingHTTPServer):
    def server_bind(self):
        super(HTTPBackend, self).server_bind()
        logging.info(f"bound to {self.server_address}")

    def server_activate(self) -> None:
        # load config
        with open('config.yml', 'r') as stream:
            self.config = yaml.safe_load(stream)
            logging.info(f"config 'config.yml' loaded")

        super(HTTPBackend, self).server_activate()
        logging.info(f"started")

    def server_close(self):
        super().server_close()
        logging.info(f"stopped listening on {self.server_address}")
