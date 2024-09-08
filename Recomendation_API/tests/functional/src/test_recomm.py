import uuid
from http import HTTPStatus

import pytest

from tests.functional.db.postgres_db import delete_records, insert_in_db, get_access_token


@pytest.mark.parametrize(
    'api_url, expected_answer, test_name',
    [
        (
                '/user-recommendations/dd805001-54bd-46f4-a799-6572c8008343',
                {
                    'status': HTTPStatus.OK,
                    'length': 13
                },
                'user-recomm'
        ),
        (
                '/user-recommendations/68cc079f-7e93-4057-8bb7-c7f978a4a2cc',
                {
                    'status': HTTPStatus.NOT_FOUND,
                    'length': 1
                },
                'user-recomm'
        ),
        (
                '/similar-movies/4b8ac97d-a619-4af8-b2e0-d194361e6a39',
                {
                    'status': HTTPStatus.OK,
                    'length': 9
                },
                'similar-movies'
        ),
        (
                '/similar-movies/5c870a2b-effc-47ee-adb7-a750b94b5bbb',
                {
                    'status': HTTPStatus.NOT_FOUND,
                    'length': 1
                },
                'similar-movies'
        )
    ]
)
@pytest.mark.asyncio
async def test_recomm(
        make_request,
        api_url: str,
        expected_answer: dict,
        test_name: str
):
    api_url_prefix = '/api/v1/recomm'
    access_data = await get_access_token()
    token = {'Authorization': f"Bearer {access_data['access_token']}", 'X-Request-Id': str(uuid.uuid4())}

    match test_name:

        case 'user-recomm':

            await delete_records(test_name)
            await insert_in_db(test_name)

            response = await make_request(
                api_url=f'{api_url_prefix}{api_url}',
                headers=token
            )
            assert len(response['body']) == expected_answer['length']

        case 'similar-movies':
            await delete_records(test_name)
            await insert_in_db(test_name)

            response = await make_request(
                api_url=f'{api_url_prefix}{api_url}',
                headers=token
            )
            assert len(response['body']) == expected_answer['length']

        case _:
            raise ValueError(f"Unknown test_name: {test_name}")

    assert response['status'] == expected_answer['status']
