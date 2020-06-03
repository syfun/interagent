import json


def construct_request(query, variables=None, operation=''):
    req = {'query': query, 'variables': variables or {}}
    if operation:
        req['operation'] = operation
    return req


def construct_multipart_request(query, variables=None):
    return {'operations': json.dumps({'query': query, 'variables': variables}),
            'map': json.dumps({"0": ["variables.file"]})}
