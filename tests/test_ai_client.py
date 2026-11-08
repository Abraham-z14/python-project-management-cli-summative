import pytest

from services.ai_client import OllamaAIClient


def test_default_model():
    client = OllamaAIClient()

    assert client.model_name == "llama3.2"


def test_custom_model():
    client = OllamaAIClient("custom-model")

    assert client.model_name == "custom-model"


@pytest.mark.parametrize(
    "prompt",
    ["", "   ", "\n\t"],
)
def test_blank_prompt_is_rejected(prompt):
    client = OllamaAIClient()

    with pytest.raises(
        ValueError,
        match="cannot be empty",
    ):
        client.send(prompt)


def test_none_prompt_is_rejected():
    client = OllamaAIClient()

    with pytest.raises(
        ValueError,
        match="cannot be empty",
    ):
        client.send(None)


def test_successful_dictionary_response(monkeypatch):
    def fake_chat(model, messages):
        assert model == "llama3.2"
        assert messages == [
            {
                "role": "user",
                "content": "Hello",
            }
        ]

        return {
            "message": {
                "content": "Hello back!"
            }
        }

    monkeypatch.setattr(
        "services.ai_client.ollama.chat",
        fake_chat,
    )

    client = OllamaAIClient()

    assert client.send("  Hello  ") == "Hello back!"


def test_successful_object_response(monkeypatch):
    class FakeMessage:
        content = "Object response"

    class FakeResponse:
        message = FakeMessage()

    monkeypatch.setattr(
        "services.ai_client.ollama.chat",
        lambda model, messages: FakeResponse(),
    )

    client = OllamaAIClient()

    assert client.send("Hello") == "Object response"


def test_service_failure_becomes_runtime_error(
    monkeypatch,
):
    def fail_chat(model, messages):
        raise ConnectionError("service offline")

    monkeypatch.setattr(
        "services.ai_client.ollama.chat",
        fail_chat,
    )

    client = OllamaAIClient()

    with pytest.raises(
        RuntimeError,
        match="AI service request failed",
    ):
        client.send("Hello")


def test_empty_ai_response_is_rejected(monkeypatch):
    monkeypatch.setattr(
        "services.ai_client.ollama.chat",
        lambda model, messages: {
            "message": {
                "content": "   "
            }
        },
    )

    client = OllamaAIClient()

    with pytest.raises(
        RuntimeError,
        match="empty response",
    ):
        client.send("Hello")