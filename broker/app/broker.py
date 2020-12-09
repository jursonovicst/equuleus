import zmq
import argparse
import logging
import threading
import json
import binascii

parser = argparse.ArgumentParser(description='0MQ broker.')

parser.add_argument('frontend', type=str, help='frontend endpoint to bind to')
parser.add_argument('backend', type=str, help='backend endpoint to bind to')
#parser.add_argument('--frontend', type=str, default='ipc:///tmp/broker.sock', help='frontend endpoint to bind to (default: %(default)s)')
#parser.add_argument('--backend', type=str, default='tcp://*:5560', help='backend endpoint to bind to (default: %(default)s)')
parser.add_argument('--log-file', type=str, default='-',
                    help='File path to write logs to. Use - for stdout. (default: %(default)s')
levels = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
parser.add_argument('--log-level', type=str, default='INFO', choices=levels,
                    help='Logging severity. (default: %(default)s')

args = parser.parse_args()


def capture_run(ctx):
    """ this is the run method of the CAPTURE thread that logs the messages
    going through the broker """
    sock = ctx.socket(zmq.PAIR)
    sock.connect("inproc://capture") # connect to the caller
    sock.send(b"") # signal the caller that we're ready
    run = True
    while run:
        try:
            msg = sock.recv()

            # JSON?
            try:
                logging.debug(f"JSON:\n{json.dumps(json.loads(msg), indent=4, sort_keys=True)} ({binascii.hexlify(msg)})")
            except:
                # string?
                try:
                    logging.debug(f"String: '{msg.decode()}' ({binascii.hexlify(msg)})")
                except:
                    # bytes
                    logging.debug(f"bytes: '{binascii.hexlify(msg)}'")

        except zmq.error.ContextTerminated:
            run = False
        except Exception as e:
            logging.warning(f"{type(e)} error: {e} processing msg: {binascii.hexlify(msg)}")
            topic = None
            obj = sock.recv()


    sock.close()


if __name__ == "__main__":
    context = None
    frontend = None
    backend = None
    capture = None
    capture_thread = None

    logging.basicConfig(level=args.log_level, format='%(levelname)s broker %(message)s')

    try:
        context = zmq.Context()

        # Socket facing clients
        frontend = context.socket(zmq.ROUTER)
        frontend.bind(args.frontend)

        # Socket facing services
        backend  = context.socket(zmq.DEALER)
        backend.bind(args.backend)

        # Socket pair for debug capture
        if logging.DEBUG == logging.root.level:
            capture = context.socket(zmq.PAIR)
            capture.bind("inproc://capture")
            capture_thread = threading.Thread(target=capture_run, args=(context,), daemon=True)
            capture_thread.start()
            capture.recv()  # wait for signal from peer thread

        logging.info(f"Starting 0MQ broker on '{args.frontend}' frontend and '{args.backend}' backend...")
        zmq.proxy(frontend, backend, capture if capture else None)

        # We never get here...
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.error(e)
    finally:
        logging.info(f"Exiting 0MQ broker...")
        if frontend:
            frontend.close()
        if backend:
            backend.close()
        if context:
            context.term()

        if capture:
            capture.close()
            if capture_thread.is_alive():
                capture_thread.join(2)

