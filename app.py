from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "classical": {"type": "string"},
        "formal": {"type": "string"},
        "informal": {"type": "string"},
        "colloquial": {"type": "string"},
        "examples": {
            "type": "object",
            "properties": {
                "english": {"type": "array", "items": {"type": "string"}},
                "arabic": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["english", "arabic"]
        }
    },
    "required": ["classical", "formal", "informal", "colloquial", "examples"]
}

SYSTEM_PROMPT = """
You are a Dual-Language Dictionary Agent.

Return meanings ONLY as structured JSON.
No sentences outside JSON.
No commentary.
No free text.

Definition rules:
- Search classical, formal, informal, and colloquial meanings
- Use browser search for validation
- Provide concise definitions in Arabic and English
- Provide two example lists: English examples and Arabic examples
"""

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/lookup", methods=["POST"])
def lookup():
    data = request.get_json()
    word = data.get("word", "").strip()

    if not word:
        return jsonify({"error": "No word provided."})

    # Call Agent
    response = client.responses.create(
        model="gpt-4.1",
        input=f"Define the word: {word}",
        system=SYSTEM_PROMPT,
        tools=[{"type": "web_browser"}],
        response_format={"type": "json_schema", "json_schema": JSON_SCHEMA}
    )

    # Agent produces valid JSON automatically
    return jsonify(response.output_json)


if __name__ == "__main__":
    app.run(debug=True)
