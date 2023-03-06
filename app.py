import logging
import os

import openai
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

load_dotenv()

# Configure logging to use stdout
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

# Initialize a new Slack WebClient instance
client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])

# Event API & Web API
app = App(token=os.environ["SLACK_APP_TOKEN"])


# This gets activated when the bot is tagged in a channel
@app.event("app_mention")
def handle_message_events(event, slack_logger):
    # Log message
    logging.info(event["text"].split(">")[1])

    # Create prompt for ChatGPT
    prompt = event["text"].split(">")[1]

    # Let the user know that we are busy with the request
    try:
        client.chat_postMessage(
            channel=event["channel"],
            thread_ts=event["ts"],
            text="Foi isso que você pediu?"
        )
    except SlackApiError as e:
        logging.error("Error sending message: {}".format(e))
        slack_logger.error("Error sending message: {}".format(e))

    # Check ChatGPT
    openai.api_key = os.environ["OPENAI_API_KEY"]
    response_body = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {"role": "user", "content": f"{prompt}"}],
        max_tokens=1024,
        temperature=0.5
    )

    response = response_body["choices"][0]["message"]["content"]

    # Reply to thread
    try:
        client.chat_postMessage(
            channel=event["channel"],
            thread_ts=event["ts"],
            text=response
        )
    except SlackApiError as e:
        logging.error("Error sending message: {}".format(e))
        slack_logger.error("Error sending message: {}".format(e))


if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
