import json
from pathlib import Path

from flask import Flask, render_template, request

from gemini_client import match_friends

app = Flask(__name__)
PEOPLE_PATH = Path(__file__).with_name("people.json")


def load_people() -> list[dict]:
    return json.loads(PEOPLE_PATH.read_text(encoding="utf-8"))


@app.get("/")
def home():
    return render_template("index.html", result=None, error=None, form={})


@app.post("/match")
def match():
    form = {
        "name": request.form.get("name", "").strip(),
        "city": request.form.get("city", "").strip(),
        "interests": request.form.get("interests", "").strip(),
        "bio": request.form.get("bio", "").strip(),
    }
    if not form["name"] or not form["interests"]:
        return render_template(
            "index.html",
            result=None,
            error="Name and interests are required.",
            form=form,
        )

    profile = {
        "name": form["name"],
        "city": form["city"] or "unspecified",
        "bio": form["bio"] or "Looking for friends with overlapping hobbies.",
        "interests": [item.strip() for item in form["interests"].split(",") if item.strip()],
    }

    try:
        result = match_friends(profile, load_people())
        people_by_id = {person["id"]: person for person in load_people()}
        for match_item in result.get("matches", []):
            match_item["person"] = people_by_id.get(match_item.get("id"))
    except Exception as exc:
        message = str(exc)
        if "API_KEY_INVALID" in message or "API key not valid" in message:
            message = "Your Gemini API key is invalid. Paste the MLH key into the .env file and restart the app."
        return render_template("index.html", result=None, error=message, form=form)

    return render_template("index.html", result=result, error=None, form=form)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
