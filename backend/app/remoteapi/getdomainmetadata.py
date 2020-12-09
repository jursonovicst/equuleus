from remoteapi import Query

class getDomainMetadata(Query):
    """
    Returns the value(s) for variable kind for zone name. Most commonly it’s one of NSEC3PARAM, PRESIGNED, SOA-EDIT. Can be others, too. You must always return something, if there are no values, you shall return empty array or false.

    Mandatory: No
    Parameters: name, kind
    Reply: array of strings
    """

    def __init__(self, parameters: dict):
        # check mandatory parameters
        if 'name' not in parameters or 'kind' not in parameters:
            raise SyntaxError(f"Missing parameters in getDomainMetadata: {str(parameters)}")

        super().__init__(parameters)

    @property
    def reply(self) -> dict:
        if self.kind == 'ENABLE-LUA-RECORDS':
            return {"result": ["0"]}

        return super().reply

    @property
    def name(self) -> str:
        return self._parameters['name']

    @property
    def kind(self) -> str:
        return self._parameters['kind']

    def __str__(self):
        return f"{self.name} {self.kind}"