from typing import TYPE_CHECKING, Dict

from starlette.datastructures import MutableHeaders
from starlette.status import HTTP_200_OK

from starlite import get
from starlite.testing import create_test_client

if TYPE_CHECKING:
    from starlite.datastructures import State
    from starlite.types import Message


def test_before_send() -> None:
    @get("/test")
    def handler() -> Dict[str, str]:
        return {"key": "value"}

    async def before_send_hook_handler(message: "Message", state: "State") -> None:
        if message["type"] == "http.response.start":
            headers = MutableHeaders(scope=message)
            headers.append("My Header", state.message)

    def on_startup(state: "State") -> None:
        state.message = "value injected during send"

    with create_test_client(handler, on_startup=[on_startup], before_send=before_send_hook_handler) as client:
        response = client.get("/test")
        assert response.status_code == HTTP_200_OK
        assert response.headers.get("My Header") == "value injected during send"