from typing import Any

from graphql import GraphQLError


class GraphQLExtensionError(GraphQLError):
    code = 'APOLLO_ERROR'
    message = 'apollo error'

    def __init__(self, message: str = None, **kwargs: Any):
        message = message or self.message
        extensions = {'code': self.code}
        if kwargs:
            extensions['exception'] = kwargs
        super().__init__(message=message, extensions=extensions)


class UserInputError(GraphQLExtensionError):
    code = 'USER_INPUT_ERROR'
    message = 'user input error'


class MethodNotAllowedError(GraphQLExtensionError):
    code = 'METHOD_NOT_ALLOWED'
    message = 'method not allowed, only accept ["GET", "POST"]'


class ServerInternalError(GraphQLExtensionError):
    code = 'SERVER_INTERL_ERROR'
    message = 'server internal error'


class InvalidArgument(UserInputError):
    message = 'input params is invalid!'
