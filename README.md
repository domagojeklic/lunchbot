# lunchbot
Simple Slack bot for lunch ordering

# Install instructions
- install python3
- create virtual environment
```sh
python3 -m venv .lunchbot
```
- activate virtual environment
```sh
source .lunchbot/bin/activate
```
- install required packages
```sh
pip3 install -r requirements.txt
```
- set environment variable _SLACK_BOT_TOKEN_ to your bot user OAuth access token value
```sh
export SLACK_BOT_TOKE="OAuth_access_token_value"
```
- run script
```sh
python3 lunchbot
```

# Heroku deployment instructions
- download and install Heroku CLI
- login to Heroku:
```
heroku login
```
- set environment variable _SLACK_BOT_TOKEN_ to your bot user OAuth access token value
```
heroku config:set SLACK_BOT_TOKEN=OAuth_access_token_value
```
- create and checkout deploy branch
```
git checkout -b deploy
```
- create Procfile and define worker process
```
touch Procfile
echo 'worker: python lunchbot.py' > Procfile
```
- commit changes and push to Heroku remote master
```
git commit -m "Procfile added"
git push heroku deploy:master
```
- launch a worker
```
heroku ps:scale worker=1
```
