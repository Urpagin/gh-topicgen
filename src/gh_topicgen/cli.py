# File: cli.py
# Author: Urpagin
# Date: 2025-08-16
# License: MIT (c) 2025 Urpagin

from gh_topicgen.config import Config
from gh_topicgen.github import GithubConn
from gh_topicgen.openai import AIClient
from github.Repository import Repository


def main(argv=None) -> int:
    # Load CLI and env vars.
    cfg: Config = Config(argv)
    print(cfg)

    # print('\n\n\n\n\n')
    # print(ai.ask(req_test, take_my_money=True))
    # return

    ai: AIClient = AIClient(token=cfg.openai_token, system=cfg.system_prompt, model=cfg.model, take_my_money=True)
    gh: GithubConn = GithubConn(cfg.gh_token)
    for repo in gh.iter_repos(rx=cfg.regex, ignore_case=cfg.ignore_case, visibility=cfg.visibility):
        new_topics: list[str] = generate_topics(repo, ai)
        print(f"[]New topics for {repo.full_name}: {new_topics}")
        repo.replace_topics(new_topics)
        print(f"#")
        break

    return 0


def generate_topics(repo: Repository, ai: AIClient) -> list[str]:
    """
    Fetches repo information and queries the AI to generate the topics.
    Returns the parsed topics. If there was an error, return the same repo topics.
    """
    repo_info: str = GithubConn.get_repo_ai_info(repo)
    ai_topics: list[str] = ai.generate_topics(repo_info)
    if not ai_topics:
        print(f"Warning: failed to generate topics for repository {repo.full_name}")

    # Ordered list of topics [CURRENT, AI]
    topics: list[str] = list(dict.fromkeys([
        *repo.get_topics(),
        *ai_topics
    ]))

    return topics[:20]
