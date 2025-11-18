import os
from flask import Flask, request, Response
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
AGENT_ID = os.getenv("AGENT_ID")

SYSTEM_PROMPT = """
You are a dual-language dictionary agent.
Return meanings ONLY in structured JSON.
"""

@app.route("/")
def home():
    return "DualLex Agent Backend is Running."

@app.route("/lookup", methods=["POST"])
def lookup():
    data = request.get_json()
    word = data.get("word", "").strip()

    if not word:
        return {"error": "No word provided"}, 400

    def stream():
        yield "event: status\ndata: Agent starting...\n\n"

        run = client.agents.runs.create(
            agent_id=AGENT_ID,
            input=f"Define the word: {word}"
        )

        step_stream = client.agents.runs.create_steps_stream(
            agent_id=AGENT_ID,
            run_id=run.id
        )

        final_json = None

        for event in step_stream:
            ### Status updates
            if hasattr(event, "event_type"):
                yield f"event: status\ndata: {event.event_type}\n\n"

            if hasattr(event, "output_text") and event.output_text:
                yield f"event: status\ndata: {event.output_text}\n\n"

            ### Final JSON from agent
            if hasattr(event, "output") and event.output:
                final_json = event.output

        if final_json:
            yield f"event: final\ndata: {final_json}\n\n"

        yield "event: done\ndata: complete\n\n"

    return Response(stream(), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
