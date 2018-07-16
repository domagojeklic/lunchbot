# lunchbot
Simple Slack bot for lunch ordering

# Install instructions
- install python3
- create virtual environment:
```sh
python3 -m venv .lunchbot
```
- activate virtual environment:
```sh
source .lunchbot/bin/activate
```
- install required packages:
```sh
pip install -r requirements.txt
```
- set environment variable _SLACK_BOT_TOKEN_ to your bot user OAuth access token value
```sh
export SLACK_BOT_TOKE="OAuth_access_token_value"
```
- run script:
```sh
python3 lunchbot
```
