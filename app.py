from flask import Flask, request, jsonify
import requests
import os
from flask_cors import CORS
from requests.exceptions import Timeout, ConnectionError, HTTPError

app = Flask(__name__)
CORS(app)

TMDB_API_KEY = os.environ.get("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org"


@app.route("/")
def home():
    return jsonify({
        "status": "ok",
        "service": "TMDB Proxy API",
        "message": "Service running successfully 🚀"
    }), 200


@app.route("/api/<path:path>", methods=["GET"])
def proxy(path):
    # ---------- API KEY CHECK ----------
    if not TMDB_API_KEY:
        return jsonify({
            "status": "error",
            "message": "TMDB API key not configured on server"
        }), 500

    # ---------- INPUT VALIDATION ----------
    if not path.startswith("3/"):
        return jsonify({
            "status": "error",
            "message": "Invalid TMDB path. Path must start with /3/"
        }), 400

    try:
        # ---------- BUILD REQUEST ----------
        params = dict(request.args)
        params["api_key"] = TMDB_API_KEY

        url = f"{TMDB_BASE_URL}/{path}"

        # ---------- CALL TMDB ----------
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        return jsonify(response.json()), response.status_code

    # ---------- TIMEOUT ----------
    except Timeout:
        return jsonify({
            "status": "error",
            "message": "TMDB request timed out"
        }), 504

    # ---------- NETWORK ERROR ----------
    except ConnectionError:
        return jsonify({
            "status": "error",
            "message": "Unable to connect to TMDB servers"
        }), 502

    # ---------- TMDB ERROR ----------
    except HTTPError as http_err:
        return jsonify({
            "status": "error",
            "tmdb_status": response.status_code,
            "tmdb_response": response.text
        }), response.status_code

    # ---------- UNKNOWN ERROR ----------
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Internal proxy error",
            "details": str(e)
        }), 500


# ---------- VERCEL HANDLER ----------
def handler(request, *args, **kwargs):
    return app(request, *args, **kwargs)


# ---------- LOCAL SERVER ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
