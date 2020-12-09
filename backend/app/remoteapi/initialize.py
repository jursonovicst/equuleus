from remoteapi import Query

class initialize(Query):
    """
    Called to initialize the backend. This is not called for HTTP connector. You should do your initializations here.

    Mandatory: Yes (except HTTP connector)
    Parameters: all parameters in connection string
    Reply: true on success / false on failure
    """

    @property
    def reply(self) -> dict:
        return {'result': True}

    def __str__(self):
        return str(self._parameters)
