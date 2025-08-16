# File: openai.py
# Author: Urpagin
# Date: 2025-08-16
# License: MIT (c) 2025 Urpagin
# ai_client.py
# NOTE: Don't name this file "openai.py" (it would shadow the real package).
# pip install openai
import asyncio
import random
import re
from typing import Optional

from openai import OpenAI


class AIClient:
    """
    Minimal wrapper to send ChatGPT-style prompts.

    Usage:
        ai = AIClient(token="sk-...", system="You are concise.", model="gpt-4o-mini")
        print(ai.ask("In one sentence, explain Rust ownership."))
    """

    TAKE_MY_MONEY_MODEL: str = 'gpt-5'
    _SENTINEL_INVALID: str = '__INSUFFICIENT_CONTEXT__'

    # Single-topic validator: lowercase letters/digits/hyphens, no edge/double hyphens, ≤50 chars
    _TOPIC_RE = re.compile(r'^(?=.{1,50}$)[a-z0-9]+(?:-[a-z0-9]+)*$')

    def __init__(self, token: str, *, system: str = "You are helpful and concise.", model: str = "gpt-5-nano",
                 take_my_money: bool = False):
        """
        Interface for querying an OpenAI AI model.
        :param token: OpenAI API model.
        :param system: AI system prompt.
        :param model: AI model queried.
        :param take_my_money: If True, directly uses the most expansive model at the time of writing this.
        """
        if take_my_money:
            print("Info: take_my_money is ON")
        self._client = OpenAI(api_key=token)
        self._system = system
        self._take_my_money: bool = False
        self._model = model if not take_my_money else AIClient.TAKE_MY_MONEY_MODEL
        print("Info: AI model is " + self._model)

    async def _call_with_retry(self, **kwargs):
        retries = 10
        base_delay = 1

        for attempt in range(retries):
            try:
                # offload sync call to thread
                return await asyncio.to_thread(self._client.responses.create, **kwargs)
            except Exception as e:
                # Look for OpenAI rate-limit / transient error
                if "rate limit" not in str(e).lower() and "429" not in str(e):
                    raise

                wait = base_delay * (2 ** attempt) + random.random()
                print(f"Rate limited. Retry {attempt + 1}/{retries} in {wait:.1f}s...")
                await asyncio.sleep(wait)

        raise RuntimeError("Too many rate-limit errors, giving up")

    async def ask(self, prompt: str) -> str:
        """Single-turn prompt → assistant reply (string)."""
        if self._take_my_money:
            resp = await self._call_with_retry(
                model=AIClient.TAKE_MY_MONEY_MODEL,
                instructions=self._system,
                input=prompt,
                reasoning={"effort": "high"},
            )
        else:
            resp = await self._call_with_retry(
                model=self._model,
                instructions=self._system,
                input=prompt,
            )

        return resp.output_text.strip()

    @staticmethod
    def normalize_part(part: str) -> Optional[str]:
        """
        Normalize a raw topic fragment into a GitHub-compliant topic.
        - Reject if contains any non-ASCII character.
        - Lowercase, collapse non [a-z0-9] runs to single hyphen, trim edge hyphens.
        - Map a few common language aliases (e.g., c++ -> cpp).
        - Return None if invalid/empty after normalization.
        """
        # Reject any non-ASCII (UTF-8 beyond 0x7F) characters
        if any(ord(c) > 127 for c in part):
            return None

        s = part.strip().lower().replace(' ', '-').replace('_', '-')

        # Common language aliases
        aliases = {
            "c++": "cpp",
            "c-plus-plus": "cpp",
            "c#": "c-sharp",
            "f#": "f-sharp",
        }
        s = aliases.get(s, s)

        # Replace any non [a-z0-9] run with a single hyphen, then trim
        s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')

        # Empty after cleanup? invalid.
        if not s:
            return None

        # Must match strict topic pattern (≤50 chars, kebab-case)
        if not AIClient._TOPIC_RE.fullmatch(s):
            return None

        return s

    async def generate_topics(self, repo_info: str) -> list[str]:
        """
        Tries to generate the new topics.
        :param repo_info: Repository information like explained in the system_prompt.txt
        :return: A list of topics, not empty hopefully...
        """

        resp: str = await self.ask(repo_info)
        if resp == AIClient._SENTINEL_INVALID:
            return []

        parts: list[str] = list(dict.fromkeys(resp.split(',')))
        return [self.normalize_part(t) for t in parts]
