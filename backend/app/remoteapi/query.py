import importlib
import logging


class Query:
    @classmethod
    def load(cls, query: dict):
        if 'method' not in query or 'parameters' not in query:
            raise SyntaxError(f"Mailformed query: {query}")

        module = importlib.import_module('remoteapi')
        class_ = getattr(module, query['method'])
        return class_(query['parameters'])

    def __init__(self, parameters: dict):
        self._parameters = parameters
        logging.debug(str(self))

    @property
    def reply(self) -> dict:
        return {"result": []}

    def __str__(self):
        return str(self._parameters)




