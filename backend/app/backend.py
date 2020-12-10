import argparse
import logging
from threading import Event

from pdnsbackend import HTTPBackend, HTTPRequestHandler

parser = argparse.ArgumentParser(description='Equuleus DNS Backend for PowerDNS.')

parser.add_argument('--listen', type=str, help='Address to bind on (default: %(default)s', default='0.0.0.0')
parser.add_argument('--port', type=int, help='port to listen on (default: %(default)s', default=80)

parser.add_argument('--log-file', type=str, default='-',
                    help='File path to write logs to. Use - for stdout. (default: %(default)s')
levels = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
parser.add_argument('--log-level', type=str, default='INFO', choices=levels,
                    help='Logging severity. (default: %(default)s')

args = parser.parse_args()

if __name__ == '__main__':

    logging.basicConfig(level=args.log_level, format='%(levelname)s %(message)s')
    config_reload = Event()

    try:
        server_address = ('', 8000)

        with HTTPBackend((args.listen, args.port), HTTPRequestHandler) as server:
            # this will block
            server.serve_forever()
    except KeyboardInterrupt:
        pass
