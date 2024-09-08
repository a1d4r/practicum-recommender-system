import asyncio

import aiohttp
import pytest_asyncio

# from redis.asyncio.client import Redis

from tests.functional.settings import get_settings


@pytest_asyncio.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


# @pytest_asyncio.fixture(name='redis_cl', scope='session')
# async def redis_cl():
#    redis_conn = Redis(host=test_settings.redis_host, socket_connect_timeout=1, port=6379)
#    yield redis_conn
#    await redis_conn.close()


@pytest_asyncio.fixture(name='cl_session', scope='session')
async def cl_session():
    cl_session = aiohttp.ClientSession()
    yield cl_session
    await cl_session.close()


@pytest_asyncio.fixture(name='make_request')
def make_request(cl_session):
    async def inner(api_url, payload=None, headers=None):
        full_url = get_settings().service_url + api_url
        async with cl_session.request(
                method='GET',
                url=full_url,
                headers=headers,
                json=payload
        ) as response:
            status = response.status
            body = await response.json()
            return {'status': status, 'body': body}

    return inner
