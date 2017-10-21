
import random
import textwrap

import multidict

from . import settings
from .grotlogic.board import Board
from .grotlogic.match import Match
from .grotlogic.player import Player
from .grotlogic.random import DenseStateRandom
from .utils import get_boto3_client, timeit


client = get_boto3_client('sdb')


def init_db():
    domains = client.list_domains().get('DomainNames', [])
    for domain in ['hof', 'matches', 'users']:
        if domain not in domains:
            client.create_domain(DomainName=domain)


def clear_db():
    for domain in ['hof', 'matches', 'users']:
        client.delete_domain(DomainName=domain)


def _parse_attrs(data):
    return multidict.MultiDict(((i['Name'], i['Value']) for i in data))


def _get_first_attr(response, default=None):
    try:
        return response['Items'][0]['Attributes'][0]['Value']
    except (KeyError, IndexError):
        return default


def _split_long(text, attr):
    return [
        {'Name': '{}_{}'.format(attr, i), 'Value': line, 'Replace': True}
        for i, line in enumerate(
            textwrap.wrap(text, 1020, drop_whitespace=False))
    ]


def _join_long(attrs, attr):
    lines = []
    i = 0
    while '{}_{}'.format(attr, i) in attrs:
        lines.append(attrs['{}_{}'.format(attr, i)])
        i += 1
    return ''.join(lines)


@timeit
def _get_new_match_id(user_id):
    # get last match is exist
    response = client.select(
        SelectExpression="""SELECT match_id FROM matches
            WHERE user_id='{}' AND match_id IS NOT NULL
            ORDER BY match_id DESC LIMIT 1""".format(user_id),
        ConsistentRead=True,
    )
    # increment last match_id by 1
    return str(int(_get_first_attr(response, '0')) + 1)


@timeit
def _get_new_match_seed(new_match_id):
    # search for other users' matches with same match_id
    response = client.select(
        SelectExpression="""SELECT seed FROM matches
            WHERE match_id='{}' LIMIT 1""".format(new_match_id.zfill(6)),
        ConsistentRead=True,
    )
    # get seed from found match or generate new one
    return _get_first_attr(response, random.getrandbits(128))


@timeit
def _insert_match(match_id, api_key, user_id, seed, random_state):
    match_key = api_key + '_' + match_id
    client.put_attributes(
        DomainName='matches',
        ItemName=match_key,
        Attributes=[
            {'Name': 'match_key', 'Value': match_key, 'Replace': True},
            {'Name': 'match_id', 'Value': match_id.zfill(6), 'Replace': True},
            {'Name': 'api_key', 'Value': api_key, 'Replace': True},
            {'Name': 'user_id', 'Value': user_id, 'Replace': True},
            {'Name': 'seed', 'Value': seed, 'Replace': True},
            {'Name': 'score', 'Value': '0', 'Replace': True},
            {
                'Name': 'moves',
                'Value': str(settings.INIT_MOVES),
                'Replace': True,
            },
        ] + _split_long(random_state, 'random_state'),
        Expected={'Name': 'match_key', 'Exists': False},
    )


def new_match(api_key, user_id):
    new_match_id = _get_new_match_id(user_id)
    seed = _get_new_match_seed(new_match_id)
    random_state = DenseStateRandom(seed).getstate()
    _insert_match(new_match_id, api_key, user_id, str(seed), random_state)
    return new_match_id


def _get_match_obj(match_state):
    attrs = _parse_attrs(match_state)
    random_state = _join_long(attrs, 'random_state')
    return Match(
        Player(attrs['user_id']),
        Board.from_random_state(random_state),
        int(attrs['score']),
        int(attrs['moves']),
    )


@timeit
def get_match(api_key, match_id):
    response = client.get_attributes(
        DomainName='matches',
        ItemName='{}_{}'.format(api_key, match_id),
        ConsistentRead=True,
    )
    if 'Attributes' in response:
        return _get_match_obj(response['Attributes'])


@timeit
def update_match(api_key, match_id, match):
    match_key = api_key + '_' + match_id
    client.put_attributes(
        DomainName='matches',
        ItemName=match_key,
        Attributes=[
            {'Name': 'score', 'Value': str(match.score), 'Replace': True},
            {'Name': 'moves', 'Value': str(match.moves), 'Replace': True},
        ] + _split_long(match.board.random.getstate(), 'random_state'),
        Expected={'Name': 'score', 'Value': str(match.old_score)},
    )


@timeit
def new_user(user_id, email, api_key):
    client.put_attributes(
        DomainName='users',
        ItemName=api_key,
        Attributes=[
            {'Name': 'api_key', 'Value': api_key, 'Replace': True},
            {'Name': 'user_id', 'Value': user_id, 'Replace': True},
            {'Name': 'email', 'Value': email, 'Replace': True},
        ],
        Expected={'Name': 'api_key', 'Exists': False},
    )


@timeit
def get_user_id(api_key):
    response = client.get_attributes(
        DomainName='users',
        ItemName=api_key,
        AttributeNames=['user_id'],
        ConsistentRead=True,
    )
    return response['Attributes'][0]['Value']


def _increment_total(user_id, attr_name, value):
    response = client.get_attributes(
        DomainName='hof',
        ItemName=user_id,
        AttributeNames=[attr_name],
        ConsistentRead=True,
    )
    try:
        old_total = int(response['Attributes'][0]['Value'])
        expected = {'Name': attr_name, 'Value': str(old_total)}
    except (KeyError, IndexError):
        old_total = 0
        expected = {}

    new_total = str(old_total + value)

    client.put_attributes(
        DomainName='hof',
        ItemName=user_id,
        Attributes=[
            {'Name': attr_name, 'Value': new_total, 'Replace': True},
        ],
        Expected=expected,
    )


@timeit
def increment_total_matches(user_id):
    _increment_total(user_id, 'total_matches', 1)


@timeit
def increment_total_score(user_id, score):
    _increment_total(user_id, 'total_score', score)


@timeit
def get_hof_data():
    results = []
    response = client.select(
        SelectExpression="SELECT total_score, total_matches FROM hof",
        ConsistentRead=True,
    )
    for item in response.get('Items'):
        attrs = _parse_attrs(item['Attributes'])
        results.append({
            'user_id': item['Name'],
            'total_matches': int(attrs.get('total_matches', '1')),
            'total_score': int(attrs.get('total_score', '0')),
        })
    results.sort(
        key=lambda item: item['total_score']/item['total_matches'],
        reverse=True
    )
    return results


@timeit
def get_match_results(match_id):
    response = client.select(
        SelectExpression="""SELECT user_id, score FROM matches
            WHERE match_id='{}'""".format(match_id.zfill(6)),
        ConsistentRead=True,
    )
    matches = response.get('Items', [])
    return [_parse_attrs(match['Attributes']) for match in matches]


if __name__ == '__main__':
    clear_db()
    init_db()
