import unittest
from typing import TYPE_CHECKING, cast

from givenpy import given, then, when
from hamcrest import assert_that, equal_to

from tests.infrastructure.steps import prepare_api_server

if TYPE_CHECKING:
    from fastapi.testclient import TestClient  # Only imported for type checking


class TestApiHealth(unittest.TestCase):
    def test_that_health_endpoint_returns_ok_result_status(self):
        with given(
            [
                prepare_api_server(),
            ]
        ) as context:
            client = cast("TestClient", context.client)

        with when():
            response = client.get("/health/")

        with then():
            assert_that(response.status_code, equal_to(200))
