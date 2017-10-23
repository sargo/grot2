
import functools
import time

import boto3
from botocore.config import Config

from . import settings


def get_boto3_client(
        service_name,
        use_ssl=settings.USE_SSL,
        connect_timeout=settings.CONNECT_TIMEOUT,
        read_timeout=settings.READ_TIMEOUT,
        parameter_validation=settings.PARAMS_VALIDATION,
        max_retries=settings.MAX_RETRIES
    ):
    return boto3.client(
        service_name,
        use_ssl=use_ssl,
        config=Config(
            connect_timeout=connect_timeout,
            read_timeout=read_timeout,
            parameter_validation=parameter_validation,
            retries={'max_attempts': max_retries},
        )
    )


def timeit(func):
    @functools.wraps(func)
    def timed(*args, **kw):
        ts = time.time()
        result = func(*args, **kw)
        te = time.time()
        print('EXEC TIME: {}  {:.2f} ms'.format(
            func.__name__, (te - ts) * 1000))
        return result
    return timed


def print_match_state(data):
    print('score: ', str(data['score']), '    moves: ', str(data['moves']))
    print(data['preview']['directions'], data['preview']['points'])
    rows_points = data['board']['points'].split('\n')
    rows_directions = data['board']['directions'].split('\n')
    for pair in zip(rows_directions, rows_points):
        print(*pair)
    print('')
