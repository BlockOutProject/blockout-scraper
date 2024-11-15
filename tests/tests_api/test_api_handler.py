import pytest
from aiohttp import ClientResponse
from unittest.mock import AsyncMock
from utils.handlers.api_handler import handle_api_response


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status, payload, expected_exception",
    [
        (500, {"message": "Internal Server Error"}, "Erreur API 500: Internal Server Error"),
        (404, {"message": "Not Found"}, "Erreur API 404: Not Found"),
        (400, {"message": "Bad Request"}, "Erreur API 400: Bad Request"),
    ],
)
async def test_handle_api_response_errors(status, payload, expected_exception):
    async def mock_function(*args, **kwargs):
        response = AsyncMock(spec=ClientResponse)
        response.status = status
        response.content_type = "application/json"
        response.json = AsyncMock(return_value=payload)
        return response

    decorated_function = handle_api_response()(mock_function)

    with pytest.raises(Exception, match=expected_exception):
        await decorated_function()