# gh-retag

Automatically fills in all GitHub repository topics to the max using AI to guess which topics are the best.


## Build

Inside the root directory.

pip install -e .

## Example

Used to generate this repo's topics.
```bash
python -m gh_topicgen -v all -m gpt-5 -r 'Urpagin/gh-topicgen'
```