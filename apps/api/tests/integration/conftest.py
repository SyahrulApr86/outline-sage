from __future__ import annotations

import pytest
import pytest_asyncio
import redis.asyncio as redis
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

from outline_sage_api.db import create_engine, create_session_factory, init_db


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:16-alpine") as container:
        yield container


@pytest.fixture(scope="session")
def redis_container():
    with RedisContainer("redis:7-alpine") as container:
        yield container


@pytest_asyncio.fixture
async def session_factory(postgres_container):
    url = postgres_container.get_connection_url().replace("psycopg2", "asyncpg")
    engine = create_engine(url)
    await init_db(engine)
    factory = create_session_factory(engine)
    yield factory
    await engine.dispose()


@pytest_asyncio.fixture
async def redis_client(redis_container):
    host = redis_container.get_container_host_ip()
    port = redis_container.get_exposed_port(6379)
    client = redis.Redis(host=host, port=int(port), decode_responses=True)
    yield client
    await client.flushall()
    await client.aclose()
