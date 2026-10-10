from flask import Flask, request, jsonify
import subprocess
import sys
import os
import html

import database

app = Flask(__name__)

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

SCRIPTS = {
    "main": "main.py",
    "diagnose": "diagnose.py",
    "evaluate": "evaluate.py",
    "calibrate": "calibrate.py",
    "inspect_cases": "inspect_cases.py"
}

database.initialize_database()


def run_script(module):
    """Run a project module and return its output and status."""

    if module not in SCRIPTS:
        return None, "error", "Unknown module"

    try:
        result = subprocess.run(
            [sys.executable, SCRIPTS[module]],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            timeout=60
        )

        output = result.stdout or ""

        if result.stderr:
            output += "\n\nMessages or errors:\n" + result.stderr

        if not output.strip():
            output = "The script finished without producing output."

        status = "success" if result.returncode == 0 else "error"

        return output, status, None

    except subprocess.TimeoutExpired:
        return "The script exceeded the 60-second time limit.", "error", None

    except Exception as error:
        return str(error), "error", None


def make_page(output="Welcome! Select a button to run your project."):
    safe_output = html.escape(output)

    buttons = ""

    for key, filename in SCRIPTS.items():
        label = filename.replace(".py", "").replace("_", " ").title()

        buttons += f"""
        <form method="post" action="/run/{key}">
            <button type="submit">{label}</button>
        </form>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Fileless Invoice Dashboard</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <style>
            body {{
                margin: 0;
                font-family: Arial, sans-serif;
                background: #eef2f7;
                color: #1e293b;
            }}

            header {{
                background: #101827;
                color: white;
                text-align: center;
                padding: 30px 15px;
            }}

            .container {{
                max-width: 1000px;
                margin: 30px auto;
                padding: 0 20px;
            }}

            .cards {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
            }}

            .card {{
                background: white;
                padding: 20px;
                border-radius: 12px;
                box-shadow: 0 3px 10px #0001;
            }}

            .buttons {{
                display: flex;
                flex-wrap: wrap;
                gap: 12px;
                margin: 20px 0;
            }}

            button {{
                background: #2563eb;
                color: white;
                border: 0;
                border-radius: 7px;
                padding: 13px 18px;
                cursor: pointer;
                font-size: 14px;
            }}

            button:hover {{
                background: #1d4ed8;
            }}

            .output {{
                background: #0b1220;
                color: #a7f3d0;
                padding: 20px;
                border-radius: 10px;
                white-space: pre-wrap;
                overflow-wrap: anywhere;
                overflow-x: auto;
                min-height: 150px;
                line-height: 1.5;
            }}

            .api-links {{
                background: white;
                padding: 18px;
                border-radius: 10px;
                margin-top: 20px;
            }}

            .api-links a {{
                color: #2563eb;
                margin-right: 15px;
            }}

            footer {{
                text-align: center;
                padding: 25px;
                color: #64748b;
            }}
        </style>
    </head>

    <body>
        <header>
            <h1>Fileless Invoice</h1>
            <p>Security Event Analysis and Attack Detection</p>
        </header>

        <div class="container">
            <h2>Project Dashboard</h2>

            <div class="cards">
                <div class="card">
                    <h3>Event Analysis</h3>
                    <p>Investigate security events and attack evidence.</p>
                </div>

                <div class="card">
                    <h3>Diagnostics</h3>
                    <p>Examine detection accuracy and missing evidence.</p>
                </div>

                <div class="card">
                    <h3>Evaluation</h3>
                    <p>Review the model's test results.</p>
                </div>

                <div class="card">
                    <h3>Calibration</h3>
                    <p>Compare probability calibration metrics.</p>
                </div>
            </div>

            <h2>Run Project Modules</h2>

            <div class="buttons">
                {buttons}
            </div>

            <h2>Execution Results</h2>
            <div class="output">{safe_output}</div>

            <div class="api-links">
                <h3>Backend Services</h3>
                <p>
                    <a href="/api/health">Backend Status</a>
                    <a href="/api/history">Analysis History</a>
                </p>
            </div>

            <p>
                Note: Attack probabilities are estimates,
                not proof of an attack.
            </p>
        </div>

        <footer>Fileless Invoice Security Analysis Project</footer>
    </body>
    </html>
    """


@app.route("/")
def home():
    return make_page()


@app.route("/run/<module>", methods=["POST"])
def run_module(module):
    if module not in SCRIPTS:
        return "Unknown module", 404

    output, status, error = run_script(module)

    if error:
        output = error
        status = "error"

    try:
        database.save_result(module, status, output)
    except Exception:
        app.logger.exception("Failed to save analysis result")

    return make_page(output)


# API: Check whether the backend and database are available.
@app.route("/api/health", methods=["GET"])
def health():
    try:
        history_count = len(database.get_history(limit=200))

        return jsonify({
            "status": "ok",
            "application": "Fileless Invoice",
            "database": "connected",
            "recent_history_records": history_count
        }), 200

    except Exception:
        app.logger.exception("Health check failed")

        return jsonify({
            "status": "error",
            "database": "unavailable"
        }), 500


# API: Run a module and return structured JSON.
@app.route("/api/run/<module>", methods=["POST"])
def api_run_module(module):
    if module not in SCRIPTS:
        return jsonify({
            "error": "Unknown module",
            "available_modules": list(SCRIPTS.keys())
        }), 404

    output, status, error = run_script(module)

    if error:
        output = error
        status = "error"

    try:
        result_id = database.save_result(module, status, output)
    except Exception:
        app.logger.exception("Failed to save analysis result")

        return jsonify({
            "module": module,
            "status": status,
            "output": output,
            "database_saved": False
        }), 500

    return jsonify({
        "id": result_id,
        "module": module,
        "status": status,
        "output": output,
        "database_saved": True
    }), 200 if status == "success" else 500


# API: Retrieve recent analysis history.
@app.route("/api/history", methods=["GET"])
def api_history():
    try:
        limit = request.args.get("limit", default=50, type=int)

        if limit is None or limit < 1:
            return jsonify({
                "error": "limit must be a positive integer"
            }), 400

        records = database.get_history(limit=limit)

        return jsonify({
            "count": len(records),
            "history": records
        }), 200

    except Exception:
        app.logger.exception("Could not retrieve history")

        return jsonify({
            "error": "Could not retrieve analysis history"
        }), 500


# API: Retrieve one result by its database ID.
@app.route("/api/history/<int:result_id>", methods=["GET"])
def api_single_result(result_id):
    try:
        result = database.get_result(result_id)

        if result is None:
            return jsonify({
                "error": "Result not found"
            }), 404

        return jsonify(result), 200

    except Exception:
        app.logger.exception("Could not retrieve result")

        return jsonify({
            "error": "Could not retrieve result"
        }), 500


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )