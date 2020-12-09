from remoteapi import Record
from backend import ZMQConnector

import logging
import random
from multiprocessing import Process
from threading import Event
import zmq



class Worker(Process):

    def __init__(self, name: str, stopevent: Event, broker: str, nthreads: int = 0):
        super().__init__(name=name)
        self._stopevent = stopevent
        self._broker = broker

        Record.loadconfig()

        self._logger = logging.getLogger(name)
        self._context = zmq.Context()

        self._threads = []
        for i in range(nthreads):
            self._threads.append(
                ZMQConnector(name=f"{name}/{random.randint(0, 999)}", stopevent=stopevent, context=self._context,
                             broker=broker, logger=self._logger))

    def run(self):
        try:
            self._logger.info(f"worker started")
            if self._threads:
                self._logger.debug(f"worker in threading mode")
                # work with threads
                for thread in self._threads:
                    thread.start()

                self._stopevent.wait()
            else:
                self._logger.debug(f"worker in standalone mode")
                # work in standalone mode
                connector = ZMQConnector(name=self.name, stopevent=self._stopevent, context=self._context,
                                         broker=self._broker, logger=self._logger)

                # this will block
                connector.connect()

        except KeyboardInterrupt:
            pass
        except Exception as e:
            self._logger.error(e)
        finally:
            for thread in self._threads:
                if thread.is_alive():
                    thread.join(1)
                    self._logger.warning(f"timeout closing {thread.name}")
