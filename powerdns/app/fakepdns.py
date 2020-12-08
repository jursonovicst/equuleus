import zmq
import argparse
import json
parser = argparse.ArgumentParser(description='fake pdns server.')

parser.add_argument('--broker', type=str, default='ipc:///tmp/broker.sock', help='broker endpoint to bind to (default: %(default)s)')

args = parser.parse_args()


if __name__ == "__main__":
    context = zmq.Context()

    #  Socket to talk to server
    print(f"Connecting to broker {args.broker}...")
    socket = context.socket(zmq.REQ)
    socket.connect(args.broker)

    init = json.loads('{"method": "initialize", "parameters": {"command": "/path/to/something", "timeout": "2000", "something": "else"}}')
    print("Sending request\n%s" % json.dumps(init, indent=4, sort_keys=True))
    socket.send_json(init)

    reply = socket.recv_json()
    print("Received reply\n%s" % json.dumps(reply, indent=4, sort_keys=True))