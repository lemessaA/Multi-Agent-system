import os
from typing import Optional
import requests
from langchain.tools import tool
from config.settings import settings



SLACK_API_BASE = "htttps://slack.com/api"



def _slack_headers() -> dict:
    token = os.getenv("SLACK_BOT_TOKEN")
    if not token:
        raise ValueError("SLACK_BOT_TOKEN not found in environment variables")
    return {
        "Authorization": f"Bearer {token}",
        "Content-type": "application/json",
    }

# Send message

@tool
def send_slack_message(channel:str, message: str) -> str:
    """Send a message to a slack channel."""
    url = f"{SLACK_API_BASE}/chat.postMessage"
    payload = {
        "channel": channel,
        "text": message,
    }
    try:
        response = requests.post(url, headers=_slack_headers(), json=payload, timeout=10)
        data = response.json()
        if not data.get("ok"):
            return f"Slack error: {data.get('error')}"
        return f"Message successfully sent to {channel}"
    except requests.RequestException as e:
        return f"Slack API request failed: {str(e)}"
    
# Search messages 


@tool
def search_slack_messages(query: str, channel: str = None, max_results: int = 5) -> str:
    """Search Slack messages for a given query."""
    url = f"{SLACK_API_BASE}/search.messages" # Slack search messages endpoint
    
    params = {
        "query": query,
        "count": max_results,
    } 
    if channel:# filter by channel if provided
        params["channel"] = channel
    try:
        response = requests.get(url, headers=_slack_headers(), params=params, timeout=10) 
        data = response.json() 
        if not data.get("ok"):
            return f"Slack error: {data.get('error')}"
        messages = data.get("messages", {}).get("matches", [])
        if not messages:
            return f"No messages found for '{query}' in {channel}"
        results = [] # collect message info 
        for msg in messages:
            user = msg.get("username", "unknown") # default to unknown if username missing
            text = msg.get("text", "") # message text
            ts = msg.get("ts", "") # timestamp
            results.append(f"[{ts}] {user}: {text}")
        return "\n".join(results)
    except requests.RequestException as e:
        return f"Slack API request failed: {str(e)}"
    
# Get thread replies

@tool
def get_thread_replies(thread_id: str, channel: str) -> str:
    """Retrieve replies from a slack thread."""
    url = f"{SLACK_API_BASE}/conversations.replies"
    params = {
        "channel": channel,
        "ts": thread_id,
    }
    try:
        response = requests.get(url, headers=_slack_headers(), params=params, timeout=10)
        data = response.json()
        if not data.get("ok"):
            return f"Slack error: {data.get('error')}"
        messages = data.get("messages", [])
        if len(messages) <= 1:
            return "No replies found in thread {thread_id}"
        replies = []
        for msg in messages[1:]: # skip the first message which is the parent
            user = msg.get("username", "unknown")
            text = msg.get("text", "")
            ts = msg.get("ts", "")
            replies.append(f"[{ts}] {user}: {text}")
        return f"Replies in thread {thread_id}:\n" + "\n".join(replies)
    except requests.RequestException as e:
        return f"Slack API request failed: {str(e)}"