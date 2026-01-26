import os 
import requests
from typing import Optional
from langchain.tools import tool



# Notion API helper


NOTION_API_URL = "https://www.notion.com/"
NOTION_API_VERSION = "2022-06-28"    # official Notion API version



def _make_notion_header() -> dict:
    token = os.getenv("NOTION_TOKEN")
    if not token:
        raise ValueError("Notion token not found in environment variables.")
    return {
        "Authorization":f"Bearer {token}",
        "Notion-Version": NOTION_API_VERSION,
        "content-type": "application/json",
    }


# Notion Search Tool

@tool
def search_notion(query: str, max_results: int=5) -> str:
    """Search Notion workspaces and pages for a given query,"""
    headers = _make_notion_header()
    url = f"{NOTION_API_URL}/search"
    payload = {
        "query": query,
        "page_size": max_results,
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        results = response.json().get("results", [])
        if not results:
            return f"No results found for query: {query}"
        
        # collect basic information 

        pages_info = []
        for page in results:
            title = "Untitled" # default title
            properties = page.get("properties", {}) # get page properties {} this fallback  if the key properties is missing
            if properties:
                title = properties.get("title", [{"text": "Untitled"}])[0].get("text", {}).get("content", "Untitled")
            pages_info.append({
                "id": page["id"],
                "title": title,
                "url": page["url"],
            })
        return str(pages_info)
    except requests.RequestException as e:
        return f"Notion API Request failed : {str(e)}"


@tool
def get_notion_page(page_id: str) -> str:
    
    """
    Retrieve content from a specified Notion page by its ID.
    Returns  a text summary of the page content.

    """
    headers = _make_notion_header()
    url = f"{NOTION_API_URL}/blocks/{page_id}/chaildren"
    try:
        response = requests.get(url, headers=headers, timeout=10) 
        response.raise_for_status()
        blocks = response.json().get("results", [])
        if not blocks:
            return f"No content found for page ID: {page_id}"
        


        # Extract text content from blocks
        texts = []

        for block in blocks:
            if block["type"] == "paragraph": # exract paragraph text
                texts.append("".join([text["plain_text"] for text in block["paragraph"]["text"]])) # extract text from paragraph block
            elif block["type"] == "heading_1":
                texts.append("# " + "".join([text["plain_text"] for text in block["heading_1"]["text"]])) # extract heading 1 text
            elif block["type"] == "heading_2":
                texts.append("## " + "".join([text["plain_text"] for text in block["heading_2"]["text"]]))
            elif block["type"] == "heading_3":
                texts.append("### " + "".join([text["plain_text"] for text in block["heading_3"]["text"]]))
            # Add more block types as needed
        if not texts:
            return f"No text content found for page ID: {page_id}."
        return f"Content of Notion page {page_id}:\n" + "\n\n".join(texts)
    except requests.RequestException as e:
        return f"Notion API Request failed: {str(e)}"