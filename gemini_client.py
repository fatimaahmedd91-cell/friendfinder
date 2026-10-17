import json
import os

from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv(Path(__file__).with_name(".env"), override=True)

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")


def get_client() -> genai.Client:
    api_key = (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "").strip()
    if not api_key or api_key.startswith("your-gemini-api-key"):
        raise RuntimeError(
            "Missing GEMINI_API_KEY. Open the .env file and paste your MLH Gemini key from Google AI Studio."
        )
    return genai.Client(api_key=api_key)


def match_friends(profile: dict, candidates: list[dict]) -> dict:
    client = get_client()
    prompt = f"""
You are FriendFinder, a warm, practical friend-matching assistant.

User profile:
{json.dumps(profile, indent=2)}

Candidate people:
{json.dumps(candidates, indent=2)}

Pick the 3 best potential friends for this user. Rank them. Be specific about shared
interests and one honest difference that could still make the friendship interesting.

Return JSON only, matching this schema:
{{
  "summary": "1-2 sentence overview of who this person would click with",
  "matches": [
    {{
      "id": "candidate id",
      "name": "candidate name",
      "score": 0-100,
      "why": "2-3 sentences",
      "icebreakers": ["question 1", "question 2"]
    }}
  ]
}}
"""
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )
    return json.loads(response.text)
