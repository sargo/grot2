
from . import settings
from .utils import get_boto3_client, timeit


client = get_boto3_client('apigateway', use_ssl=True)


@timeit
def get_api_key(user_id):
    resp = client.get_api_keys(nameQuery=user_id, includeValues=True)
    items = resp.get('items')
    if items:
        return items[0]['value']


@timeit
def new_api_key(user_id, email):
    response = client.create_api_key(
        name=user_id,
        description=email,
        enabled=True,
    )
    client.create_usage_plan_key(
        usagePlanId=settings.API_USAGE_PLAN_ID,
        keyId=response['id'],
        keyType='API_KEY',
    )
    return response['value']