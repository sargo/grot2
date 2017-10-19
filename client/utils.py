
import json
from urllib.error import HTTPError
from urllib.request import urlopen, Request


def json_urlopen(*args, **kwargs):
    if 'data' in kwargs:
        kwargs['data'] = json.dumps(kwargs['data']).encode()

    headers = kwargs.setdefault('headers', {})
    if 'Accept' not in headers:
        headers['Accept'] = 'application/json'
    if (
            kwargs.get('method') in ['PUT', 'POST'] and
            'data' in kwargs and
            'Content-type' not in headers
        ):
        headers['Content-type'] = 'application/json'

    try:
        response = urlopen(Request(*args, **kwargs))
    except HTTPError as err:
        response = err

    raw_data = response.read()
    result = {'code': response.code, 'raw': raw_data}
    try:
        result['json'] = json.loads(raw_data.decode())
    except ValueError:
        pass

    if response.code != 200:
        try:
            print(result['json']['Message'])
        except KeyError:
            print(result['raw'])

    return result




