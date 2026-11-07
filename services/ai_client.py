import ollama


class OllamaAIClient:
    """Reusable client for sending prompts to an Ollama model."""

    def __init__(self, model_name="llama3.2"):
        """Initialize the client with a configurable model name."""
        self.model_name = model_name

    def send(self, prompt):
        """Send a prompt to Ollama and return the assistant response text."""
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        clean_prompt = prompt.strip()

        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": clean_prompt,
                    }
                ],
            )

            content = self._extract_content(response)

            if not content:
                raise RuntimeError("AI service returned an empty response.")

            return content

        except RuntimeError:
            raise

        except Exception as error:
            raise RuntimeError(
                f"AI service request failed: {error}"
            ) from error

    def _extract_content(self, response):
        """Extract assistant text from dictionary or object-style responses."""
        if response is None:
            return None

        if isinstance(response, dict):
            message = response.get("message")

            if isinstance(message, dict):
                content = message.get("content")
            else:
                content = getattr(message, "content", None)
        else:
            message = getattr(response, "message", None)
            content = getattr(message, "content", None)

        if not isinstance(content, str):
            return None

        content = content.strip()

        return content or None