from dotenv import load_dotenv
load_dotenv()
import requests
import os

def send_msg(message, channel_name):
  url = os.getenv(f"SLACK_WEBHOOK_URL_{channel_name}")
  response = requests.post(url, data='{"text":"' + message + '"}')

def send_json(json, channel_name):
	url = os.getenv(f"SLACK_WEBHOOK_URL_{channel_name}")
	response = requests.post(url, data=json)

def send_to_nba_pipeline(message):
	send_msg(message, "nba-pipeline")



