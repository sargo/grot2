import json
from urllib.request import urlopen, Request


def _get_access_token(gh_code, client_id, client_secret):
    pay_load = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': gh_code,
    }
    resp = urlopen(Request(
        'https://github.com/login/oauth/access_token',
        method='POST',
        data=json.dumps(pay_load).encode(),
        headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
    ))
    return json.loads(resp.read().decode('utf8')).get('access_token', None)


def get_user_data(gh_code, client_id, client_secret):
    access_token = _get_access_token(gh_code, client_id, client_secret)
    if not access_token:
        return

    resp = urlopen(
        'https://api.github.com/user?access_token={}'.format(access_token)
    )
    return json.loads(resp.read().decode('utf8'))
