from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
import os
import json

app = Flask(__name__)
CORS(app)

api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY is not set.")

client = genai.Client(api_key=api_key)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "running"
    })


@app.route("/solve", methods=["POST"])
def solve():
    data = request.get_json()

    question = data.get("question", "").strip()

    if not question:
        return jsonify({
            "error": "No question provided"
        }), 400

    prompt = f"""
You are an AI study helper.

Solve the following question.

Question:
{question}

Return ONLY valid JSON:

{{
    "answer": "the correct answer",
    "explanation": "short explanation"
}}
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        text = response.text.strip()

        # Remove markdown JSON formatting if Gemini adds it
        if text.startswith("```"):
            text = text.replace("```json", "")
            text = text.replace("```", "")
            text = text.strip()

        result = json.loads(text)

        return jsonify({
            "answer": result.get("answer", ""),
            "explanation": result.get("explanation", "")
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )