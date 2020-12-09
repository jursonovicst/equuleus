from backend import Worker

import argparse
import logging
from threading import Event
import petname
from multiprocessing.connection import wait as mpwait

parser = argparse.ArgumentParser(description='Equuleus DNS Responder - PowerDNS 0MQ remote backend.')

parser.add_argument('broker', type=str, help='broker endpoint to connect to')
parser.add_argument('--log-file', type=str, default='-',
                    help='File path to write logs to. Use - for stdout. (default: %(default)s')
levels = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
parser.add_argument('--log-level', type=str, default='INFO', choices=levels,
                    help='Logging severity. (default: %(default)s')
parser.add_argument('--workers', type=int, default=2, help='Number of workers to start. (default: %(default)s')
parser.add_argument('--threads', type=int, default=0, help='Number of threads per worker to start. (default: %(default)s')

args = parser.parse_args()

if __name__ == '__main__':

    logging.basicConfig(level=args.log_level, format='%(levelname)s %(message)s')
    stop = Event()
    workers = {}

    try:
        for i in range(args.workers):
            worker = Worker(name=petname.Generate(2), stopevent=stop, broker=args.broker, nthreads=args.threads)
            worker.start()
            workers[worker.sentinel] = worker


        while workers and not stop.is_set():
            for sentinel in mpwait(workers.keys()):
                # process exited
                if workers[sentinel].exitcode != 0:
                    # respawn if non-zero error code...
                    logging.warning(f"Worker {workers[sentinel].name} exited with code {workers[sentinel].exitcode}, respawn...")

                    worker = Worker(name=petname.Generate(2), stopevent=stop, broker=args.broker, nthreads=args.threads)
                    worker.start()
                    workers[worker.sentinel] = worker
                else:
                    logging.debug(f"Worker {workers[sentinel].name} exited cleanly")

                # remove exited
                workers.pop(sentinel)

    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.error(e)
    finally:
        stop.set()
        for worker in workers.values():
            if worker.is_alive():
                worker.join(1)
                logging.warning(f"Timeout closing {worker.name}")
                worker.terminate()



