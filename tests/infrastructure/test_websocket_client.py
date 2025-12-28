import pytest

from tests.helpers.mock_ws_client import MockWebSocketClient


def test_mock_websocket_client_replays_messages() -> None:
    client = MockWebSocketClient(messages=["a", "b"])

    client.connect()

    assert client.receive() == "a"
    assert client.receive() == "b"
    with pytest.raises(StopIteration):
        client.receive()

    client.close()
    with pytest.raises(RuntimeError):
        client.receive()
