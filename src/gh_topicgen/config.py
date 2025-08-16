# File: config.py
# Author: Urpagin
# Date: 2025-08-16
# License: MIT (c) 2025 Urpagin

import argparse
import os
from pathlib import Path
from typing import Union, Optional, Literal

from dotenv import load_dotenv


class Config:
    def __init__(self, argv):
        args: argparse.Namespace = self._load_cli(argv)

        env_file: str = args.env_file
        gh: str = args.gh_token
        oai: str = args.openai_token
        allow_prompt: bool = not args.no_input
        self.visibility: Literal["public", "private", "all"] = args.visibility[0]
        self.regex: str = args.regex
        self.ignore_case: bool = args.ignore_case
        self._prompt_file: Path = args.prompt
        self.system_prompt: str = self._load_system_prompt()
        self.model: str = args.model

        self.gh_token: Union[str, None] = gh
        self.openai_token: Union[str, None] = oai

        # Lenient: populate the missing values if there are. Priority CLI if conflicts.
        load_dotenv()
        load_dotenv(env_file)
        self._load_env()

        if not (self.gh_token and self.openai_token) and allow_prompt:
            self._load_user()
        elif not allow_prompt and not (self.gh_token and self.openai_token):
            raise RuntimeError(
                'Failed to load config. Please populate GH_TOKEN and OPENAI_TOKEN in a .env file or use cli args'
            )

    def __str__(self) -> str:
        return str(self.__dict__)

    def _load_env(self):
        """Tries to load via environment variables."""
        # Load environment variables
        gh: Optional[str] = os.getenv("GH_TOKEN").strip()
        oai: Optional[str] = os.getenv("OPENAI_TOKEN").strip()

        if not self.gh_token and gh:
            self.gh_token = gh
        if not self.openai_token and oai:
            self.openai_token = oai

        if not (self.gh_token and self.openai_token):
            print("Warning: failed to load config via environment variables; reading from user input.")
            print("\nInfo: please make a .env file and populate it with the tokens.")
            return False

        return True

    def _load_user(self) -> None:
        """Loads by asking the user."""
        print()
        self.gh_token = self._ask_user("GitHub token")
        print()
        self.openai_token = self._ask_user("OpenAI token")

    def _load_system_prompt(self) -> str:
        """Read the system prompt text. Prefer project root, then CWD, then <root>/src."""
        p = self._prompt_file  # Path from args; default "system_prompt.txt"

        if p.is_absolute():
            if not p.is_file():
                raise FileNotFoundError(f"System prompt not found: {p}")
            return p.read_text(encoding="utf-8")

        cwd = Path.cwd().resolve()
        # Detect project root by walking up for pyproject.toml or .git
        root = None
        for d in (cwd, *cwd.parents):
            if (d / "pyproject.toml").is_file() or (d / ".git").exists():
                root = d
                break

        candidates = []
        if root:
            candidates.append(root / p)  # project root first
        candidates.append(cwd / p)  # then current working dir
        if root:
            candidates.append(root / "src" / p)  # then <root>/src

        for c in candidates:
            if c.is_file():
                return c.read_text(encoding="utf-8")

        tried = "\n  - ".join(str(x) for x in candidates)
        raise FileNotFoundError(f"System prompt file not found. Looked in:\n  - {tried}")

    @staticmethod
    def _load_cli(argv) -> argparse.Namespace:
        """Loads the CLI and parses the arguments."""

        p = argparse.ArgumentParser(prog="gh-retag", description="Manage tokens/config.")

        p.add_argument("--gh-token", "-g", help="GitHub token (overrides env; aka GH_TOKEN)")
        p.add_argument(
            "--openai-token", "-o", help="OpenAI token (overrides env; aka OPENAI_API_KEY)"
        )
        p.add_argument(
            "--model", "-m", help="Which OpenAI model to use (https://platform.openai.com/docs/models)",
            default="gpt-5-nano"
        )
        p.add_argument(
            "--prompt", "-p", help="Path to AI system prompt file.",
            default="system_prompt.txt", type=Path
        )
        p.add_argument("--regex", "-r",
                       help="Regex for repo names (matches against full_name, e.g., 'Urpagin/slpcli').")
        p.add_argument("--ignore-case", "-i", action="store_true", help="Case-insensitive regex.")

        p.add_argument(
            "--env-file",
            "-e",
            metavar="PATH",
            help="Path to .env to load first (default: auto-detect)",
        )
        p.add_argument(
            "--no-input",
            action="store_true",
            help="Do not prompt; fail if tokens are missing",
        )

        p.add_argument("--visibility", "-v", choices=["public", "private", "all"], nargs=1, required=True)

        # then parse.
        return p.parse_args(argv)

    @staticmethod
    def _ask_user(prompt: str) -> str:
        """Read user input"""
        while True:
            usr_int: str = input(f"{prompt}\n-> ").strip()
            if usr_int:
                return usr_int
