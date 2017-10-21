
import functools
import time

import boto3
from botocore.config import Config

from . import settings


def get_boto3_client(service_name):
    return boto3.client(
        service_name,
        use_ssl=settings.USE_SSL,
        config=Config(
            connect_timeout=settings.CONNECT_TIMEOUT,
            read_timeout=settings.READ_TIMEOUT,
            parameter_validation=settings.PARAMS_VALIDATION,
            retries={'max_attempts': settings.MAX_RETRIES},
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