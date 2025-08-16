# gh-retag

Automatically fills in all GitHub repository topics to the max using AI to guess which topics are the best.

> [!WARNING]
> Needs heavy polishments.

## Build

Inside the root directory.

pip install -e .

## Example

Used to generate this repo's topics.
```bash
python -m gh_topicgen -v all -m gpt-5 -r 'Urpagin/gh-topicgen'
```

## Compatibility

Made with compatibility in mind, developped using Python 3.8 instead of 3.13. And a more tangible proof using [vermin](https://github.com/netromdk/vermin):

```bash
$ vermin src/gh_topicgen/*                                                                                                                            [23:38:51]
Tips:
- Generic or literal annotations might be in use. If so, try using: --eval-annotations
  But check the caveat section: https://github.com/netromdk/vermin#caveats
- You're using potentially backported modules: argparse, typing
  If so, try using the following for better results: --backport argparse --backport typing
- Since '# novm' or '# novermin' weren't used, a speedup can be achieved using: --no-parse-comments
(disable using: --no-tips)

Minimum required versions: 3.8
Incompatible versions:     2
```
