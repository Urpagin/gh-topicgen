# File: github.py
# Author: Urpagin
# Date: 2025-08-16
# License: MIT (c) 2025 Urpagin
# Requires: pip install PyGithub
import re
from re import Pattern
from typing import Generator, Literal, Union, Iterable, Optional, Iterator

from github import Github, NamedUser, AuthenticatedUser
from github.Repository import Repository

Visibility = Literal["public", "private", "all"]


class GithubConn:
    # Maximum number of topics a repository can have.
    MAX_TOPIC_COUNT: int = 20

    def __init__(self, token: str):
        """
        Args:
            token: Personal access token with at least 'repo' scope for private repos.
        """
        if not token:
            raise RuntimeError('GitHub token must not be empty.')

        self._token = token
        self._gh: Github = Github(token)

    def iter_repos(self, rx: str, ignore_case: bool = False, visibility: Visibility = "all") -> Generator[
        Repository, None, None]:
        """
        Yield repositories for the authenticated user filtered by visibility.

        Args:
            visibility: "public", "private", or "all".
            ignore_case: if True, ignore case in regex matching.
            rx: Regex pattern to filter. If None, no filtering done.
        """
        user: Union[NamedUser, AuthenticatedUser] = self._gh.get_user()

        compiled = self._compile_user_regex(pattern=rx, ignore_case=ignore_case)
        it = user.get_repos() if rx is None else self._filter_repos_by_regex(user.get_repos(), compiled)
        for repo in it:  # includes owned + collaborations
            if visibility == "public" and repo.private:
                continue
            if visibility == "private" and not repo.private:
                continue
            yield repo

    @staticmethod
    def get_repo_topics(repo: Repository) -> list[str]:
        return repo.get_topics()

    @staticmethod
    def replace_repo_topics(repo: Repository, labels: Iterable[str]) -> None:
        """
        Replaces the topics of a ``Repository``.
        If there are more topics than ``GithubConn.MAX_TOPIC_COUNT``,
        truncates to remove the excedent.
        """
        # Truncate.
        repo.replace_topics(list(labels)[:GithubConn.MAX_TOPIC_COUNT])

    @staticmethod
    def _compile_user_regex(pattern: Optional[str], ignore_case: bool = False) -> Optional[Pattern[str]]:
        if not pattern:
            return None
        flags = re.IGNORECASE if ignore_case else 0
        try:
            return re.compile(pattern, flags)
        except re.error as e:
            raise SystemExit(f"Invalid --regex: {e}")

    @staticmethod
    def _filter_repos_by_regex(
            repos: Iterable[Repository],
            rx: Optional[Pattern[str]],
    ) -> Iterator[Repository]:
        if rx is None:
            yield from repos
            return
        for r in repos:
            if rx.search(r.full_name):
                yield r

    @staticmethod
    def get_repo_ai_info(repo: Repository) -> str:
        """
    Info like:
    REPO_NAME: <name>
    DESCRIPTION: <text>
    EXISTING_TOPICS: topic1, topic2, ...
    LANGUAGES: Rust, Python, C++
    README: <full content here>
        """
        name: str = repo.full_name
        desc: str = repo.description
        topics: str = ",".join(GithubConn.get_repo_topics(repo))
        langs: str = ",".join(repo.get_languages().keys())
        readme: str = repo.get_readme().decoded_content.decode(encoding='utf-8')

        return (
            f"REPO_NAME: {name}\n"
            f"DESCRIPTION: {desc}\n"
            f"EXISTING_TOPICS: {topics}\n"
            f"LANGUAGES: {langs}\n"
            f"README: \n\n{readme}"
        )
