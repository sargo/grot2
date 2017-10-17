
import random
import textwrap

import boto3
import multidict
from botocore.config import Config
from botocore.vendored.requests.exceptions import ReadTimeout

from grotlogic.board import Board
from grotlogic.match import Match
from grotlogic.player import Player
from grotlogic.random import DenseStateRandom
import settings


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
    if 'matches' not in domains:
        client.create_domain(DomainName='matches')
    if 'users' not in domains:
        client.create_domain(DomainName='users')


def clear_db():
    client.delete_domain(DomainName='matches')
    client.delete_domain(DomainName='users')


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


def _insert_match(match_id, user_id, seed, random_state):
    match_key = user_id + '_' + match_id
    client.put_attributes(
        DomainName='matches',
        ItemName=match_key,
        Attributes=[
            {'Name': 'match_key', 'Value': match_key, 'Replace': True},
            {'Name': 'match_id', 'Value': match_id, 'Replace': True},
            {'Name': 'user_id', 'Value': user_id, 'Replace': True},
            {'Name': 'seed', 'Value': seed, 'Replace': True},
            {'Name': 'score', 'Value': '0', 'Replace': True},
            {'Name': 'moves', 'Value': str(settings.INIT_MOVES), 'Replace': True},
        ] + _split_long(random_state, 'random_state'),
        Expected={'Name': 'match_key', 'Exists': False},
    )


def _get_match_obj(match_state):
    attrs = _parse_attrs(match_state['Attributes'])
    random_state = _join_long(attrs, 'random_state')
    return Match(
        Player(attrs['user_id']),
        Board.from_random_state(random_state),
        int(attrs['score']),
        int(attrs['moves']),
    )


def new_match(user_id):
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
        SelectExpression="select seed from matches where match_id='{}' limit 1".format(new_match_id),
        ConsistentRead=True,
    )
    try:
        seed = response['Items'][0]['Attributes'][0]['Value']
    except (KeyError, IndexError):
        seed = random.getrandbits(128)

    random_state = DenseStateRandom(seed).getstate()
    _insert_match(new_match_id, user_id, str(seed), random_state)

    return new_match_id


def get_match(user_id, match_id):
    response = client.select(
        SelectExpression="select * from matches where match_key='{}_{}' limit 1".format(user_id, match_id),
        ConsistentRead=True,
    )
    matches = response.get('Items')
    if matches:
        return _get_match_obj(matches[0])


def update_match(user_id, match_id, match):
    match_key = user_id + '_' + match_id
    client_nowait = boto3.client(
        'sdb',
        use_ssl=False,
        config=Config(
            connect_timeout=10,
            read_timeout=0.01,
            parameter_validation=settings.debug,
            retries={'max_attempts': 0}
        )
    )
    try:
        client_nowait.put_attributes(
            DomainName='matches',
            ItemName=match_key,
            Attributes=[
                {'Name': 'score', 'Value': str(match.score), 'Replace': True},
                {'Name': 'moves', 'Value': str(match.moves), 'Replace': True},
            ] + _split_long( match.board.random.getstate(), 'random_state'),
            Expected={'Name': 'score', 'Value': str(match.old_score)},
        )
    except ReadTimeout:
        # for a matter of costs we just put data into db without waiting for a
        # response if the write fail then user will play the same round again
        pass


def get_match_results(match_id):
    response = client.select(
        SelectExpression="select user_id, score from matches where match_id='{}'".format(match_id),
    )
    matches = response.get('Items', [])
    return [_parse_attrs(match['Attributes']) for match in matches]


def new_user(user_id, email, api_key):
    client.put_attributes(
        DomainName='users',
        ItemName=user_id,
        Attributes=[
            {'Name': 'user_id', 'Value': user_id, 'Replace': True},
            {'Name': 'email', 'Value': email, 'Replace': True},
            {'Name': 'api_key', 'Value': api_key, 'Replace': True},
        ],
        Expected={'Name': 'user_id', 'Exists': False},
    )


def get_user_id(api_key):
    response = client.select(
        SelectExpression="select user_id from users where api_key='{}'".format(api_key),
    )
    users = response.get('Items', [])
    if users:
        return users[0]['Name']


if __name__ == '__main__':
    clear_db()
    init_db()
