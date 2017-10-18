import boto3
from botocore.config import Config

client = boto3.client(
    'apigateway',
    use_ssl=False,
    config=Config(
        connect_timeout=10,
        read_timeout=10,
        parameter_validation=settings.debug,
    )
)


def get_api_key(user_id):
    resp = client.get_api_keys(nameQuery=user_id, includeValues=True)
    items = resp.get('items')
    if items:
        return items[0]['value']


def new_api_key(user_id, email):
    response = client.create_api_key(
        name=user_id,
        description=email,
        enabled=True,
    )
    client.create_usage_plan_key(
        usagePlanId='37vn6y',
        keyId=response['id'],
        keyType='API_KEY',
    )
    return response['value']