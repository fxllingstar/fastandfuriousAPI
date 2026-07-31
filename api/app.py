"""
Fast & Furious Quotes API
A tiny personal Flask API that serves quotes from quotes.json.

Endpoints:
  GET /quotes                  -> all quotes
  GET /quotes/random           -> one random quote
  GET /quotes/<id>             -> a specific quote by id
  GET /quotes?character=Dom    -> filter by character (partial match, case-insensitive)
  GET /characters              -> list of distinct character names
"""

import json
import random
from pathlib import Path
from flask import Flask, jsonify, request, abort

app = Flask(__name__)

DATA_FILE = Path(__file__).parent / "quotes.json"


def load_quotes():
    """Load quotes fresh from disk on every request.

    For a dataset this small (a few hundred quotes at most), reading the
    file each time is simpler and safer than caching in memory — you can
    edit quotes.json directly while the server is running and see changes
    immediately, without needing a restart or a cache-invalidation step.
    """
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


@app.route("/quotes", methods=["GET"])
def get_quotes():
    quotes = load_quotes()

    character_filter = request.args.get("character")

    if character_filter:
        quotes = [q for q in quotes if character_filter.lower() in q["character"].lower()]

    return jsonify(quotes)


@app.route("/quotes/random", methods=["GET"])
def get_random_quote():
    quotes = load_quotes()
    if not quotes:
        abort(404, description="No quotes in the database yet.")
    return jsonify(random.choice(quotes))


@app.route("/quotes/<int:quote_id>", methods=["GET"])
def get_quote_by_id(quote_id):
    quotes = load_quotes()
    match = next((q for q in quotes if q["id"] == quote_id), None)
    if match is None:
        abort(404, description=f"No quote found with id {quote_id}.")
    return jsonify(match)


@app.route("/characters", methods=["GET"])
def get_characters():
    quotes = load_quotes()
    characters = sorted(set(q["character"] for q in quotes))
    return jsonify(characters)


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": str(e.description)}), 404


if __name__ == "__main__":
    # host="0.0.0.0" makes it reachable from other apps/devices on your
    # network, not just from within Termux itself. Change to "127.0.0.1"
    # if you only ever want to hit it from something running on-device.
    app.run(host="0.0.0.0", port=5000, debug=False)