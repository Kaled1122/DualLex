from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
import json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a Dual-Language Dictionary Agent.
Return meanings ONLY as valid JSON.
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
        instructions=SYSTEM_PROMPT,
        input=f"Define the word: {word}",
        tools=[]
    )

    # FIX: output_text() MUST have parentheses
    raw = response.output_text()

    # try converting to JSON
    try:
        result_json = json.loads(raw)
        return jsonify(result_json)
    except Exception as e:
        return jsonify({
            "error": "Model did not return valid JSON",
            "raw_output": raw,
            "exception": str(e)
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
