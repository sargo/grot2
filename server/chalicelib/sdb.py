
import random
import textwrap

import boto3
import multidict
from botocore.config import Config

from .grotlogic.board import Board
from .grotlogic.match import Match
from .grotlogic.player import Player
from .grotlogic.random import DenseStateRandom
from . import settings


client = boto3.client(
    'sdb',
    use_ssl=False,
    config=Config(
        connect_timeout=10,
        read_timeout=10,
        parameter_validation=settings.debug,
    )
)


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


def _split_long(text, attr):
    return [
        {'Name': '{}_{}'.format(attr, i), 'Value': line, 'Replace': True}
        for i, line in enumerate(textwrap.wrap(text, 1020, drop_whitespace=False))
    ]


def _join_long(attrs, attr):
    lines = []
    i = 0
    while '{}_{}'.format(attr, i) in attrs:
        lines.append(attrs['{}_{}'.format(attr, i)])
        i += 1
    return ''.join(lines)


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
            {'Name': 'moves', 'Value': str(settings.INIT_MOVES), 'Replace': True},
        ] + _split_long(random_state, 'random_state'),
        Expected={'Name': 'match_key', 'Exists': False},
    )


def _get_match_obj(match_state):
    attrs = _parse_attrs(match_state)
    random_state = _join_long(attrs, 'random_state')
    return Match(
        Player(attrs['user_id']),
        Board.from_random_state(random_state),
        int(attrs['score']),
        int(attrs['moves']),
    )


def new_match(api_key, user_id):
    # get last match is exist
    response = client.select(
        SelectExpression="select match_id from matches where user_id='{}' and match_id is not null order by match_id desc limit 1".format(user_id),
        ConsistentRead=True,
    )
    try:
        # and increment it
        new_match_id = str(int(response['Items'][0]['Attributes'][0]['Value']) + 1)
    except (KeyError, IndexError):
        new_match_id = '0'

    # search for other users' matches
    response = client.select(
        SelectExpression="select seed from matches where match_id='{}' limit 1".format(new_match_id.zfill(6)),
        ConsistentRead=True,
    )
    try:
        seed = response['Items'][0]['Attributes'][0]['Value']
    except (KeyError, IndexError):
        seed = random.getrandbits(128)

    random_state = DenseStateRandom(seed).getstate()
    _insert_match(new_match_id, api_key, user_id, str(seed), random_state)

    return new_match_id


def get_match(api_key, match_id):
    response = client.get_attributes(
        DomainName='matches',
        ItemName='{}_{}'.format(api_key, match_id),
        ConsistentRead=True,
    )
    if 'Attributes' in response:
        return _get_match_obj(response['Attributes'])


def update_match(api_key, match_id, match):
    match_key = api_key + '_' + match_id
    client.put_attributes(
        DomainName='matches',
        ItemName=match_key,
        Attributes=[
            {'Name': 'score', 'Value': str(match.score), 'Replace': True},
            {'Name': 'moves', 'Value': str(match.moves), 'Replace': True},
        ] + _split_long( match.board.random.getstate(), 'random_state'),
        Expected={'Name': 'score', 'Value': str(match.old_score)},
    )

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


def increment_total_matches(user_id):
    _increment_total(user_id, 'total_matches', 1)


def increment_total_score(user_id, score):
    _increment_total(user_id, 'total_score', score)


def get_hof_data():
    results = []
    response = client.select(
        SelectExpression="select total_score, total_matches from hof",
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


def get_match_results(match_id):
    response = client.select(
        SelectExpression="select user_id, score from matches where match_id='{}'".format(match_id.zfill(6)),
        ConsistentRead=True,
    )
    matches = response.get('Items', [])
    return [_parse_attrs(match['Attributes']) for match in matches]


if __name__ == '__main__':
    clear_db()
    init_db()
