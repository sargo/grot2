import io
import os.path

import boto3
from botocore.config import Config
from botocore.vendored.requests.exceptions import ReadTimeout

import settings


client_nowait = boto3.client(
    's3',
    use_ssl=False,
    config=Config(
        connect_timeout=10,
        read_timeout=0.01,
        parameter_validation=settings.debug,
        retries={'max_attempts': 0}
    )
)

HOF_TEMPLATE = os.path.join(
    os.path.dirname(__file__), 'templates', 'hall-of-fame.html')


def update_hof(hof_data):
    hof_table = '\n'.join([
        '<tr><td>{}</td><td>{:.2%}</td></tr>'.format(
            item['user_id'],
            item['total_score']/item['total_matches'],
        )
        for item in hof_data
    ])
    with open(HOF_TEMPLATE) as f:
        html_page = f.read()
    html_page = html_page.replace('{{ hof-table }}', hof_table)
    try:
        client_nowait.upload_fileobj(
            io.BytesIO(html_page),
            'game.pythonfasterway.org',
            'hall-of-fame.html'
        )
    except ReadTimeout:
        # for a matter of costs we just upload file into s3 without waiting for a
        # response if the write fail then hall of fame will not be updated
        pass
