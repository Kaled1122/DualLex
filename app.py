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

@app.route("/")
def home():
    return "DualLex Agent Running on Vercel (Docker Mode)."

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

        steps = client.agents.runs.create_steps_stream(
            agent_id=AGENT_ID,
            run_id=run.id
        )

        final_json = None

        for ev in steps:
            if hasattr(ev, "event_type"):
                yield f"event: status\ndata: {ev.event_type}\n\n"

            if hasattr(ev, "output_text") and ev.output_text:
                yield f"event: status\ndata: {ev.output_text}\n\n"

            if hasattr(ev, "output") and ev.output:
                final_json = ev.output

        if final_json:
            yield f"event: final\ndata: {final_json}\n\n"

        yield "event: done\ndata: complete\n\n"

    return Response(stream(), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
