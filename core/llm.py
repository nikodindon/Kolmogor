"""
llm.py

Minimal HTTP client for llama-server (OpenAI-compatible /v1/chat/completions).
Uses http.client directly to avoid the openai library hanging on Windows/WSL
with llama-server (known issue documented in local-intent-coder findings).
"""

import http.client
import json
import time
import urllib.parse
from typing import Optional


class LLMClient:
    def __init__(self, config: dict):
        self.base_url = config["base_url"].rstrip("/")
        self.api_key = config.get("api_key", "sk-placeholder")
        self.model = config["model"]
        self.temperature = config.get("temperature", 0.0)
        self.max_tokens = config.get("max_out_tokens", 3000)

        parsed = urllib.parse.urlparse(self.base_url)
        self.host = parsed.hostname
        self.port = parsed.port or (443 if parsed.scheme == "https" else 80)
        self.use_ssl = parsed.scheme == "https"
        # None means no timeout (for large/slow models). Default 1800s.
        self.timeout = config.get("http_timeout", 1800)

    def complete(
        self,
        system_prompt: str,
        user_message: str,
        model_override: Optional[str] = None,
        max_tokens_override: Optional[int] = None,
        label: str = "",
    ) -> str:
        """
        Send a chat completion request. Returns the assistant message text.
        Raises on HTTP errors or malformed responses.
        """
        model = model_override or self.model
        max_tokens = max_tokens_override or self.max_tokens

        payload = {
            "model": model,
            "temperature": self.temperature,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        }

        body = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "Content-Length": str(len(body)),
        }

        t0 = time.time()
        if self.use_ssl:
            conn = http.client.HTTPSConnection(self.host, self.port, timeout=self.timeout)
        else:
            conn = http.client.HTTPConnection(self.host, self.port, timeout=self.timeout)

        try:
            conn.request("POST", "/v1/chat/completions", body=body, headers=headers)
            response = conn.getresponse()
            raw = response.read().decode("utf-8")
        finally:
            conn.close()

        elapsed = time.time() - t0

        if response.status != 200:
            raise RuntimeError(f"LLM HTTP {response.status}: {raw[:300]}")

        data = json.loads(raw)
        text = data["choices"][0]["message"]["content"]

        if label:
            tokens = data.get("usage", {}).get("completion_tokens", "?")
            prompt_tokens = data.get("usage", {}).get("prompt_tokens", "?")
            print(f"  [{label}] {prompt_tokens} prompt + {tokens} completion tokens, {elapsed:.1f}s")

        return text
