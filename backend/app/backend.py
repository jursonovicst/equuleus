import argparse
import zmq
import logging
import json

parser = argparse.ArgumentParser(description='Equuleus DNS Responder - PowerDNS 0MQ remote backend.')

parser.add_argument('--broker', type=str, default='tcp://127.0.0.1:5560', help='broker endpoint to connect to (default: %(default)s)')
#parser.add_argument('--threads', type=int, help='noumber of ')
parser.add_argument('--log-file', type=str, default='-',
                    help='File path to write logs to. Use - for stdout. (default: %(default)s')
levels = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
parser.add_argument('--log-level', type=str, default='INFO', choices=levels,
                    help='Logging severity. (default: %(default)s')

args = parser.parse_args()

if __name__ == '__main__':

    context = None
    server = None

    logging.basicConfig(level=args.log_level, format='%(levelname)s dnsresponder %(message)s')



    try:
        context = zmq.Context()
        server = context.socket(zmq.REP)
        server.connect(args.broker)

        while True:
            #  Wait for next request from client
            message = server.recv_json()
            logging.debug(json.dumps(message, indent=4, sort_keys=True))

            #  Do some 'work'
            import time
            time.sleep(1)

            #  Send reply back to client
            response = json.loads('{"result":true}')
            logging.debug(json.dumps(response, indent=4, sort_keys=True))
            server.send_json(response)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.error(e)
    finally:
        if server:
            server.close()