from functools import wraps


def label_columns(*tables):
    columns = []
    for table in tables:
        columns.extend([c.label(f'{table.name}.{c.name}') for c in table.c])
    return columns


def format_join_row(row):
    """
    example:
    {'id': 1, 'company.id': 1, 'company.name': 'teletraan'}
    ==>
    {'id': 1, 'company': {'id': 1, 'name': 'teletraan'}}

    but if nested object all None, we should drop it.
    {'id': 1, 'company.id': None, 'company.name': None}
    ==>
    {'id': 1, 'company': None}
    """
    if not row:
        return row

    data = {}
    nested_none = {}
    for k, v in row.items():
        if '.' not in k:
            data[k] = v
            continue
        table, k = k.split('.', 1)
        if table not in data:
            data[table] = {}
            nested_none[table] = True
        data[table][k] = v
        if v is not None:
            nested_none[table] = False

    for k, v in nested_none.items():
        if v:
            data[k] = None

    return data


def format_join(index=0):
    def wrap(func):
        @wraps(func)
        async def _wrap(*args, **kwargs):
            result = await func(*args, **kwargs)
            if isinstance(result, tuple):
                result = list(result)
                data = result[index]
                if isinstance(data, list):
                    result[index] = [format_join_row(r) for r in data]
                else:
                    result[index] = format_join_row(data)
                return tuple(result)
            elif isinstance(result, list):
                return [format_join_row(r) for r in result]

            return format_join_row(result)

        return _wrap

    return wrap
