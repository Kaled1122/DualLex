from flask import Flask, request, Response
from flask_cors import CORS
from openai import OpenAI
import os
import json

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

AGENT_SYSTEM = """
You are DualLex, a bilingual English–Arabic dictionary agent.

Capabilities:
- Use the web browser tool to search authoritative dictionary sources.
- Analyze usage in classical, formal, informal, and colloquial Arabic.
- Build a JSON dictionary entry.
- Show your reasoning steps as you work (the client will stream them).

Your final output MUST be JSON:
{
  "classical": "",
  "formal": "",
  "informal": "",
  "colloquial": "",
  "examples": {
    "english": [],
    "arabic": []
  }
}
"""

@app.route("/")
def home():
    return "DualLex Agent running on Render."

@app.route("/lookup", methods=["POST"])
def lookup():
    data = request.get_json()
    word = data.get("word", "")

    def stream():
        stream = client.agents.runs.create_steps_stream(
            model="gpt-4.1",
            instructions=AGENT_SYSTEM,
            input=f"Lookup the word: {word}. Produce JSON output.",
            tools=[{"type": "web_browser"}]  # REAL BROWSER TOOL
        )

        for event in stream:
            # Send intermediate steps to frontend
            yield f"data: {json.dumps(event.to_dict())}\n\n"

    return Response(stream(), mimetype="text/event-stream")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
