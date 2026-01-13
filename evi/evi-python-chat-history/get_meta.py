import os
import json
import http.client
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

API_HOST = "api.hume.ai"
API_BASE = "/v0/evi"


def get_hume_api_key() -> str:
    api_key = os.environ.get("HUME_API_KEY")
    if not api_key:
        raise ValueError("HUME_API_KEY is not set in the environment variables.")
    return api_key


def get_last_10_chats() -> dict:
    api_key = get_hume_api_key()

    conn = http.client.HTTPSConnection(API_HOST)
    conn.request(
        "GET",
        f"{API_BASE}/chats?page_number=0&page_size=10&ascending_order=false",
        headers={
            "X-Hume-Api-Key": api_key,
            "Accept": "application/json",
        },
    )

    response = conn.getresponse()
    body = response.read().decode("utf-8")
    conn.close()

    if response.status != 200:
        raise RuntimeError(f"API error {response.status}: {body}")

    return json.loads(body)


def main():
    data = get_last_10_chats()
    chats = data.get("chats", [])

    print(f"\n🧪 Last {len(chats)} chats:\n")

    for i, chat in enumerate(chats, start=1):
        created = chat.get("created") or chat.get("created_at")
        chat_id = chat.get("chat_id") or chat.get("id")

        print(f"{i}. chat_id: {chat_id}")
        print(f"   raw created field: {created}")

        # Try converting if epoch
        if isinstance(created, int):
            dt = datetime.fromtimestamp(created, tz=timezone.utc)
            print(f"   created (UTC): {dt.isoformat()}")

        print("-" * 50)


if __name__ == "__main__":
    main()
