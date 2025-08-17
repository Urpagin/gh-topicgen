# gh-topicgen

Automatically fills in all GitHub repository topics to the max using AI to guess which topics are the best.

> [!NOTE]
> Still rough around the edges, untested & lacks features.

## Why? 🧠

I found myself wanting to fill each of my repos’ topics as much as I could, but it came at the cost of slowly and
sequentially thinking about what keywords to choose. So of course I will take hours of my time to shave off a few
seconds of creative thought.

## Brief 📦

A Python program that uses GitHub and OpenAI’s APIs, wiring them together to make an AI model generate a list of
topics (the tags/keywords you see on the repository page) based on the repo’s metadata:
i.e., title, description, existing tags, programming languages, and of course the contents of the legendary `README.md`
file.

## Behavior ⚙️

Final topics are ordered as: existing topics first, then AI-generated ones.
If you already have 5 topics, those five remain; the app only appends new topics until it reaches the maximum (`GithubConn.MAX_TOPIC_COUNT`). You can change this limit programmatically if you prefer to cap the list at N topics.


## Quickstart 🚀

> [!TIP]
> As we’ll be working with dotfiles (files beginning with a `.`), your file manager may not show them by default.
> For a better experience, enable “show hidden files”.

1. **Clone the repository and enter it.**

   ```bash
   git clone https://github.com/Urpagin/gh-topicgen.git
   cd gh-topicgen
   ```

2. **Before running, populate the two API tokens you’ll need.**
   Copy the `.env.example` file to `.env` and follow the instructions inside.

   ```bash
   cp .env.example .env
   ```

3.A **\[Linux/macOS] Create a Python virtual environment and activate it (optional).**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3.B **\[Windows] Create a Python virtual environment and activate it (optional).**

```bash
py -m venv .venv
.\.venv\Scripts\activate
```

4. **Install the app (editable mode).**

   ```bash
   pip install -e .
   ```

5. **Run it to generate relevant topics for a repository.**

> [!CAUTION]
> For a first run, narrow changes to a single repository to try things out.
> Use `--regex`/`-r`, e.g. `ghtopicgen -v public -r 'Urpagin/slpcli'` to affect only the
> [Urpagin/slpcli](https://github.com/Urpagin/slpcli) repository.
> More info in the [Usage section](#usage).

   ```bash
   ghtopicgen --visibility public --regex 'YourUserName/YourRepoTitle'
   ```

> [!TIP]
> If calling `ghtopicgen` doesn’t work, try:
> `python3 -m gh_topicgen <your arguments>`

To quickly get the hang of the app, skim the [Examples section](#examples--uses).

## Usage 🛠️

```text
$ python -m gh_topicgen -h
usage: ghtopicgen [-h] [--gh-token GH_TOKEN] [--openai-token OPENAI_TOKEN] [--model MODEL] [--prompt PROMPT] [--regex REGEX] [--ignore-case]
                  [--env-file PATH] [--no-input] [--take-my-money] --visibility {public,private,all}

Manage tokens/config.

optional arguments:
  -h, --help            show this help message and exit
  --gh-token GH_TOKEN, -g GH_TOKEN
                        GitHub token (overrides env; aka GH_TOKEN)
  --openai-token OPENAI_TOKEN, -o OPENAI_TOKEN
                        OpenAI token (overrides env; aka OPENAI_API_KEY)
  --model MODEL, -m MODEL
                        Which OpenAI model to use (https://platform.openai.com/docs/models)
  --prompt PROMPT, -p PROMPT
                        Path to AI system prompt file.
  --regex REGEX, -r REGEX
                        Regex for repo names (matches against full_name, e.g., 'Urpagin/slpcli').
  --ignore-case, -i     Case-insensitive regex.
  --env-file PATH, -e PATH
                        Path to .env to load first (default: auto-detect)
  --no-input            Do not prompt; fail if tokens are missing
  --take-my-money       Special model spec: GPT-5 Thinking with high effort. If set, any --model value is ignored.
  --visibility {public,private,all}, -v {public,private,all}
                        What type of repositories to use.
```

## Examples / Uses 💡

Used to generate this repo’s topics:

```bash
ghtopicgen -v public -m gpt-5 -r 'Urpagin/gh-topicgen'
```

Generate the topics of **all** your repos (private + public) using the best model currently:

```bash
ghtopicgen -v all --take-my-money
```

Generate the topics of **all** your repos using the fastest and cheapest model (default model):

```bash
ghtopicgen -v all -m gpt-5-nano
```

## AI Instructions 🤖

The system prompt given to the model is stored in `system_prompt.txt`.
Feel free to tweak it as you wish.

## Compatibility 🧪

Made with compatibility in mind, avoiding highly modern 3.11/3.12-only features.

Compatible with **Python ≥ 3.9**.

```bash
$ vermin --no-tips src/gh_topicgen/*
Minimum required versions: 3.9
Incompatible versions:     2
```

## Acknowledgements 🙏

* [The PyGithub library](https://github.com/pygithub/pygithub) — interacting with the GitHub REST API
* [The official OpenAI Python library](https://github.com/openai/openai-python) — interacting with the OpenAI REST API

## License 📄

Every file in the repository falls under the MIT License.

MIT © 2025 Urpagin.
