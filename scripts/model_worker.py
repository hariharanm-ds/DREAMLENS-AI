from flask import Flask, request, jsonify

from groq_client import check_groq_health, interpret_dream

app = Flask(__name__)


@app.route("/status")
def status():
    return jsonify(check_groq_health())


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json() or {}
    dream = (data.get("dream") or "").strip()
    db_context = (data.get("db_context") or "").strip()
    if not dream:
        return jsonify({"success": False, "error": "no dream provided"}), 400

    result = interpret_dream(dream, db_context=db_context)
    status_code = 200 if result["success"] else 502
    return jsonify(result), status_code


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5010)
