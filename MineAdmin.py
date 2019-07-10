import os
import os.path
import dotenv
import requests
import json
import datetime
import subprocess

dotenvPath = os.path.join(os.path.dirname(__file__), '.env')
dotenv.load_dotenv(dotenvPath)

DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
CHECK_CHANNEL_ID = os.environ['CHECK_CHANNEL_ID']

url = f'https://discordapp.com/api/channels/{CHECK_CHANNEL_ID}/messages'

queryString = {'limit':'1'}

payload = ''
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bot {DISCORD_TOKEN}',
    'cache-control': 'no-cache',
}

response = requests.request('GET', url, data='', headers=headers, params=queryString)
lastMessageJson = json.loads(response.text).pop()

userName = lastMessageJson['author']['username'] + '#' + lastMessageJson['author']['discriminator']
content = lastMessageJson['content']
timestamp = datetime.datetime.strptime(lastMessageJson['timestamp'][:-13], "%Y-%m-%dT%H:%M:%S")
validationTime = datetime.datetime.now() - datetime.timedelta(minutes=2)

# 古い投稿は無視
if validationTime > timestamp:
    exit()

SERVICE_ACCOUNT_ID = os.environ['SERVICE_ACCOUNT_ID']
GCP_PROJECT_NAME = os.environ['GCP_PROJECT_NAME']
MINECRAFT_INSTANCE_NAME = os.environ['MINECRAFT_INSTANCE_NAME']
MINECRAFT_INSTANCE_ZONE = os.environ['MINECRAFT_INSTANCE_ZONE']

payload = ''
option = ''
if content == '/start':
    payload = '{"content":"Starting up server...","tts":false,"embed":{}}'
    option = 'start'

elif content == '/stop':
    payload = '{"content":"Stopping server...","tts":false,"embed":{}}'
    option = 'stop'

if payload != '':
    requests.request('POST', url, data=payload, headers=headers, params='')
    command = f'/snap/bin/gcloud --account={SERVICE_ACCOUNT_ID} compute instances {option} {MINECRAFT_INSTANCE_NAME} --project {GCP_PROJECT_NAME} --zone {MINECRAFT_INSTANCE_ZONE}'
    subprocess.call(command.split())
    