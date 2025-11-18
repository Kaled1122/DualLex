from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

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
"""

@app.route("/")
def home():
    return "DualLex backend is running."

@app.route("/lookup", methods=["POST"])
def lookup():
    data = request.get_json()
    word = data.get("word", "").strip()

    if not word:
        return jsonify({"error": "No word provided."})

    response = client.responses.create(
        model="gpt-4.1",
        input=f"Define the word: {word}",
        instructions=system=SYSTEM_PROMPT,
        tools=[],
        response_format={"type": "json_schema", "json_schema": JSON_SCHEMA}
    )

    # Extract JSON (correct for new Responses API)
    result_json = response.output[0].content[0].json

    return jsonify(result_json)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
