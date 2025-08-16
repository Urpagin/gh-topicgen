# File: cli.py
# Author: Urpagin
# Date: 2025-08-16
# License: MIT (c) 2025 Urpagin
import asyncio

from gh_topicgen.config import Config
from gh_topicgen.github import GithubConn
from gh_topicgen.openai import AIClient
from github.Repository import Repository

CONCURRENT_WORKERS: int = 10


async def main(argv=None) -> int:
    # Load CLI and env vars.
    cfg: Config = Config(argv)
    print(cfg)

    # Max N number of running workers.
    # Each worker calls an OpenAI model response and PUTs to GitHub for the topics.

    sem = asyncio.Semaphore(CONCURRENT_WORKERS)
    print(f"Beginning with a max of {CONCURRENT_WORKERS} concurrent workers.")

    ai: AIClient = AIClient(token=cfg.openai_token, system=cfg.system_prompt, model=cfg.model, take_my_money=True)
    gh: GithubConn = GithubConn(cfg.gh_token)

    ai_worker_tasks = []
    gh_fetcher_tasks = []
    count: int = 1
    for repo in gh.iter_repos(rx=cfg.regex, ignore_case=cfg.ignore_case, visibility=cfg.visibility):
        print(f"[#{count}] [{repo.full_name}] Fetching...")
        count += 1
        ai_worker_tasks.append(worker(repo, ai, sem))

    # Launch all tasks at once. This call blocks until all have joined.
    print(f"Launching {len(ai_worker_tasks)} with a concurrency of {CONCURRENT_WORKERS}...")
    await asyncio.gather(*ai_worker_tasks)

    return 0


async def worker(repo: Repository, ai: AIClient, sem: asyncio.Semaphore, skip_full: bool = True):
    async with sem:
        try:
            current_topic_count: list[str] = await asyncio.to_thread(repo.get_topics)
            if skip_full and len(current_topic_count) >= GithubConn.MAX_TOPIC_COUNT:
                print(
                    f"Info [{repo.full_name}]: skipping; {current_topic_count}/{GithubConn.MAX_TOPIC_COUNT} topics already set.")
                return

            new_topics: list[str] = await generate_topics(repo, ai)
            print(f"[{repo.full_name}] new topics({len(new_topics)}): {new_topics}")
            await asyncio.to_thread(repo.replace_topics, new_topics)
            print(f"[{repo.full_name}] topics replaced!")
        except Exception as e:
            print(f"Error [{repo.full_name}]: {e}")


async def generate_topics(repo: Repository, ai: AIClient) -> list[str]:
    """
    Fetches repo information and queries the AI to generate the topics.
    Returns the parsed topics. If there was an error, return the same repo topics.
    """
    repo_info: str = GithubConn.get_repo_ai_info(repo)
    ai_topics: list[str] = await ai.generate_topics(repo_info)
    if not ai_topics:
        print(f"Warning: failed to generate topics for repository {repo.full_name}")

    # Ordered list of topics [CURRENT, AI]
    topics: list[str] = list(dict.fromkeys([
        *repo.get_topics(),
        *ai_topics
    ]))

    return topics[:20]
